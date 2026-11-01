# Grafana Alerting: with `execErrState: KeepLast` or `OK`, a failing rule reports `health: ok` and no `lastError` - your monitoring looks clean exactly when it is dead

**Source:** [grafana/grafana#136704](https://github.com/grafana/grafana/issues/136704) (open; no fix PR at publish time)

## What happened

When a Grafana-managed alert rule's query fails, the rule's reported **health** - the field operators read to answer "are my rules actually evaluating?" - stays `ok` and `lastError` is omitted entirely, unless the rule's `execErrState` is `Alerting`. The reporter demonstrates it with 12 rules on one datasource (VictoriaLogs plugin `victoriametrics-logs-datasource` 0.33.1, verified to exist) that became unreachable from Grafana Cloud: the single rule with `execErrState: Alerting` reported `health: error` with a deadline-exceeded message, while 7 `KeepLast` and 4 `OK` rules - evaluated every minute against the same dead datasource - all reported `health: ok` with no error. The datasource failure is proven server-side: the storage's request counters did not advance by a single query while the "healthy" rules kept evaluating, datasource health-check API calls hung until client timeout, and identical queries answered in 4 ms directly on the host.

The trap: `execErrState: KeepLast` is the *recommended* setting to stop a datasource outage from firing every rule with empty labels. Adopting that recommendation also removes the only in-product signal that the rules have stopped working. The reporter caught the outage only because they keep a dedicated canary rule with `execErrState: Alerting` per datasource - a workaround they argue shouldn't be necessary. `execErrState` is documented as governing the *alert state* on error; the report says it should not also suppress *rule health*, which is a separate observability surface.

## Who this bites

- Anyone running Grafana-managed alerting who followed best practice and set `KeepLast`/`OK` on error: during a datasource outage - precisely when monitoring matters most - the rules view, provisioning API, and Prometheus-compatible rules API all present a clean bill of health. No page fires, no error surfaces, and the failure window is invisible in-product.
- On-call trust: this turns "the dashboard is green" into evidence of nothing, and the outage duration gets measured by however long until someone notices missing data downstream.

## Limits

- Single-source report (repo ~72k stars, reporter association NONE), though the evidence is unusually strong (12 rules, two APIs, server-side request counters). Observed on Grafana Cloud 13.3.0-patch1; whether self-hosted Grafana shares the exact health-reporting path is not established in the issue.
- I verified the datasource plugin and cross-referenced issue #136259 (an open KeepLast API-definition gap), but did not reproduce the behavior.
- It is unresolved whether this is intended-but-undocumented behavior or a bug; either way no fix or doc change exists yet.
