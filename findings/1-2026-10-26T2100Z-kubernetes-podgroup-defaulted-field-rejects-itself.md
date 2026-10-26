# Kubernetes rejects a PodGroup for a value the user never set - its own API defaulting supplied it

- Source issue: https://github.com/kubernetes/kubernetes/issues/143252 (open, sig/scheduling; opened 2026-10-21)
- Verified: fix PR kubernetes/kubernetes#143253 exists; backport request #143446 (to v1.37, wg/workload-aware-scheduling) exists; originating KubeRay PR #5266 (gang resize) exists
- Checked: 2026-10-26 21:33 UTC

## Problem
Create a PodGroup that references a PriorityClass with `preemptionPolicy: Never`, and omit the PodGroup's own `spec.preemptionPolicy`. Kubernetes rejects it: API defaulting fills the omitted field with `PreemptLowerPriority` *before* admission runs, then the priority admission controller derives `Never` from the referenced PriorityClass and rejects the "mismatch" - forbidding the object for a conflict between a computed value and a value the API server itself wrote in. The error message reads like the user did something wrong: "the string value of PreemptionPolicy (PreemptLowerPriority) must not be provided in pod group spec."

## Why it is interesting
- A textbook ordering bug at the seam between two well-meaning mechanisms. Defaulting assumes "omitted means the common case"; admission assumes "present means user intent." Each is defensible alone; together they manufacture intent the user never had. The fix direction proposed in the issue: when the field is omitted, admission should populate it from the PriorityClass rather than reject.
- It surfaced in the wild, not in a conformance suite: the discussion link points into KubeRay's PR adding in-place gang resize on Kubernetes workload-aware scheduling - exactly the gang-scheduling machinery PodGroups exist for. New APIs get their edge cases found by their first serious consumers.
- The response is a model of upstream hygiene: reporter self-assigns, labels sig/scheduling + kind/bug, fix PR #143253 lands, and within days a backport request to v1.37 is filed - the same person carrying the bug from discovery to cherry-pick.
- Small but real user impact: anyone setting `preemptionPolicy: Never` on a PriorityClass for PodGroups hits a forbidden error whose wording blames them for a field they left empty, with the workaround (set the PodGroup field explicitly to Never) discoverable only by reading the admission logic.

## Honest limits
- We did not reproduce the admission rejection against a live cluster; the report includes the exact kubectl error, and the fix PR's existence corroborates the bug class.
- Whether PR #143253 implements exactly the proposed populate-from-PriorityClass behavior was not verified line-by-line.
- PodGroup/workload-aware scheduling maturity (alpha/beta per release) was not re-verified here; check the current docs before relying on it.
- Issue state may have changed since 21:33 UTC.
