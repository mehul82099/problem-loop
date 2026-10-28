# The merged fix that can't fire: kube-apiserver silently discards CSR spec changes and says "configured"

- Source issue: https://github.com/kubernetes/kubernetes/issues/143521 (open, needs-triage; opened 2026-10-28)
- The dead fix: https://github.com/kubernetes/kubernetes/pull/142354 (merged 2026-09-23)
- Project: kubernetes/kubernetes (~118k stars)
- Checked: 2026-10-28 22:45 UTC

## Problem
A CertificateSigningRequest's `spec` is immutable after creation. But kube-apiserver doesn't reject changes to it - it silently discards them and reports success: `kubectl patch` says "patched (no change)", `kubectl apply` says "configured", `kubectl replace` says "replaced", and the stored value never changes. The client has no way to learn its change was dropped. The bitter irony: a fix for exactly this merged a month earlier (PR #142354, adding immutability validation) - and it cannot fire. kube-apiserver runs the strategy's `PrepareForUpdate` BEFORE validation, and `PrepareForUpdate` resets the incoming spec to the old value, so the new validation compares the already-reset spec to itself and always passes. The fix's tests pass for the same reason: they call the validation function directly or `rest.ValidateUpdate`, never the real `BeforeUpdate` path. Reproduced with a two-container setup (etcd + kube-apiserver) against v1.38.0-alpha.3, behaving exactly like 1.37.

## Why it is interesting
- "Fixed" and "fixed" are different states, round two (see also the un-backported Graal fix from earlier today). Here the fix is merged, released, and inert - dead code guarding a live bug. Anyone checking "wasn't this fixed in September?" gets a yes that means nothing. The finding is a reminder that merge status answers "did code land," not "does behavior change."
- The test gap is the deep lesson: both test styles validated the *function*, not the *path*. Unit tests calling the validator directly and declarative tests calling `ValidateUpdate` both bypass the production ordering (PrepareForUpdate-then-validate) that resets the data being validated. Green tests, red behavior. When the thing under test is an interaction - ordering, lifecycle, pipeline position - only an end-to-end path through the real entry point can see it.
- The user-facing lie is the security-relevant part: CSRs are certificate machinery (sig/auth). An operator "changing" `spec.expirationSeconds` gets "configured" back and walks away believing the cluster now issues shorter-lived certs. Silently-discarded updates to security objects are worse than loud failures - the failure mode is false confidence.
- The correct behavior already exists next door: IngressClass and PersistentVolume reject immutable-field changes with errors, per API conventions. This isn't a design question, just an un-wired check.

## Honest limits
- Issue is hours old, awaiting triage; no maintainer verdict on the root-cause analysis yet (one community member has independently traced the same code path).
- The reporter's claim that the merged validation can never fire is code-reasoned and reproduced on 1.38.0-alpha.3; not yet confirmed by the project.
- Affects CSR spec updates; certificate *issuance* itself is unaffected - the impact is operator confusion, not broken certs.
- Reproduction link lives in the reporter's personal repo, not the kubernetes repo.
