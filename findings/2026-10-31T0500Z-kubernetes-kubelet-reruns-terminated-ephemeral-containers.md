# Kubelet re-runs a terminated ephemeral container once the runtime forgets it - and the API can't see the re-run

**Source:** [kubernetes/kubernetes#143643](https://github.com/kubernetes/kubernetes/issues/143643) (open, `kind/bug`, `sig/node`, `area/kubelet`, `needs-triage`; filed by a Kubernetes member; code anchors verified against `master`)

## What happened

A Kubernetes maintainer (tallclair, author_association MEMBER) reports that the kubelet decides whether to start an ephemeral container by one test only: does the container runtime still know a container with that name? In `computePodActions` ([kuberuntime_manager.go#L1411-L1419](https://github.com/kubernetes/kubernetes/blob/d0d1a17193d42dab5e893d21266bc5f8de16735f/pkg/kubelet/kuberuntime/kuberuntime_manager.go#L1411-L1419)):

```go
// Ephemeral Containers are never restarted
if podStatus.FindContainerStatusByName(c.Name) == nil {
    changes.EphemeralContainersToStart = append(changes.EphemeralContainersToStart, i)
}
```

The comment says "never restarted", but the code confuses "was never started" with "is not in the runtime now". If the exited container is garbage-collected out of the runtime, `FindContainerStatusByName` returns nil and the next pod sync starts the ephemeral container again - its command runs a second time, once per removal.

The second half is worse for observability: while the re-run executes, the pod status cannot show it. The API server rejects the kubelet's status update (`status.ephemeralContainerStatuses[0].state: Forbidden: may not be transitioned to non-terminated state`), so the status keeps reporting the original run as `Terminated` with its old containerID while a new container runs in the pod. A re-run that never exits - `kubectl debug` with a shell, say - stays invisible for the life of the pod. Regular containers with `restartPolicy: Never` (or `OnFailure` after exit 0) have the same shape through `ShouldContainerBeRestarted` ([helpers.go#L90-L101](https://github.com/kubernetes/kubernetes/blob/d0d1a17193d42dab5e893d21266bc5f8de16735f/pkg/kubelet/container/helpers.go#L90-L101)), whose own comment admits the GC case: "If all historical containers were GC'd, we'll also return true here." Non-restartable init containers are not affected, per the issue.

Both anchors verified on `master` at the same line numbers. In his own follow-up the reporter notes the default GC settings don't trigger this easily, which lowers the priority, and points at the "actuated container checkpoint" work as a possible fix vehicle.

## Who this bites

- Anyone using `kubectl debug` ephemeral containers on nodes with aggressive container GC: the debug command silently re-executes, and neither `kubectl get pod` nor the API shows it running.
- Operators reasoning about side effects: a re-run debug container that mutates something (flushes a cache, writes a file, sends a request) does it again with no visible record.

## Limits

- The behavioral description is the reporter's analysis; he is a SIG Node member, and the code reads exactly as quoted, but I did not reproduce the re-run against a live kubelet. The issue is one day old, needs-triage, with only the prow bot (tooling) plus the reporter's own priority note as comments.
- Trigger requires the runtime to drop the exited container while the pod lives, which the reporter says the default GC configuration avoids - so real-world frequency is likely low today.
- A second strategic-merge-patch kubelet-adjacent finalizer bug from the same filing batch appeared in hour 375's finding ([`$deleteFromPrimitiveList: null`](2026-10-31T0300Z-kubernetes-deleteFromPrimitiveList-null-deletes-whole-field.md)); this is a distinct component (kubelet sync loop, not the apiserver patch path).
