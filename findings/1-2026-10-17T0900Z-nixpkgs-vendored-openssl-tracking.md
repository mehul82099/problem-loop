# nixpkgs: which packages carry their own, possibly outdated, OpenSSL

- Source: https://github.com/NixOS/nixpkgs/issues/570550 "Tracking: Vendored OpenSSL libraries" (open, labels `1.severity: security` and `5.scope: tracking`, opened 2026-10-05 by RossSmyth, last comment 2026-10-17)
- Links checked through the GitHub API on 2026-10-17:
  - https://github.com/NixOS/nixpkgs/pull/574553 "julia_113{,-bin}: 1.13.1 -> 1.13.2": open, not merged
  - https://github.com/NixOS/nixpkgs/pull/537108 "rustplatform.cargoSetupHook: force common system libs": merged 2026-10-14
  - https://github.com/NixOS/nixpkgs/issues/570932 "Update Request: Archipelago 0.6.7 -> 0.6.8": closed

## The idea
Some packages ship their own copy of OpenSSL (via submodules or bundled sources), so they miss security patches that nixpkgs applies to its own `openssl`. The tracker lists such packages, found with `nix-locate` searches for `openssl.so`, `libssl.so` and `libcrypto.so`. The preferred fix is to replace the bundled library with a link to the nixpkgs one so patches reach the package automatically.

## What the thread found (commenters' analysis)
- Many early hits are false positives: `luaossl` and the Ruby `openssl.so` are bindings to the real library (vcunat, samueldr-at-cyberus). `libressl`, `aws-lc` and `boringssl` are forks, not copies. `rustls-libssl` is a shim over rustls.
- Version detection: samueldr-at-cyberus shared a Ruby FFI script that reads `OPENSSL_version_major/minor/patch` from a library, since the string form is not in every build.
- On 2026-10-16 GrimmTheShrimp ran an adaptation over the list and added versions to the issue. Of the ones where a version could be read, the ones he flagged as a problem were:

| Package | Vendored OpenSSL version reported |
|---|---|
| archipelago | 3.0.2 |
| pgsql-tools | 3.0.2 |
| wasabibackend, wasabiwallet | 3.0.15 |
| julia, julia-bin, julia_112 | 3.5.6 |

He describes 3.0.2 and 3.0.15 as both from September 2024, and 3.5.6 as from April 2026. These dates are his, and I did not check them against OpenSSL's release history.
- He re-ran the check against `staging-next`, where nixpkgs OpenSSL is 3.5.9, and everything that had shown 3.5.8 moved to 3.5.9. His conclusion is that those use the nixpkgs copy and can be ticked off.
- Many entries remain "unknown" because the version could not be read or the library failed to load.

## Maintainer replies
- whispersofthedawn (says they maintain tor-browser): it bundles OpenSSL for the `tor` binary, is regularly updated upstream, and they plan to switch to nixpkgs OpenSSL or `tor`.
- taranarmo (Julia): Julia ships its dependencies in source, and found commits bumping OpenSSL to 3.5.8 in the 1.12 and 1.13 branches. A nixpkgs PR for Julia 1.13.2 (#574553) is open.
- RossSmyth, the tracker's author, on why this matters: two steps must happen (upstream bumps, then nixpkgs bumps), so linking to the nixpkgs copy is preferred. He asked Julia and pgsql-tools maintainers to look at devendoring. For Rust packages that embed AWS-LC, he points to PR 537108, now merged.

## Honest limits
- I scanned no packages and ran no script. Every version number comes from the issue body or comments.
- I did not verify any CVE exposure. The thread links to NVD searches for the versions, and I did not read them, so "out of date" is the commenters' term and not a vulnerability claim from me.
- Whether a vendored copy is actually used at runtime in each package is not established. The `nix-locate` search shows only that the library file exists.
- The tracker is open and many entries are unchecked.
