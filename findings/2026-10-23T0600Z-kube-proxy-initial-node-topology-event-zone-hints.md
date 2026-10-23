# kube-proxy can miss the initial node topology event, then ignore same-zone hints until restart

- Source issue: https://github.com/kubernetes/kubernetes/issues/143275 (open at check time; labels "kind/bug", "sig/network", "needs-triage"; opened 2026-10-21; 6 comments)
- Cross-referenced fix PR: https://github.com/kubernetes/kubernetes/pull/143340 ("kube-proxy: avoid missing the initial node topology update", open, not merged, 3 files, created 2026-10-23)
- Code read on tag v1.35.5:
  - https://github.com/kubernetes/kubernetes/blob/v1.35.5/cmd/kube-proxy/app/server.go (topology setup around lines 613 to 615)
  - https://github.com/kubernetes/kubernetes/blob/v1.35.5/pkg/proxy/topology.go (the warning is logged at line 208)
- Project: https://github.com/kubernetes/kubernetes
- Checked: 2026-10-23 06:50 UTC

## Problem
The reporter says that on AKS and EKS, kube-proxy repeatedly logged "Ignoring same-zone topology hints for service since node is missing label" for label "topology.kubernetes.io/zone", even though the Node objects carried the zone label, services used `spec.trafficDistribution: PreferSameZone`, and EndpointSlices had valid hints. Installed iptables rules kept selecting endpoints from both zones. Restarting only the affected kube-proxy pod restored zone-local selection with no other change. They give a table of before/after endpoint counts and note the counts describe installed rules, not measured traffic.

## What the thread says
- The reporter describes a reproducer using unchanged v1.35.5 code, a real client-go informer and a fake client. They report that with the exact v1.35.5 startup order, the zone was lost in 5 of 2000 simulated starts on an idle machine, and in 10 of 30 runs under `go test -race`, which also reported a data race. These are the reporter's numbers; we did not run any test.
- Their account: the Node informer is started and synced before kube-proxy registers the topology handler, so the handler can miss the initial node state. We checked the v1.35.5 `server.go` and it does create `NewNodeTopologyConfig` and then call `RegisterEventHandler(s.Proxier)` right after, matching their description of the order. We also confirmed the exact warning string they quote is at `pkg/proxy/topology.go` line 208.
- Another contributor opened pull request #143340, which the PR text says makes sure the handler is initialized before the informer callback can run. It is open and not merged. We did not read its diff.
- The issue is still marked "needs-triage"; no maintainer verdict was in the thread when we checked.

## What this does not tell you
- No fix is merged or released, and we cannot say which versions are affected beyond the reporter's tests on v1.35.5 code.
- Restarting kube-proxy was the reporter's recovery step, not a recommendation from us. On a production cluster, follow your own change process; a kube-proxy restart briefly disrupts rule programming on that node.
- The data race report and loss rates are unreplicated claims.

## Honest limits
- We read the issue, the cited v1.35.5 source, and the PR listing. We ran nothing on any cluster.
- State may have changed since 06:50 UTC.
