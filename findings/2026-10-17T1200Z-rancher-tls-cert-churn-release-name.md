# Rancher HA: TLS cert churn when the Helm release is not named "rancher"

- Source: https://github.com/rancher/rancher/issues/57719 (open, label `kind/bug`, opened 2026-10-04 by sehorne, 5 comments, last activity 2026-10-17)
- Proposed fix, state checked through the GitHub API on 2026-10-17: https://github.com/rancher/rancher/pull/57720 "fix(tls): resolve pod selector from app selector env" (open, by sehorne, 2 files changed, opened 2026-10-04)
- Code read on main on 2026-10-17: https://github.com/rancher/rancher/blob/main/pkg/tls/podips.go (line 114) and https://github.com/rancher/rancher/blob/main/chart/templates/_helpers.tpl (lines 102 to 104)

## The problem, as reported
In a multi-replica (HA) Rancher install where the Helm release name is not exactly `rancher`, the reporter says the internal (:444) and serving (:443) TLS certificate secrets keep being rewritten. For the serving listener, which closes connections on certificate change, he says this drops connections on every rotation.

His explanation: the pod-IP filter looks up Rancher pods with a hardcoded selector `app=rancher`. The chart labels pods with the Helm fullname, so a release called `rancher-install` gives pods labelled `app=rancher-install`. Each replica then finds no pods, builds an empty IP set, and the replicas overwrite the shared certificate secret with different views of the valid IPs.

## What I checked in the code
- `pkg/tls/podips.go` on main, line 114: `newPodIPTracker(ctx, namespace.System, "app=rancher", pods, handlerName)`. The hardcoded selector is there.
- `chart/templates/_helpers.tpl`: `rancher.selectorLabels` is `app: {{ include "rancher.fullname" . }}`, so the label value follows the release name logic and is not the literal "rancher".
- Both match the reporter's description. I did not run Rancher, so the churn itself and its effect on connections are not independently verified.

## History the reporter cites
He says the same assumption was fixed before in issues 50370 and 50371 ("Rancher features assume app: rancher label, causing issues with custom release names", both closed, the second a backport to v2.11), and that PR 56477 "reintroduced" it. I confirmed 50370, 50371 and 56477 exist and that 56477 (merged 2026-08-11, "prune stale pod IPs from the :443 serving cert too") touched `podips.go`. But the file's history also has two earlier commits (2026-07-10 and 2026-08-04), so I cannot say from this which change first introduced the hardcoded string.

## Proposed fix
The PR resolves the selector from the chart-provided environment variable `IMPERATIVE_API_APP_SELECTOR`, falling back to `app=rancher` only when the variable is unset. The issue text explains why two other candidate sources were rejected (the peer service setting and the extension API server selector). I did not read the PR diff or its tests. The reporter also asks for a backport to `release/v2.15`, where the same code lives in `pkg/tls/cnfilter.go`, and mentions a 2.15-only admin allowlist setting as a possible workaround.

## Status
Two other users (dmitrijrub, bcrubgdg) say they see the same thing. On 2026-10-17 the reporter asked a Rancher team member to look at the PR. I saw no maintainer comment on the issue or review status on the PR.

## Practical note (inferred from the report, not tested here)
Installs where the release name is exactly `rancher` should not be affected by this mechanism, since the fullname and the hardcoded value coincide. That is my inference from the code and the reporter's explanation.

## Honest limits
- I did not run Rancher or watch any secret. The behaviour and logs come from the reporter, and two other users confirm symptoms in short comments.
- I did not verify which Rancher releases contain the code, except that the reporter says main and release/v2.15.
- Whether the fix is correct is not established. It is an open PR from the reporter.
