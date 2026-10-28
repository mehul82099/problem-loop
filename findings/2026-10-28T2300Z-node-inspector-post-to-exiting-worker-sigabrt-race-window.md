# The debugger that kills the debuggee: Node's inspector aborts the process posting to a Worker that's mid-exit

- Source issue: https://github.com/nodejs/node/issues/67079 (open, no comments; opened 2026-10-28)
- Project: nodejs/node (~123k stars)
- Checked: 2026-10-28 23:45 UTC

## Problem
When a Node Worker opens `new inspector.Session().connectToMainThread()` and exits while the main thread still has something to post back (a protocol reply, an event, or the delete message sent when the session's main-thread side is destroyed), the whole process can die with SIGABRT and *no error message*. The reporter pinned the race window precisely in `src/inspector/main_thread_interface.cc`: the main thread posts to the Worker's handle after the Worker's `MainThreadInterface` use count reaches zero but before its destructor resets the handle - a gap measured in instructions, which is why there is no deterministic JS reproduction. The stack tells the story: `ThreadSafeDelegate::SendMessageToFrontend` -> `MainThreadInterface::Post` -> abort. The design intent is clear from the code itself: `Post` returns false once the handle is reset, and the destructor posts unconditionally with a comment noting a disappearing thread may cause a *memory leak* - i.e., tolerate, never crash. Node's own test for this says "Do not crash" and has flaked in CI with exit code -6 and no output, previously closed as a duplicate of another flaky-test issue. Affects v24.21.0 through current `main`; code unchanged in v26.

## Why it is interesting
- Tooling must never be the fault. The inspector exists to observe a process; here observing is what kills it - and silently, with no Node-level error, so operators see a vanished process and no explanation. Monitoring and debugging infrastructure carries a higher reliability bar than the code it watches, because it's the thing you reach for when everything else is already broken.
- The race is the classic almost-thread-safe pattern: refcount hits zero, but teardown isn't atomic, and the window between "no users left" and "handle invalidated" accepts posts. Everything is correct on both sides of the window; only the gap crashes. These bugs survive for years precisely because they're un-reproducible on demand - this one surfaced twice in CI and got filed away as flake.
- The flake-to-bug pipeline matters. CI crashes with no output were previously closed as duplicates of a generic flaky issue (#54804 -> #40611). Every "CI flake, ignored" is a real bug that didn't get a detective; this report is what happens when one shows up with a gdb core, source-line refs, and the exact interleaving.
- Also a nice case of self-documenting intent: the fix direction is written into the code's own comments ("Disappearing thread may cause a memory leak") - tolerate the loss; a leak is recoverable, an abort is not.

## Honest limits
- No maintainer response at check time (~15 hours after filing).
- No deterministic reproduction; root-cause window is reporter analysis from a core dump and code reading, not yet confirmed by the project.
- Frequency is genuinely rare; impact is a crashed process when it does hit.
- Whether the prior CI flakes are the same bug is plausible but unproven.
