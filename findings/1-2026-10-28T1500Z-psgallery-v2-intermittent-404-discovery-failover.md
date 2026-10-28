# 404 for a package that exists: PowerShell Gallery's intermittent discovery failures and the failover that fixed them

- Source issue: https://github.com/PowerShell/PowerShellGallery/issues/356 (closed as resolved 2026-10-27 20:21 UTC)
- Project: PowerShell/PowerShellGallery (~289 stars; public issue tracker for the PowerShell Gallery service)
- Checked: 2026-10-28 15:10 UTC

## Problem
On 2026-10-26, repeated identical GET requests to the Gallery v2 discovery endpoint (`FindPackagesById()`) for the existing `powershell-yaml` module intermittently returned HTTP 404 - 3 out of 12 requests, roughly 25% - while 12 interleaved requests to the package-download endpoint all succeeded. The reporter's rigor is worth noting: they explicitly declined to call it a service-wide outage from one machine's view, and admitted they hadn't retained the failed response headers. Corroboration arrived within hours and it was broad: multiple users installing `Microsoft.Graph` and `Az` module families (each with many submodules) saw random per-module failures across local machines and Azure DevOps Microsoft-hosted agents, different modules failing on different runs, sometimes requiring 10+ retries. One user's detail was diagnostic: the same files that 404'd in discovery downloaded fine manually. A PowerShell team member (author_association MEMBER) responded the next afternoon: failover to the last known good deployment. Within about an hour, users confirmed their automations were succeeding again, and the issue was closed.

## Why it is interesting
- A complete, public incident lifecycle in ~21 hours: careful initial report, community corroboration narrowing the fault domain, vendor rollback, confirmed resolution. This is what "file it and it gets fixed" looks like for a service with no public status-page drama attached.
- The failure pattern is a classic distributed-systems tell. Discovery returning random 404s for existing entries while downloads stay healthy points at the index/metadata tier (or a bad deployment skewed across nodes) rather than missing content. Some fraction of requests hit a node whose view of the package catalog was wrong - load balancer roulette. The reporter's own data (identical URL, random outcomes) implies exactly that without needing to name it.
- Multi-module packages are the canary here. `Az` and `Microsoft.Graph` pull dozens of submodules; at a 25% per-request failure rate, the probability of a clean full install collapses, which is why CI pipelines felt it as "nothing works" while single-module users saw a shrug-and-retry.
- Resolution by failover, not fix: the mitigation was rolling back to the last known good deployment. The root cause of the bad deployment was never disclosed in the thread - a candid reminder that "resolved" and "understood" are different endpoints.

## Honest limits
- Root cause is undisclosed; "bad deployment" is inferred from the announced failover, not confirmed.
- Single initial report from one machine; the service-wide nature is established by later corroboration, not by the first post.
- Issue is closed as resolved; status could regress and is unverified beyond 2026-10-28 15:10 UTC.
- No GitHub code change is linked; this is a service-operations incident, not a library bug.
