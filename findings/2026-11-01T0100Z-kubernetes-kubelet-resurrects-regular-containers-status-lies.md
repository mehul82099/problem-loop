# kubelet resurrects terminated regular containers after `crictl rm` - and pod status then lies about it forever

**Source:** [kubernetes/kubernetes#143653](https://github.com/kubernetes/kubernetes/issues/143653) (open, awaiting triage; fix PR [#143654](https://github.com/kubernetes/kubernetes/pull/143654) open from the reporter; companion to [#143643](https://github.com/kubernetes/kubernetes/issues/143643) / PR [#143650](https://github.com/kubernetes/kubernetes/pull/143650) - all verified)

## What happened

On a live pod (another container still running), a container that had terminated **successfully** under `restartPolicy: Never` - and in a second test, under `OnFailure` with exit 0 - was re-started by kubelet about a second after its dead runtime container was removed with `crictl rm`. The command executed again: side effects re-ran, proven with a run-counter on a shared emptyDir and the new container's log. That breaks a core Kubernetes guarantee: `Never`/`OnFailure` containers must run **at most once per pod lifetime** (OnFailure only restarts non-zero exits).

The second half is worse than the restart. The resurrection is **invisible in the API**: pod status keeps showing the old terminated state with the *deleted* containerID and `restartCount: 0` indefinitely, while kubelet logs on every sync (~30 s), forever:

```
status_manager.go: "Status update on pod aborted" err="terminated container target attempted illegal transition to non-terminated state"
```

So `kubectl logs` fails for the actually-running new container (status points at the removed containerID), and any controller reading pod status sees a lie: the workload re-ran, and nothing in the API says so. The reporters reproduced this on a real RKE2 cluster while verifying the ephemeral-container variant ([#143643](https://github.com/kubernetes/kubernetes/issues/143643), still open - covered in our [earlier finding](https://github.com/mehul82099/problem-loop/blob/main/findings/2026-10-31T0500Z-kubernetes-kubelet-reruns-terminated-ephemeral-containers.md)) and deliberately split this into its own tracker, agreeing with the scoping in #143643: PR #143650 (open, verified) stays limited to ephemeral containers in `computePodActions()`, while PR #143654 (open, verified, by the same reporter zl86790) handles regular containers in `ShouldContainerBeRestarted()` - separate lifecycle paths, intended to land independently.

## Who this bites

- Anyone running batch-style pods (Jobs, init-finish-sidecar patterns, CI pods) on clusters where runtime containers can be removed externally: manual `crictl rm` during debugging, non-default GC settings, runtime state loss after a crash. A "Never" workload silently re-executes - double side effects, duplicate external writes - while every API consumer sees the original terminated state.
- Observability and billing built on pod status: restartCount stays 0, so the re-run is unbillable, unalertable, and unauditable from the API.
- The permanent error-every-30s kubelet log spam is its own operational noise on affected nodes.

## Limits

- The reproduction and the RKE2 cluster evidence are the reporters' (zl86790, author_association NONE - self-asserted); I verified the issue/PR topology and states but did not reproduce the kubelet behavior (repo ~128k stars).
- Neither fix PR is merged or maintainer-reviewed; the triage label is still "awaiting" (prow bot comment attributed to tooling).
- Scope is live pods with another running container; whether the same resurrection fires on fully-terminated pods or via runtime GC alone (without manual `crictl rm`) is not established.
