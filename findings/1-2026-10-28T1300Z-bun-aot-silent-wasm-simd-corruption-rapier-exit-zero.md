# Exit code 0, physics broken: Bun's new AOT path silently corrupts a WASM SIMD world

- Source issue: https://github.com/oven-sh/bun/issues/47189 (open; opened 2026-10-28)
- Project: oven-sh/bun (~96k stars)
- Checked: 2026-10-28 13:15 UTC

## Problem
Same canary executable, three ways to run the same Rapier physics script: `bun run` (JIT) works, `bun build --compile` (JIT executable) works, and `bun build --compile --aot` - Bun's new experimental ahead-of-time path - produces a binary that exits 0 with no stderr, no Wasm trap, and a quietly broken simulation: the floor collider starts enabled but is disabled after the first step, the raycast misses the floor entirely, and the falling sphere floats forever at its initial height. The reporter pins everything: exact canary revision with SHA-256, exact dependency version, exact WASM byte size, and the extra experiment of loading the raw unchanged .wasm bytes directly (JIT still fine, AOT still broken). Failure also reproduced on stable for the JIT cases (which pass) and on an earlier experimental AOT revision (which fails the same way).

## Why it is interesting
- Silent semantic corruption is the worst failure class a new compiler pipeline can have. A crash is a bug report; a program that runs to completion with exit 0 while its computed world quietly stops making sense is a corrupted artifact that ships. The AOT build succeeds, the binary runs, and only the numbers are wrong - colliders disable, rays miss, gravity stops. Nobody gets told.
- The control structure of the report is textbook. Three runs of one script with one binary (source, JIT-compiled, AOT-compiled), identical revision, identical dependency bytes. When two agree and one doesn't, the variable is isolated to the AOT pipeline itself - no application code, no flags, no patches. This is how you file a compiler bug so it cannot be bounced back.
- WASM SIMD is the frontier where young toolchains bleed. Rapier's SIMD colliders lean on Wasm vector instructions; a new AOT backend that lowers or caches code differently is exactly where a vector path can be miscompiled or silently skipped. The mechanism is unconfirmed (mis-lowering? feature detection gone wrong? unsupported opcode dropped?), and the finding frames it as an open question - but the behavioral fingerprint (SIMD-heavy math degrading rather than trapping) is consistent across both the package path and raw bytes.
- Timing note: this is an experimental flag on a canary build, reported within a day of that canary - the report is early-warning, exactly when a broken optimization pipeline is cheapest to fix.

## Honest limits
- Single reporter, no maintainer response at check time (~45 minutes after filing).
- Root cause unknown and explicitly unclaimed; only the behavioral difference (AOT vs JIT, same bytes) is demonstrated.
- Affects an experimental --aot flag on canary builds; stable releases' normal JIT paths are unaffected per the report.
- macOS arm64 only in the report; other platforms unverified.
- Issue state may have changed since 13:15 UTC.
