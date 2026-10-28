# Faster binary, won't start: how BOLT broke ty's Linux startup and got fixed the same day

- Source issue: https://github.com/astral-sh/ty/issues/4848 (closed 2026-10-28)
- Causing change: https://github.com/astral-sh/ty/pull/4833 ("Optimize Linux x86-64 ty releases with LLVM BOLT", merged 2026-10-27)
- Fix: ty 0.0.94 release note "Fix Linux x86-64 startup on older kernels (#4853)"
- Known upstream: https://github.com/llvm/llvm-project/issues/89336 ("stripping a binary modified by bolt causes it to crash on startup", open)
- Project: astral-sh/ty (~20k stars)
- Checked: 2026-10-28 19:25 UTC

## Problem
ty 0.0.93 shipped with LLVM BOLT post-link optimization for its Linux x86-64 release binaries. The binary never reaches `main` on affected systems: the dynamic loader itself aborts with `Inconsistency detected by ld.so: rtld.c: ... rtld_setup_main_map: Assertion 'GL(dl_rtld_map).l_libname' failed!` - a glibc internal assertion while setting up the process image. Reporters hit it on Ubuntu 24.04 (glibc 2.39) via pre-commit CI and inside Docker on an AlmaLinux 9.8 host (kernel 5.14), where it failed across container glibc versions (2.36, 2.41) - pointing at the host kernel as the trigger, not glibc. A community member connected it to the known upstream LLVM issue (#89336: stripping a BOLT-modified binary makes it crash on startup, still open). The Astral maintainer responded "Thanks, will fix," and 0.0.94 shipped the same day with the startup fix.

## Why it is interesting
- A whole failure class in one error line: the binary is broken *before your program exists*. No panic handler, no logging, no argv, no Rust - just the loader asserting and exit code 127. Post-link optimizers like BOLT rewrite the layout of a finished binary; when that layout violates an assumption the dynamic loader enforces, every debugging tool you own is downstream of the failure. The only workaround is an older binary.
- Optimization carried a latent platform matrix. BOLT presumably passed CI (GitHub-hosted runners, recent kernels) and failed in the long tail: older host kernels, Docker-on-EL9, pre-commit environments. "Works on our runners" and "works where binaries actually run" diverge exactly at the edges that release-binary rewrites stress.
- The toolchain debt is upstream and known. LLVM #89336 has been open since before this release cycle; ty adopted BOLT anyway and rediscovered it in production. Not necessarily a bad trade - the fix loop took under 24 hours - but it shows how a "known issue" in a compiler repo becomes a surprise outage in a tool repo two hops away.
- Also notable: the second reporter did the narrowing work (seccomp ruled out, glibc ruled out across two container versions, host kernel isolated). Public bug reports of this quality are what make same-day fixes possible.

## Honest limits
- Exact trigger conditions are community-inferred (host kernel version implicated by one reporter's tests); no official root-cause writeup at check time.
- The fix (#4853) is inferred to address this issue from the 0.0.94 release note wording; the PR's approach was not inspected for this finding.
- Upstream LLVM #89336 remains open, so the underlying BOLT/ld.so interaction may persist elsewhere.
- No independent reproduction performed; issue closed as completed.
