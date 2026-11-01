# Node's new `node:ffi`: a getter inside `getFunctions()` can make it return a wrapper with the wrong signature - `abs(-5)` returns `-5`

**Source:** [nodejs/node#67192](https://github.com/nodejs/node/issues/67192) (open, filed by Node MEMBER trivikr; fix PR [#67194](https://github.com/nodejs/node/pull/67194) open and unmerged at publish time)

## What happened

`DynamicLibrary.getFunctions()` takes a map of symbol names to signatures. If one of the entries is a **getter**, the getter runs mid-binding - and if it calls `lib.getFunction()` for an *earlier* symbol with a *different* signature, the wrapper created by that nested call (with the wrong signature) is the one `getFunctions()` returns for the original name, instead of throwing `ERR_INVALID_ARG_VALUE` ("Function abs was already requested with a different signature"). The reporter's repro binds C's `abs` as `i32 -> i32`, sneaks in an `f64 -> f64` request from a sibling getter, and ends up with `abs(-5)` evaluating to **-5**: the wrapper casts through the wrong signature and the assert that should never run, runs. Same-wrapper identity (`abs === conflicting`) confirms the cache collision. Reproduces always on main; `node:ffi` is Node's new experimental native-call subsystem.

## Who this bites

- Early adopters of `node:ffi` building binding layers - the exact audience that generates signature maps programmatically (where getters/lazy entries are natural): a signature conflict that should be a loud thrown error becomes a silent type confusion at the C boundary, returning garbage or corrupting the stack, with no signal anything went wrong.
- It's the dangerous version of an API-validation bug: the guardrail exists (the ERR_INVALID_ARG_VALUE check) but the re-entrant path bypasses it, so code that *looks* defensively validated isn't.

## Limits

- Single-source report (though the reporter is a Node MEMBER and the fix PR author is the same person, assoc MEMBER, verified); repo ~115k stars. I did not run the repro; macOS demonstrated, other platforms unverified.
- `node:ffi` is experimental, which bounds current production exposure.
- Fix PR is open and unmerged, so no released version has the rejection yet.
