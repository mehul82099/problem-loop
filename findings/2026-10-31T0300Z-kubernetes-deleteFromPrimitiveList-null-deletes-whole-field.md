# A strategic merge patch with `"$deleteFromPrimitiveList/<field>": null` deletes the whole field - finalizers included

**Source:** [kubernetes/kubernetes#143638](https://github.com/kubernetes/kubernetes/issues/143638) (open, `kind/bug`, `sig/api-machinery`, `needs-triage`; the code path verified against `master`; no maintainer response yet)

## What happened

Kubernetes documents a [strategic merge patch directive](https://github.com/kubernetes/community/blob/main/contributors/devel/sig-api-machinery/strategic-merge-patch.md) `$deleteFromPrimitiveList/<field>` whose list value names the primitive elements to remove from `<field>`. The reporter shows that when the directive's value is `null`, the apiserver returns 200 and deletes the entire field instead of deleting no element: `{"metadata":{"$deleteFromPrimitiveList/finalizers":null}}` strips every finalizer, and the same directive on `labels` or `data` empties those maps. A directive value of `[]`, a list with no matching element, or a plain string all leave the field alone.

The client-side trap: a Go caller that builds the patch from a nil `[]string` marshals it as `null`, so code that intends "remove these zero finalizers" removes all of them. On an object already being deleted, losing its finalizers deletes the object at once.

Reproduction (reporter's, against Server v1.37.2, also v1.38.0-alpha.3 and v1.34.1 - so not a regression): five `kubectl patch --type=strategic` calls on a ConfigMap with two finalizers; only the `null` one empties the field, and a second patch with `$deleteFromPrimitiveList/labels: null` and `$deleteFromPrimitiveList/data: null` empties both maps. All five calls return 200.

## Why it happens

In `mergeMap` in `staging/src/k8s.io/apimachinery/pkg/util/strategicpatch/patch.go`, the null branch runs before the directive is honored: `preprocessDeletionListForMerging` sets `isDeleteList` (line 1349), then `if patchV == nil { delete(original, k) ... }` (lines 1368-1373) removes the whole field unconditionally; the `isDeleteList` checks only come later (line 1377 onward), after the damage. Verified on `master` at the same lines, and against commit `386245de` the reporter cites ([patch.go#L1349-L1373](https://github.com/kubernetes/kubernetes/blob/386245def96934751c6fe8014aa9a9a0b60f7ab8/staging/src/k8s.io/apimachinery/pkg/util/strategicpatch/patch.go#L1349-L1373)). The reporter suggests skipping the deletion when `isDeleteList` is set, or rejecting a non-list directive value with `mergepatch.ErrBadPatchFormatForPrimitiveList`.

## Who this bites

- Any controller or operator that patches finalizers, labels, or `data` through a strategic merge patch built from a Go slice that can be nil - a very natural shape for "remove these elements" code.
- Objects under deletion are the worst case: stripping finalizers finalizes them immediately, bypassing whatever cleanup the finalizer was guarding.

## Limits

- The kubectl outputs are the reporter's (association NONE); I verified the code path on `master` and at the cited commit, the linked doc, and the search for prior duplicates (earlier `$deleteFromPrimitiveList` bugs - #105421, #105146, #82320 - are closed and about different behaviors), but I did not run the reproduction against a live apiserver.
- The issue is one day old with no maintainer response; only the prow triage bot and the reporter's own `/sig api-machinery` have commented (bot output is tooling, not triage acceptance).
- Long-standing behavior (present since at least v1.34.1 per the reporter), so a fix could face compatibility scrutiny: some clients may already depend on `null` clearing the field. The finding takes no position on the suggested fix.
- Related prior hour: [kubernetes#143637 finalizer-removal SSA bug](2026-10-30T1800Z-kubernetes-ssa-last-finalizer-removal-strips-foregrounddeletion-object-deleted.md) covers a different finalizer-stripping path (server-side apply, not strategic merge patch).
