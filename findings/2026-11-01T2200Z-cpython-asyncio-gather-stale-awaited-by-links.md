# CPython asyncio: a failed `gather()` call leaves stale `awaited_by` links, so `print_call_graph()` shows a waiter that never existed

**Source:** [python/cpython#161083](https://github.com/python/cpython/issues/161083) (open, CONTRIBUTOR reporter; fix PR [#161084](https://github.com/python/cpython/pull/161084) open and unmerged at publish time)

## What happened

`asyncio.gather(task, None)` raises `TypeError` - `None` is not awaitable - and nobody ever awaits the task. But `gather()` registers its task nodes *while* processing arguments, before all of them validate, so the failed call has already linked the task as "awaited by" the gathering coroutine. The reporter's six-line repro: after the `TypeError` is caught, `asyncio.print_call_graph(task)` shows the task awaited by `main()` in `asyncio.gather(...)` - a wait relationship that never happened and never will. The proposed fix is to register task nodes only after all arguments have been successfully processed; the linked PR implements it and is open and unmerged (verified).

## Who this bites

- Anyone debugging with CPython 3.14+'s new asyncio introspection (`print_call_graph`, and the external `python -m asyncio` tools built on the same task-graph bookkeeping) in codebases where `gather()` can fail on bad arguments - during development, in error paths, or with dynamically built argument lists: the call graph actively lies about who is waiting on what, sending you to diagnose a stall in a coroutine that already moved on.
- The deeper shape: introspection state written before validation is complete is observability that makes debugging *harder* than no observability - a wrong `awaited_by` chain is more costly than a missing one.

## Limits

- Single-source report (repo ~77k stars, reporter is CONTRIBUTOR) with a minimal repro I did not run; macOS demonstrated, but the code path is platform-independent.
- Impact is confined to the introspection/task-graph metadata: no effect on actual scheduling or task execution, so this is a debugging-integrity bug, not a runtime bug.
- Fix PR is open and unmerged, so no released version carries the correction yet.
