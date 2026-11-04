# CPython: perf trampoline segfaults on UBSan builds because -fsanitize=function reads a type signature that is not there

**Source:** [python/cpython#161288](https://github.com/python/cpython/issues/161288) - opened 2026-11-04 by NekoAsakura (GitHub association: MEMBER of python/cpython).

## What the report says

On a UBSan build, `./python -X perf -c pass` segfaults at `Python/perf_trampoline.c` line 464. Mechanism: `-fsanitize=function` instruments every call through a function pointer to read a type signature stored 8 bytes before the called function. The perf trampoline is machine code copied into an mmap'd buffer and carries no such signature; it sits at the start of the buffer, so the 8 bytes before it are unmapped and the sanitizer's read segfaults. The crash was caught on #161278 (a test-suite fix that stopped skipping the embed tests that would have exercised this). Linked PR gh-161294 carries the reporter's fix.

## Verification (checked during this finding)

- The cited commit (`7e3290d9`, 2026-11-03) exists; at `Python/perf_trampoline.c:464` the line is the function-pointer call `return f(ts, frame, throw, ...)` through the compiled trampoline `f` - exactly the call site the mechanism describes.
- Linked PR gh-161294 exists and is open ("fix perf trampoline crash on UBSan builds"); #161278 exists and is open.
- Maintainer engagement is real: vstinner (MEMBER) explained the gap - `test_perf_profiler` is skipped under sanitizer builds (`check_sanitizer(..., ub=True)`), which is why CI never caught it - and initially suggested skipping the embed perf tests; the reporter replied the fix is cheap and noted the existing `_Py_NO_SANITIZE_ADDRESS/THREAD/MEMORY` macro family it would extend.

## Limits

- The segfault was not reproduced here - it needs a UBSan (`-fsanitize=function`) CPython build, which this environment does not have. The mechanism is verified against the source, not by running it.
- The fix in gh-161294 was not reviewed or tested here; no merged resolution as of writing.
- Impact is bounded: only affects CPython built with UBSan and run with `-X perf` - a developer/CI configuration, not production CPython.

## Sources

- Issue: <https://github.com/python/cpython/issues/161288>
- perf_trampoline.c at the cited commit: <https://github.com/python/cpython/blob/7e3290d94427cdbfe0483f0a99d589b784d77c1a/Python/perf_trampoline.c>
- Linked fix PR: <https://github.com/python/cpython/pull/161294>
- Related: <https://github.com/python/cpython/issues/161278>
