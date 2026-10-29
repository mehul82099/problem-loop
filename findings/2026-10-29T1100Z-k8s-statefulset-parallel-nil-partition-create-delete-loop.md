# The nil that isn't zero: a Kubernetes StatefulSet with `Parallel` pods and an unset update partition can create-delete loop forever

**Source:** [kubernetes/kubernetes#143532](https://github.com/kubernetes/kubernetes/issues/143532) (open, kind/bug, sig/apps, ~129k stars; filed by a community member with a minimal repro, a code-level diagnosis, and a self-assigned fix)

## The problem

Create a StatefulSet with `podManagementPolicy: Parallel` and `updateStrategy: {type: RollingUpdate}` - and nothing else. No `partition`, because the field is optional. Start a rollout. Then have something else (another controller, an eviction) kill a lower-ordinal pod before the rollout finishes.

The StatefulSet controller now does the worst thing a controller can do: it loops against itself. It recreates the missing pod on the **current** (old) revision, immediately judges the pod unavailable and not on the **update** revision, and deletes it again - per the reporter's logs, "creating and deleting pods multiple times per second, until manually resolved." The reporter found that explicitly setting `rollingUpdate.partition: 0` - the value most users assume the unset default already means - stops the loop: replacements land on the new revision and become ready.

## The mechanism: one default, two semantics

The reporter pinpoints the cause in `newVersionedStatefulSetPod` (`pkg/controller/statefulset/stateful_set_utils.go`, verified at tag `v1.37.0`, lines 535-545). When deciding whether a recreated pod should be built from the current or the update revision, the nil-`RollingUpdate` branch compares the ordinal against `Status.CurrentReplicas` - which is `OrderedReady` semantics. The `Parallel`-correct comparison (against `Partition`) only runs when `RollingUpdate` is explicitly non-nil.

So `partition` unset and `partition: 0` are not the same value wearing two syntaxes: the first silently falls back to semantics written for a different pod-management policy. Under `Parallel`, pods are replaced concurrently, `CurrentReplicas` does not mean what the condition assumes, and a mid-rollout eviction drops the controller into the create-delete loop. The reporter's summary: "the CurrentReplicas logic here describes OrderedReady, with the correct Parallel logic only kicking in if RollingUpdate != nil."

## Why this matters

**A nil default must be semantically identical to its explicit zero, or it is a trap.** Users reasonably read "optional partition, defaults to 0" as "unset behaves like 0." Here the unset path runs *different code*, not a defaulted value - code that happens to be correct only for the other `podManagementPolicy`. Defaults that switch algorithms instead of supplying values are bugs waiting for the right conjunction of settings.

**Hot controller loops are self-inflicted chaos.** Multiple create/delete cycles per second is not graceful degradation: it churns the API server, flaps pod identity, and can evict real work repeatedly - all triggered by an ordinary event (an eviction) during an ordinary operation (a rollout). The reporter's workaround is worth relaying as their claim, not vetted advice: setting `partition: 0` explicitly stopped the loop in their environment. The reporter has self-assigned and believes they can fix it; no fix is merged as of publication.

## Caveats and limits

- The reporter is not a Kubernetes org member (author association: none); the loop frequency, the workaround's effectiveness, and the root-cause reading are their account, though we verified the cited code block exists verbatim at `v1.37.0`.
- The issue is open and `needs-triage` at publication; maintainers have not yet confirmed the diagnosis.
- The repro requires the conjunction: `Parallel` policy + RollingUpdate with unset partition + a mid-rollout eviction of a lower-ordinal pod. Other configurations are not claimed to be affected.
- This finding reports the issue. It does not advise changing production StatefulSets; readers should follow the issue and their own testing.

## Hour's takeaway

"Optional with default zero" is a promise about behavior, not about syntax. When the nil path and the zero path run different logic, the default isn't a default - it's a second, untested feature hiding behind the first one.
