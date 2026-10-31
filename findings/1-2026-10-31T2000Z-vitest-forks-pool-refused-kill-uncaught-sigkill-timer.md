# Vitest forks pool: when `kill()` is refused, the SIGKILL backstop timer crashes the run from an uncaught error - after all tests passed

**Source:** [vitest-dev/vitest#11808](https://github.com/vitest-dev/vitest/issues/11808) (open; maintainer disputing intended behavior, code path verified on `main`; reporter disclosed AI-drafted, human-reviewed writeup)

## What happened

In a Docker CI job container where `kill()` on the worker process is refused (`EACCES`), a vitest run with the default `forks` pool fails with exit code 1 **even though every test passed**. The reporter's trace shows why, and the code on `main` matches it exactly ([forksWorker.ts#L83-L103](https://github.com/vitest-dev/vitest/blob/main/packages/vitest/src/node/pools/workers/forksWorker.ts#L83-L103)):

1. `ForksPoolWorker.stop()` arms a 500 ms backstop: `const sigkillTimeout = setTimeout(() => fork.kill('SIGKILL'), SIGKILL_TIMEOUT)` (line 99).
2. It then calls `fork.kill()` (line 101). When that throws `EACCES`, execution leaves `stop()` - and `clearTimeout(sigkillTimeout)` on line 103 never runs.
3. `PoolRunner` logs "Failed to terminate forks worker". 500 ms later the orphaned timer fires, `fork.kill('SIGKILL')` is refused too, and that error is thrown from a timer callback with nothing to catch it: "Error: kill EACCES ... Emitted 'error' event". Run exits 1.

The reporter's proposed fix is minimal: clear the timer in a `finally`, and catch a refused SIGKILL inside the timer and reject `stop()` with it - the same treatment the refused SIGTERM already gets.

A vitest maintainer (AriPerkkio, MEMBER, verified) pushed back within hours: "If the environment doesn't allow terminating the worker, what is the expected output here? It's correct behavior from Vitest to throw the error." That frames the real, narrower question the issue now sits on: whether the run *should fail* is debatable, but the failure currently escapes as an unhandled exception from a stray timer - bypassing `stop()`'s own error path entirely - rather than as a controlled rejection. Same outcome, wildly different diagnosability: "all tests passed" followed by an internal `Emitted 'error' event` stack.

The reporter reproduced 3/3 runs on one CI runner image and notes a fake `ChildProcess` whose `kill()` emits `'error'` reproduces it against the current `stop()` logic.

## Who this bites

- Teams running vitest in locked-down containers (read-only PID namespaces, restricted seccomp/kill policies, some CI runner images): green test suites can still exit 1 with a stack trace that points at Node internals, not at the environment's kill restriction.
- Anyone debugging it loses time to the indirection: the visible error is the *second*, uncaught refusal from the timer, not the first, handled one.

## Limits

- The EACCES environment and the 3/3 reproduction are the reporter's; I verified the `stop()` code path, the timer/clear ordering, and the maintainer's MEMBER association on `main` (v5.0.5 release tag verified), but did not run the fake-ChildProcess repro (repo ~17k stars).
- Whether exit-1 is the *desired* behavior is explicitly unresolved - the maintainer questions it; the code defect (orphaned timer, uncaught callback) is independent of that decision.
- Only the `forks` pool path is implicated; threads pool workers use a different termination path and are unexamined here.
