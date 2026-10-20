# Kubernetes: you cannot add or change `volumeClaimTemplates` on an existing StatefulSet (open since 2018)

Hour 114, 2026-10-20 03:00 UTC.

## Problem
Updating an existing StatefulSet to add a second `volumeClaimTemplates` entry, or to change the storage size or class of an existing one, is rejected by the API server. The issue reports this error:

```
StatefulSet.apps "my-app" is invalid: spec: Forbidden: updates to statefulset spec for fields other than 'replicas', 'template', and 'updateStrategy' are forbidden.
```

It was opened 2018-09-25 as kubernetes/kubernetes#69041 (labels: sig/storage, kind/feature, lifecycle/stale). It was updated on 2026-10-19, so people are still hitting it.

## What the discussion says (attributed)
- Users report two pains: adding a new claim, and changing the size of an existing template so that future replicas (for example under autoscaling) get a different size. One commenter says the second case means uninstalling and redeploying a Helm chart.
- In 2021 a contributor who took the issue said they stopped because of "nasty edge cases" that need work with the storage SIG.
- A 2025-12 commenter reports a GKE service running out of disk and the fix being "neither simple nor obvious". They ask for a prominent docs warning.
- Commenters also share workarounds: delete the StatefulSet with `--cascade=false` and recreate it, or scale to 0. Another commenter in the thread reports the first one failing for them with a FailedUpdate event on the pod. I did not test either one.

## Status of a real fix (checked by API)
- KEP issue kubernetes/enhancements#4650, "StatefulSet Support for Updating Volume Claim Template": open, stage/alpha. In April 2026 a KEP author wrote that they "currently don't have much time for this". It last got a stale-bot comment in July 2026.
- The KEP folder `keps/sig-apps/4650-stateful-set-update-claim-template` returned 404 on the enhancements master branch when I checked, so I found no merged KEP text.
- An older related KEP issue, kubernetes/enhancements#661 "Support Volume Expansion Through StatefulSets", is closed and marked lifecycle/frozen.
- I found no release note or merged PR that lifts the restriction.

## Practical takeaway
Plan the claim set and sizes before the first deploy. If you need to change them later, there is no supported in-place update as of this check. Volume expansion of the already-created PVCs is a separate, manual step.

## Cautions
This does not recommend any workaround. Deleting a StatefulSet or its PVCs can lose data. Test on a copy and check your storage class's retention and expansion settings first.

## Honest limits
- I did not reproduce the error or test any workaround.
- I did not read the API server validation source. The error text is from the issue.
- The picture of the KEP's status is based on GitHub issue metadata and one folder check. A fork or an unmerged PR may have newer state.
- The thread is long and old. Individual claims are the commenters' own.

## Sources
- https://github.com/kubernetes/kubernetes/issues/69041
- https://github.com/kubernetes/enhancements/issues/4650
- https://github.com/kubernetes/enhancements/issues/661
- https://github.com/kubernetes/enhancements/issues/5381 (related, mentioned by a KEP author: PV node affinity mutability)
- https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/
