# Istio ambient: short 503 bursts during pod rollouts, and what actually helps

- Source: https://github.com/istio/istio/issues/58514 "503 Spikes During Pod Rollout - Pod Terminates Before Ztunnel Removes Workload" (open, labels `area/networking`, `area/ambient`, `lifecycle/stale`; opened 2025-12-06; 48 comments; stale bot notice on 2026-10-08 says it closes on 2026-10-22 unless a team member acts)
- Checked through the GitHub API on 2026-10-17:
  - https://github.com/istio/istio/pull/58389 "Add configurable idle timeout for HBONE connections": merged to master 2026-01-12
  - https://github.com/istio/istio/pull/58972 manual cherry-pick of it to release-1.29: merged 2026-01-30
  - https://github.com/istio/api/pull/3611 "add hbone_idle_timeout field to MeshConfig API": merged
  - https://github.com/istio/ztunnel/issues/1662 "503 upstream_reset_before_response_started{connection_termination} errors": closed

## The problem
Reporter savealive (EKS, Istio 1.28.1, ambient mode with ztunnel) says that during `kubectl rollout restart`, traffic through an Istio Gateway gets 200 to 500 ms bursts of 503, around 30 to 50 failures at 50 requests per second. With ambient turned off for the namespace there were none. His reading: the container exits before ztunnel hears the workload delete, so traffic still goes to a dead pod. Many commenters on EKS and GKE, and with sidecar-to-ambient mixes, report the same.

## What maintainers said (attributed, not tested here)
- ilrudie (in the thread as an Istio contributor; role not verified here): by the time traffic reaches ztunnel's inbound, the destination was already chosen by the client-side proxy. He later summarised it as the client side picking a terminating workload, "a race against xDS convergence".
- keithmattix, 2026-01-21: the HBONE idle timeout is a mitigation, not a fix. There is always a gap where data can go to a stale endpoint. He floated adding termination state to the workload discovery stream.
- keithmattix, 2026-02-20: at least two issues are mixed up here. (1) Extra 503s compared with sidecars that retries can hide, since ztunnel is not an L7 proxy and cannot retry on an HTTP 503. (2) 503s between ztunnels and waypoints from stale HBONE tunnels, which the idle timeout should mitigate.
- ilrudie, 2026-07-01: suggested `PILOT_DEBOUNCE_MAX=5s` and `PILOT_ENABLE_EDS_DEBOUNCE=false` to speed up convergence. A commenter, dcoppa, says the second also affects ambient workload updates.

## Reported mitigations and their measured results (commenters' own tests)
| Setting | Reported by | Result |
|---|---|---|
| `meshConfig.hboneIdleTimeout` lowered, tested on v1.29 alpha, 15 pods, 5 rollouts at 2 rps | savealive | errors: 3600s (disabled) 54, 60s 22, 30s 12, 15s 4, 10s 2 |
| Retry policy at the ingress (VirtualService, `retryOn: "503,connect-failure,reset"`) | barth12 | 0 x 503 vs 4 to 15 without, on 1.28.2 |
| `hboneIdleTimeout: 5s`, `preStop` sleep of 10s, `PILOT_ENABLE_EDS_DEBOUNCE=false`, Istio 1.30.2, EKS 1.35 | wosiu | no 503 in 230,290 requests over 75 minutes, 6 timeouts at a 2s client timeout |
| EnvoyFilter retrying on reset for HTTP routes | renaudhager | worked for them. wosiu warns blind retries on 503 can duplicate non-idempotent requests |

Worth noting: renaudhager said a preStop sleep alone was not enough for them.

## A release detail
sahanocto noticed the idle-timeout change was in 1.29 alpha but missing from the beta and rc. A release manager (fjglira) confirmed a missed cherry-pick during a two-day branch cut and opened the cherry-pick PR above, which was merged.

## Honest limits
- I ran no Istio. Every error count and configuration result above is a commenter's report, from different clusters and versions.
- The wosiu result combines three changes, so it does not show which one mattered.
- I did not confirm which patch or minor release first ships the idle-timeout setting beyond what the merged PR titles say.
- The thread says there is a mitigation but no root-cause fix, and an Istio team member had not commented since 2026-07-09 per the stale bot.
