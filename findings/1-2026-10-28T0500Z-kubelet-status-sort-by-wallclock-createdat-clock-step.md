# Sorting by wall-clock is a bet that time never runs backward - the kubelet loses it

- Source issue: https://github.com/kubernetes/kubernetes/issues/143482 (open; opened 2026-10-28)
- Verified: companion fix PR kubernetes/kubernetes#143483 (open, with regression test)
- Project: kubernetes/kubernetes (~129k stars)
- Checked: 2026-10-28 05:15 UTC

## Problem
After a backward clock step on a node, the kubelet's API conversion (`convertToAPIContainerStatuses`) can report a terminated container instance as the pod's current state instead of the actually running one. The culprit is a re-sort by `CreatedAt`: wall-clock creation time. If the clock jumps backward, a newer container can carry an EARLIER timestamp than an older one, so sorting by time inverts reality - the reporter's unit-test table shows the API selecting the dead instance (restart count 1) over the running one (restart count 3). The fix (PR #143483, same reporter) sorts by restart count - a monotonic counter that doesn't care what the clock did - and uses creation time only to break ties. This is the third layer of a known clock-rollback family: the umbrella issue #138174, the sandbox fix #130551, and the runtime follow-up #138191 all left this API-conversion sort untouched.

## Why it is interesting
- The sorting-key choice is a hidden dependency on physics. `CreatedAt` looks like the natural "newest first" key - it is even called creation time. But it is wall-clock data, and wall clocks step: NTP corrections, VM suspend/resume, manual adjustments, leap smears. A restart count is boring and monotonic and therefore correct. The bug is a one-line sort key that quietly assumed time only moves forward.
- Kubernetes already knew this lesson - that's the sting. Two prior fixes in the same family (sandbox, runtime) addressed clock-rollback ordering elsewhere in the kubelet, and this third instance survived both. Layered systems re-learn the same assumption one layer at a time; each fix scoped itself to its own layer and the API conversion kept betting on the clock.
- Consequence-wise it is a lying status, the worst kind of operational bug: kubectl says the pod is running an old terminated instance while the container is actually fine (or vice versa). Everything downstream that watches API state - dashboards, alerting, controllers - acts on the inverted reality.
- The fix arrives with its own proof: a regression test (`TestConvertToAPIContainerStatusesAfterClockRollback`) that fails before and passes after, covering regular and init containers across all input permutations. Issue and PR filed together, test-first.

## Honest limits
- Unit-test-level demonstration; no production incident described in the thread, so real-world frequency after clock steps is unestablished.
- Fix PR #143483 is open and unmerged at check time; no maintainer review yet (bot triage labels only).
- The claim that prior fixes left this sort untouched is the reporter's reading of the linked code; matches the cited line range, not independently re-derived.
- Issue state may have changed since 05:15 UTC.
