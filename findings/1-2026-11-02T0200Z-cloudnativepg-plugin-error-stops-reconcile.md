# CloudNativePG's cluster controller stops reconciling a Cluster after a plugin connection error - no requeue, stuck until an unrelated edit

**Source:** [cloudnative-pg/cloudnative-pg#11816](https://github.com/cloudnative-pg/cloudnative-pg/issues/11816) (open; one automated comment, no maintainer reply at publish time)

## What happened

A user deploying the barman-cloud plugin (operator 1.30.1, plugin-barman-cloud v0.15.1, both current releases) onto a running one-instance Cluster hit a startup race: the operator reached the plugin before its Service/endpoints and the `ObjectStore` CRD were ready, logged `Error loading plugins, retrying` with `rpc error: code = Unavailable` - and then never retried. The Cluster sat in phase `Cluster cannot proceed to reconciliation due to an error while interacting with plugins` for five-plus minutes while the plugin itself became healthy within seconds (already listed in `status.pluginStatus`, certificates Ready). Nothing resumed reconciliation until the user added an arbitrary annotation to the Cluster; that unrelated change triggered a reconcile that went straight to a clean restart and healthy WAL archiving. The reporter's log timeline (02:17:32 first error, silence until 02:22:50, one annotation fixes everything) makes the missing requeue hard to argue with, and the repro is a standard GitOps ordering: apply plugin chart, CRD, `ObjectStore`, `spec.plugins` and a `ScheduledBackup` in one sync. A secondary casualty: the `immediate: true` `Backup` created in the same window failed permanently and is not retried, so a fresh deploy ends with `LastBackupSucceeded=False` until the next schedule. An automated triage comment (AI tooling, not a maintainer) points at merged PR [#11683](https://github.com/cloudnative-pg/cloudnative-pg/pull/11683) fixing related [#11618](https://github.com/cloudnative-pg/cloudnative-pg/issues/11618) - a plugin hook asking for a requeue without a delay was translated into an empty result, stopping reconciliation; the fix supplies a one-second minimum - but that PR merged 2026-10-17 against main and 1.30.1 shipped 2026-09-23, so the released operator plausibly still carries the bug. All references verified.

## Who this bites

- Anyone enabling a CNPG-I plugin on an existing Cluster via GitOps (Argo CD in the report): the apply ordering that naturally races plugin readiness is exactly what a one-shot Application sync produces, and the failure is silent - no events, no further logs, just a phase string - until someone pokes the Cluster for an unrelated reason.
- Operators reading "retrying" at face value: the log promises a retry that never comes, which sends diagnosis toward the plugin even after the plugin is demonstrably healthy.

## Limits

- Single-source report (repo ~20k stars, reporter association NONE, +1 reaction) with quoted operator and plugin logs and a clear reproduction; I did not run it.
- The link to PR #11683 comes from an AI triage bot, not a maintainer; whether that merged fix covers this exact path (and which release will carry it) is unconfirmed at publish time.
- The permanent `Backup` failure may be by design, as the reporter concedes; no maintainer comment yet on either point.
