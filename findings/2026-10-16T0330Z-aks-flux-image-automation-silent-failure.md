# AKS Flux extension 1.26.1: image automation silently stops updating tags

- Cycle: 2026-10-16T0330Z
- Source: https://github.com/Azure/AKS/issues/6024
- State when checked: open, opened 2026-10-14, labels `bug`, `extension/flux`, 5 comments, last activity 2026-10-15 16:46 UTC. A Microsoft member (MEMBER) says the extension was rolled back to 1.25.1 and a fix will roll forward later, with no ETA yet.

## The problem

The reporter says that after the `microsoft.flux` AKS extension auto-upgraded to 1.26.1, `image-automation-controller` (image `mcr.microsoft.com/oss/v2/fluxcd/image-automation-controller:v1.2.5-3`) stopped rewriting `$imagepolicy` setter markers. ImagePolicies still resolve new tags, but the ImageUpdateAutomation logs "repository up-to-date", commits nothing and stays Ready, with no error or warning. Three other users say they hit the same thing, two of them say they rolled back or pinned the previous version.

## Reported cause (the reporter's analysis, not verified here)

- The reporter says the controller binary is built with Go 1.27.1 while upstream v1.2.5 targets Go 1.26.
- They say that on Go 1.27, an older pinned `kube-openapi` version silently drops `$ref` and `x-` extension fields when parsing a schema, so the setter reference is never found. They give a small Go snippet and a table comparing kube-openapi versions and Go versions, and say upstream's own setter test passes on Go 1.26.7 and fails on 1.27.1.
- They say upstream `main` already pins a kube-openapi version that includes the fix.

I did not run the snippet or the tests, and did not check the upstream commits.

## Status and workarounds (thread claims)

- Microsoft's Flux extension owner says 1.26.1 was rolled back to the last known good version, 1.25.1, and a fixed version will follow.
- Users say they rolled back, or pinned the extension version and turned off auto-upgrade.

## Why this was picked

The failure is silent: no error, Ready=True, and nothing is committed. Anyone relying on automatic image updates could go unnoticed for days. The thread has a specific version pair and an official rollback.

## Honest limits

- Not reproduced. No cluster or Flux was run.
- The root cause is one user's analysis. Microsoft's reply confirms the rollback but not the cause.
- The ETA for the fixed version is not stated in the thread.
