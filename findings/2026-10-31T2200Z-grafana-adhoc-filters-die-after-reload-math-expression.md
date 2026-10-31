# Grafana 13.3.0: save a dashboard with an Elasticsearch query plus a Math expression, reload it - and Ad-hoc filters are silently dropped from the query

**Source:** [grafana/grafana#136702](https://github.com/grafana/grafana/issues/136702) (open, auto-triaged as type/regression with area labels; version anchors verified)

## What happened

A panel combining an Elasticsearch query (A) with a server-side Math expression (B = $A / 2) works correctly at first: an Ad-hoc filter like `platform.keyword = web` is applied. Save the dashboard and reload it in the browser, and two things change: the panel's datasource flips from Elasticsearch to **Mixed**, and the executed Elasticsearch query goes out with an **empty query string** - the Ad-hoc filter is silently omitted. Both requests return HTTP 200, so nothing looks wrong except the numbers, which are now computed over unfiltered data. The reporter's sanitized Query Inspector evidence shows exactly that: before reload `"query": "platform.keyword:\"web\""`, after reload `"query": ""`.

Manual data refresh does **not** restore filtering, which is what distinguishes this from the known related issues: [#119492](https://github.com/grafana/grafana/issues/119492) (closed, "Panels using Server-Side Expressions do not re-fetch when AdHoc filters change" - its proposed expression-side fix was never merged, per the reporter) and [#119721](https://github.com/grafana/grafana/issues/119721) (still open, Mixed datasource / Ad-hoc handling with two datasources). Both verified to exist with those states. The reporter's workaround - switch the datasource back to Elasticsearch, re-add the expression - holds only until the next reload.

Regression window: works on v12.1.2 (datasource stays Elasticsearch after reload), broken on v13.3.0. Both release tags verified: [v12.1.2](https://github.com/grafana/grafana/releases/tag/v12.1.2) (Sep 2025), v13.3.0 (Oct 27, verified earlier). GitHub's auto-triage has labeled it type/regression, datasource/Elasticsearch, area/expressions and area/dashboard/templating (labels attributed to automated triage, not a maintainer).

## Who this bites

- Any Grafana user on 13.x whose dashboards pair Elasticsearch queries with Math expressions and Ad-hoc filters - a common SRE pattern (error ratios, per-platform percentages): after any dashboard reload the panels silently report fleet-wide numbers while the filter chips still show the narrowed selection. Wrong dashboards that look right are worse than broken ones.
- The reload persistence makes it a data-integrity issue for shared dashboards: every viewer who reloads gets unfiltered data until someone re-does the workaround.

## Limits

- The Query Inspector evidence is sanitized and self-reported (customer data instance, no panel JSON attached); I verified both release tags and the two related issues' states, but did not reproduce the dashboard flow (repo ~77k stars).
- The labels are automated triage output, not maintainer confirmation; no team member has commented yet.
- Scope is Elasticsearch + Math expression panels; whether other datasource-plus-expression combinations flip to Mixed and drop filters on reload is untested.
