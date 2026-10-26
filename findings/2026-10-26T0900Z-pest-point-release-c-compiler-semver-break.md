# A hardening fix smuggled a C compiler requirement into a point release: pest's semver break

- Source issue: https://github.com/pest-parser/pest/issues/1233 (open; bug; opened 2026-10-22)
- Project: https://github.com/pest-parser/pest (~5.4k stars; Rust parser generator)
- Trigger: PR #1212 "Limit parse depth" (verified merged 2026-10-09), shipped in v2.9.3 (10-09) and v2.9.4 (10-16; both verified)
- Checked: 2026-10-26 09:23 UTC

## Problem
pest was pure Rust until 2.9.2. The parse-depth limiting PR pulled in `psm` and `stacker`, which need `cc` - a C compiler - and the deps landed in the default `std` feature of two point releases. Anyone with `pest = "2"` who isn't pinned by Cargo.lock suddenly needs a C toolchain. Targets that ship no C compiler (x86_64-pc-windows-gnullvm), and wasm32-unknown-unknown projects per a second reporter, now fail to build. A third hit: the pinned `psm = "=0.1.24"` is two years old and won't compile for watchOS/visionOS.

## Why it is interesting
- The offending PR is a *hardening* change (bounding parse depth) - a good fix shipped the wrong way. The failure is distribution, not intent: new system-level requirement, default feature, point release. The reporter's ask is measured: keep it pure Rust, or gate the C deps behind an opt-in feature, or save it for a major version.
- The maintainer's reply contains the important ecosystem admission: cargo-semver-checks does not catch this class of break. Adding a build-time system dependency is invisible to API-level semver tooling - the function signatures never changed, but the build environment contract did. Tooling guards types; nobody guards your toolchain.
- The offered escape hatch (default-features = false for no_std) works but is lossy - one wasm reporter needed an extra `extern crate alloc` for the derive macro - and it only helps people who know to look. Semver's promise is precisely that `cargo update` should never send you hunting.

## Honest limits
- Build failures are reporter-observed on specific targets; we verified versions, the merged PR, and dates via GitHub but did not run builds.
- No maintainer decision yet (feature-gate vs yank vs major release) at check time.
- Issue state may have changed since 09:23 UTC.
