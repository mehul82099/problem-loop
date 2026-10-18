# CPython 3.15 sampling profiler: CPU samples can land on the wrong thread state (cpython#159312)

- Source: https://github.com/python/cpython/issues/159312 "profiling.sampling CPU mode may attribute on-CPU samples to detached tstates when sharing native_thread_id" (open, labels type-bug, extension-modules, topic-profiling; opened 2026-10-13 by superajun-wsj; 15 comments when read)
- Linked pull request, state checked through the GitHub API on 2026-10-18: https://github.com/python/cpython/pull/159328 "gh-159312: Resolve CPU attribution from collected stacks" (open, by pablogsal, opened 2026-10-13)
- A related pull request a commenter pointed to: https://github.com/python/cpython/pull/159259 "gh-159194: Fix `sys.remote_exec()` with a subinterpreter" (open)
- Documentation: https://docs.python.org/3/library/profiling.sampling.html ("Added in version 3.15", the module is called Tachyon). The newest CPython tag the API listed was v3.15.0.

## What the module is
`profiling.sampling` is the new statistical profiler in Python 3.15. It takes periodic snapshots of a running program's call stacks from outside the process. Its "CPU mode" is meant to count only samples where a thread was actually running on a CPU.

## The report
The reporter wrote a small test: a C extension that, on one operating-system thread, switches from one Python "thread state" to a second one in the same interpreter, so there are two Python stacks for one OS thread. The first stack is suspended in `funB`. The second runs a busy loop in `funD`. He says CPU mode attributes about half of the samples to the suspended `funB` stack, though only `funD` does the work. He attached the code, a screenshot of the result and the profiler's flamegraph, which I did not open. He says he has not seen this in production and that the test came from reading how the profiler rebuilds stacks from a thread state, while looking at extending it to mixed Python and native stacks.

## What maintainers and contributors said (attributed)
- maurycy (CONTRIBUTOR) suggested checking `tstate_status.bound_gilstate` before marking a sample as on-CPU.
- pablogsal (marked MEMBER) asked about the real use case for two thread states on one OS thread. After the reporter said it came from a targeted experiment, he wrote that he does not see it as a practical problem, knows of no real software using this pattern, and that py-spy and Austin have the same issue. He said they would keep looking for a cheap fix and that he is not willing to add an expensive check for this case. He later said he is open to a small interpreter change if it keeps the ABI and keeps extra work off the normal call path.
- liuzhijie-0614 (CONTRIBUTOR) noted a hard case: filtering on the bound flag alone could miss CPU samples when native code runs on behalf of the first stack after the second one is unbound, while falling back to all unbound stacks could double-count. He sketched an "owner per OS thread" idea needing interpreter changes. pablogsal replied that he explored it too and worried about work on every eval loop entry and exit.
- maurycy and liuzhijie-0614 observed that the thread id alone cannot uniquely identify a thread state, similar to the discussion in pull request 159259.
- Pull request 159328 by pablogsal, according to its description, prefers a bound, non-empty stack from the data already collected, keeps existing attribution when none is found, and only runs a local filter on samples that contain an unbound stack, with no extra remote reads. I read only its description, not the diff or review.

## What this shows and does not show
- It shows a corner case in the new profiler, acknowledged as real by maintainers but judged rare, with a possible fix under review.
- It does not show how common the case is in practice. Nobody in the thread reports hitting it outside the test.
- It does not show that the pull request fixes the case, and the thread does not say whether it will land for 3.15.x.

## Honest limits
- I did not build or run the reproducer, or the profiler.
- I did not open the attached flamegraph or zip.
- I did not read the pull request's code.
- The pull request was opened on 2026-10-13 before some comments in which pablogsal talks about still looking for a fix. I did not work out how those fit together.
