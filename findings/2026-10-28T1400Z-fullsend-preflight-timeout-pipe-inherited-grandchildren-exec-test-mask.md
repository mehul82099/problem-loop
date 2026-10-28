# The 30-second timeout that isn't: how `exec sleep` in tests hides a process-group kill gap

- Source issue: https://github.com/fullsend-ai/fullsend/issues/8885 (open; opened 2026-10-28)
- Project: fullsend-ai/fullsend (~165 stars; autonomous-agentic engineering org)
- Checked: 2026-10-28 14:10 UTC

## Problem
`runPreflightCommand` (Go, `internal/cli/run.go`, on open PR #8769 head `91105635e`) guards a preflight shell command with a 30-second `exec.CommandContext` timeout. But `CommandContext` kills only the `sh -c` child at the deadline, while `cmd.CombinedOutput()` keeps blocking on the stdout/stderr pipes, which any non-`exec` grandchild inherits. So `preflight_check: 'sleep 600; echo done'` holds the pipes open and delays the "timed out after 30s" diagnostic by up to 10 minutes - the timeout doesn't bound wall-clock time. Verified directly in the PR-head source: `CommandContext` + `CombinedOutput` with no `Setpgid` and no `WaitDelay`. The existing timeout tests use `exec sleep 5`, and `exec` replaces the shell process entirely, so the context kill lands directly on `sleep` and the test passes - masking the exact gap it should exercise. The suggested fix is the standard pair: start the child in its own process group (`SysProcAttr{Setpgid: true}`) and kill the whole group on cancel, plus set `cmd.WaitDelay` so pipe drain is bounded.

## Why it is interesting
- This is one of Go's most re-encountered footguns, and here it is caught in the act inside a brand-new codebase: `exec.CommandContext` feels like a complete timeout, but it composes two independent mechanisms (process kill, pipe drain) and bounds neither reliably. Anyone writing "run a command with a timeout" in Go should recognize the shape.
- The test-masking detail is the real lesson. `exec sleep 5` isn't a typo - it's the natural way to write a sleep test, and it accidentally makes the shell process *be* the sleep process, which is the only case where the naive kill works. The suite green-passes a gap it was meant to catch. Code that kills `sh` but waits on pipes only ever fails when a grandchild doesn't `exec`, which is exactly the case nobody writes in tests.
- The same helper is shared by two call paths (new top-level `preflight_check` and pre-existing `validation_loop.preflight_check`), so the gap is pre-existing and now consolidated into one remediation site - a good argument for fixing at the helper rather than at either caller.
- The repo's own triage bot correctly noted the code exists only on the open PR, so the fix belongs on that branch - worth crediting as automated tooling output, not maintainer sign-off.

## Honest limits
- Filed hours ago; no human maintainer response at check time (triage comments are from the project's automation, attributed as such).
- The repo is a young, high-velocity agentic-engineering project (2,000+ open issues since March 2026); the issue author is a human account, but the codebase's AI-heavy provenance is context, not endorsement.
- Bug verified by reading the named file at the named commit, not by executing the repro.
- Code lives on an unmerged PR; the bug may never reach `main`, and the issue state may have changed since 14:10 UTC.
