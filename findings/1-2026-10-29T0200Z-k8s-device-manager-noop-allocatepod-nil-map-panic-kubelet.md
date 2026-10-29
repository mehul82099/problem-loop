# A no-op stub, a data race, and a panicking kubelet: how a feature gate makes device allocation crash whole nodes

- Source issue: https://github.com/kubernetes/kubernetes/issues/143490 (open; triage/accepted, priority/important-soon; opened 2026-10-28)
- Fix PR: https://github.com/kubernetes/kubernetes/pull/143494 (open; reporter verified master panics 3/3, PR passes 3/3 with -race)
- Project: kubernetes/kubernetes (~129k stars)
- Checked: 2026-10-29 02:50 UTC

## Problem
With the `PodLevelResourceManagers` feature gate on and `topologyManagerScope: pod`, pods that set `spec.resources` and request devices (GPUs, etc.) are admitted without any devices being allocated: the admission path calls each hint provider's `AllocatePod`, and the device manager's `AllocatePod` is a no-op stub ("Device Manager does not support pod level resource allocation") - while CPU and memory managers handle it properly. The devices then get allocated lazily at container start, from pod-worker goroutines that run in parallel, and those concurrent `Allocate` calls mutate the shared `devicesToReuse` map without synchronization. Result: `panic: assignment to entry in nil map` in the device manager, the kubelet crashes and restarts, and then every running pod on the node is rejected at re-admission. One feature gate, a no-op stub, a missing lock - and a node-wide outage. A community member independently traced the exact race interleaving; the reporter verified the open fix PR against the repro with the race detector on.

## Why it is interesting
- The bug is three bugs deep, and each layer is load-bearing: the stub that returns success without doing the work (the lie that starts it), the unsynchronized lazy path the lie forces every pod onto, and the crash-loop re-admission failure that turns one panic into a node-wide eviction. Fixing only the race (tracked separately as #136021) leaves the admission gap; fixing only the gap leaves the race reachable. The reporter and the community explicitly mapped which fix covers which layer - rare clarity for a concurrency bug.
- "Return success as a no-op" is one of the most dangerous patterns in extensible systems. A stub that does nothing and says nothing converts an unimplemented feature into silent wrong behavior downstream; had `AllocatePod` returned an error, the gate combination would have failed loudly at the first pod instead of panicking in production.
- Feature-gate combinatorics strike again: the codepaths are each fine alone, and the explosion only exists at the intersection (pod-level resources x pod-scope topology x device plugins x concurrent container starts). Gate matrices don't get integration-tested at every intersection; users find the missing cells.
- The verification culture on display is the model: reproducer included, independent race-trace by a second person, fix PR checked out and run 3/3 with `-race` by the original reporter. This is what "triage/accepted" should feel earned by.

## Honest limits
- Fix PR #143494 is open, not merged, at check time; review may change the approach.
- The panic requires the specific gate/scope combination plus device-plugin pods; default clusters are unaffected.
- The reporter and tracer are external accounts (association NONE); maintainer triage is in but no maintainer root-cause confirmation yet.
- The re-admission rejection layer is separately reported fixed (#141041); this finding relies on the issue's account of the chain.
