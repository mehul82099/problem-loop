# Closing someone else's handle numbers: uv's Windows trampoline kills its own child by coincidence

- Source issue: https://github.com/astral-sh/uv/issues/22966 (open; opened 2026-10-28)
- Project: astral-sh/uv (~91k stars)
- Checked: 2026-10-28 06:15 UTC

## Problem
When a uv venv's `python.exe` (the trampoline) is launched through the C runtime's spawn family - Python's `os.spawnv(os.P_WAIT, ...)` - it sometimes returns before the Python it launched has run: either exit 1 with "failed to get exit code of child process (os error 6)", or exit 0 with the child never having executed. CPython's own venv launcher and the base interpreter never fail under identical conditions (reporter's table: uv lost 0-15 children per 200 spawns across runs, the others lost 0 every time). Cause, per the reporter's source reading: the trampoline's `close_handles` walks the parent's C-runtime descriptor table (lpReserved2) and calls `CloseHandle` on every value - but handle values are process-local. Those numbers are meaningful in the parent; in the trampoline they can coincide with the trampoline's OWN freshly opened handles - the child process handle or the job-object handle - because Windows recycles handle values. Close your own child handle and you can no longer wait on it (os error 6); close the job handle and the child dies silently. Whether a run loses children depends on where handle values happen to land, which is why it is flaky.

## Why it is interesting
- A textbook process-locality violation, and a rare chance to see one in the wild with numbers attached. The trampoline treated integers from another process's address space as its own resources. Most of the time the values point nowhere (harmless warning spam: "Failed to close child file descriptors at N"); sometimes they point at the exact two handles the trampoline cannot afford to lose. Randomness by handle-table layout is the worst kind of flaky: unreproducible on demand, devastating in aggregate.
- It explains a very modern symptom: flaky CI. The reporter first saw it as a flaky pytest-xdist test on GitHub Actions Windows runners - a spawn that should be deterministic returning before the child ran. Anyone whose "windows CI is just flaky sometimes" involves os.spawn under a uv venv now has a mechanism to check.
- The intent was hygiene. close_handles exists to stop the child from inheriting stray descriptors - a good instinct (CPython's launcher closes nothing and prints nothing). But hygiene implemented by closing every number in someone else's table is exactly how you become the bug you were preventing.
- Report quality: a runnable repro script with pipes/spawns knobs, a five-run comparison table against two control binaries, the original CI failure log, and a line-level cause in bounce.rs. A maintainer can confirm by reading one function.

## Honest limits
- Single reporter, no maintainer response at check time (issue is ~40 minutes old at check).
- Root cause is the reporter's source reading of bounce.rs; plausible and specific, not confirmed by Astral.
- Windows + CRT-spawn entry only; normal CreateProcess launches and other platforms are unaffected per the report.
- Issue state may have changed since 06:15 UTC.
