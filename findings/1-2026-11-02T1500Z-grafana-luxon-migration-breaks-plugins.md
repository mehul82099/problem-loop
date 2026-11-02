# Grafana 13.3's default-on Luxon migration crashes existing plugins that call Moment methods like `isSameOrAfter`

**Source:** [grafana/grafana#136765](https://github.com/grafana/grafana/issues/136765) (open; filed by a Grafana contributor from an internal report, labeled `internal`)

## What happened

Grafana 13.3.0 (verified release, 2026-10-27) enables `datetime.useLuxon` by default, swapping the date-time implementation exposed to plugins from Moment to Luxon - and plugins that call Moment-specific methods on Grafana date-time values crash. The concrete casualty: the pyris panel plugin's time axis, whose `TimeAxis.ts` line 386 calls `nextCursor.isSameOrAfter(nextMajor)` (the line is verbatim in the plugin's public repo, verified); on 13.3.0 with the default flag the panel crashes, and setting `datetime.useLuxon = false` brings it back. The issue is filed by a Grafana contributor (association CONTRIBUTOR, labeled `internal`) tracking an internal bug report, and is honest about its own evidence: the reproduction "summarizes the report", has not been independently reproduced, and names no minimal dashboard. The requested follow-up is the interesting part: restore compatibility in a 13.3.1 and Grafana Cloud, add regression coverage, and account for the breakage before removing the feature-flag escape hatch in PR [#136140](https://github.com/grafana/grafana/pull/136140) ("DateTime: Always use Luxon in the frontend", verified, closed) - i.e. Grafana's own tracker now records that the default-on migration breaks the plugin ecosystem it was supposed to be transparent to, and the flag that currently saves affected users is scheduled for removal.

## Who this bites

- Plugin developers: a Grafana minor upgrade changed the runtime type of a value plugins have handled as Moment for years, so any plugin calling Moment-only methods (`isSameOrAfter` and friends) crashes at panel render with no deprecation window on the default path.
- Self-hosters and Cloud users with third-party panels: the failure looks like a broken plugin, not a Grafana regression, and the only immediate fix is an admin-level feature toggle most users will never find - while the toggle itself is already on the deprecation chopping block.

## Limits

- The originating report is an internal Slack thread the public issue links but outsiders cannot read; the issue itself says the repro is unverified and lacks plugin version details. The plugin code line and the workaround's effect are the independently checkable parts (the line is verified; the toggle behavior is as-reported).
- Single affected plugin named; the size of the affected plugin population is unknown.
- No fix or milestone at publish time; how Grafana restores compatibility (shim methods vs re-defaulting the flag) is open.
