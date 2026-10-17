# Grafana: a failed bundled-plugin auto-update leaves the plugin unregistered

- Source: https://github.com/grafana/grafana/issues/132528 (open, labels `type/bug`, `area/plugins`, 28 reactions, opened 2026-09-14, last comment 2026-10-17)
- Possibly related fix, found by search and read through the API on 2026-10-17: https://github.com/grafana/grafana/pull/134367 "Plugins: Keep the previous version loaded until a plugin update succeeds" (open, not merged, by andresmgot, opened 2026-10-07, updated 2026-10-16). The issue thread does not link it, and I did not read its diff, so I cannot say it fixes this issue.
- Earlier report of the same mechanism with a network trigger: https://github.com/grafana/grafana/issues/123110 (closed), cited by the reporter.

## The problem
Reporter mtslzr says that on every boot Grafana's background installer compares each bundled datasource plugin with the grafana.com catalog and tries to update any that are older. It stops the running plugin first, then fails to write, and never reloads the old one. His log shows loki 13.1.0 to 13.2.0: the plugin process exits, then `unlinkat .../plugins-bundled/loki: read-only file system`. After that, queries fail with `[plugin.notRegistered] plugin not registered`, and the datasource page says "Data source not found". Seven bundled plugins were hit in one boot, he says: loki, elasticsearch, jaeger, mysql, grafana-postgresql-datasource, mssql, influxdb.

His setup: Grafana 13.2.1 on Kubernetes (AKS) deployed by grafana-operator with a read-only root filesystem, defaults for `preinstall_auto_update` (true) and `update_strategy` (minor). He gives a Docker reproduction with `--read-only`, and says setting `preinstall_auto_update = false` stops the update from being attempted and the plugin stays registered.

The set of casualties grows between image releases, because it depends on how far the catalog has moved past the plugin versions bundled in the image.

## What the Grafana side said (attributed)
- tolzhabayev, 2026-09-23: the cause is right. The update path removes the running plugin before it knows the new version can be installed, so any failure leaves it unregistered. The bundled directory does not need to be writable, since updates are extracted into the plugins directory, which loads first and wins on duplicate IDs. The fix should be in the installer: download and extract first, unload the old one only after that, keep the old one loaded on failure.
- andresmgot, 2026-10-05: the flow is not trivial to change and also touches RBAC roles. He said he would take a look and attach PRs. All plugins should follow the same approach.

## A second trigger, reported today
RaziyeAkr (Grafana 13.2.4, Docker, restricted internet) says the bundled Prometheus plugin was registered, then updated from 13.2.2 to 13.2.3, the download failed with HTTP 403 (service not available in the region), and then Grafana could not find the Prometheus plugin definition. The log lines are quoted in the thread. This matches the "any failure" point, so the trigger is not only read-only paths.

## Practical note (from the report, not tested here)
If your instance runs a read-only image or has limited access to grafana.com, the reporter's setting `[plugins] preinstall_auto_update = false` avoids the update attempt. The trade-off is that bundled plugins will not update on their own.

## Honest limits
- I did not run Grafana. Behaviour and logs are as the reporters posted them.
- I confirmed the cross-referenced issue and PR exist with the states above. I did not confirm that PR 134367 addresses this issue.
- The 13.2.1 and 13.2.4 version claims are from reporters. The releases API I checked lists 13.2.4 as the latest 13.2 tag, published 2026-10-13.
- Whether the disable setting has side effects beyond skipping bundled-plugin updates is not stated in the thread.
