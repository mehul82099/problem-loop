# HAMi: standby scheduler replicas keep pre-refit devices, so a failover loses NUMA refits and can overcommit GPUs

**Source:** [Project-HAMi/HAMi#3366](https://github.com/Project-HAMi/HAMi/issues/3366) - opened 2026-11-04 by saiyam1814 (GitHub association: CONTRIBUTOR).

## What the report says

With `leaderElect: true` and more than one scheduler replica, a NUMA refit only updates the leader's device cache. Standby replicas receive the same pod updates, but for a pod they already track, `onUpdatePod` only swaps the pod object (`podManager.UpdatePod`) - their cached devices stay on the old GPU, and nothing rebuilds the cache when a replica becomes leader. After a failover the new leader counts the refitted pod on its old GPU and treats the new GPU as free, so it can overcommit the new GPU until the pod is deleted or the replica restarts. The reporter's unit-test-shaped repro: refit a pod on scheduler A (GPU-a to GPU-b), feed scheduler B the Filter patch and the refit patch through `onUpdatePod` - B still counts 20000 MiB on GPU-a and nothing on GPU-b; a replica started *after* the refit accounts GPU-b correctly, because `onAddPod` decodes the annotations. Suggested fix (reporter volunteers to implement): when a tracked pod's device annotations change, `onUpdatePod` re-decodes them and replaces devices and quota usage, like the refit path does.

## Verification (checked during this finding)

At the named master commit (`f1148b5b`, 2026-11-04):

- `pkg/scheduler/scheduler.go` `onUpdatePod` (~line 300): for a tracked, non-terminating pod the handler takes `allocLock` and calls `s.podManager.UpdatePod(newPod)` - a straight object swap with no `DecodePodDevices` call. The only device-touching path in the update handler is `releaseCompletedInitContainersLocked`, which runs solely for the init-container-completion transition.
- `onAddPodLocked` in the same file does decode: `device.DecodePodDevices(device.SupportDevices, pod.Annotations)` then `AddPod` + `quotaManager.AddUsage` - the asymmetry the repro depends on (late-starting replicas account correctly, long-running standbys do not).
- `RefitNumaAllocation` exists in `pkg/scheduler/numa_refit_handler.go` (line 88) - the leader-side refit machinery the report describes.

## Limits

- The unit-test repro was not run here; the finding rests on the verified handler asymmetry at the named commit, which matches the reported mechanism exactly.
- The reporter's association is CONTRIBUTOR; the only comment so far is a CodeRabbit automation plan (tooling, not maintainer triage). No maintainer position or merged fix as of writing.
- Trigger requires HA scheduler (`leaderElect: true`, 2+ replicas) plus NUMA refit in use - single-replica deployments are unaffected.
- Whether `podManager.UpdatePod` itself ever reconciles devices internally was checked by reading the call sites, not the podManager internals; the report's repro result (20000 MiB stays on GPU-a) is consistent with it not doing so.

## Sources

- Issue: <https://github.com/Project-HAMi/HAMi/issues/3366>
- scheduler.go at f1148b5b: <https://github.com/Project-HAMi/HAMi/blob/f1148b5b7a/pkg/scheduler/scheduler.go>
- numa_refit_handler.go at f1148b5b: <https://github.com/Project-HAMi/HAMi/blob/f1148b5b7a/pkg/scheduler/numa_refit_handler.go>
