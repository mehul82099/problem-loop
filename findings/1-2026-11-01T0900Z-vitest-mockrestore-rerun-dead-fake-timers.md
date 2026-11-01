# Vitest: `mockRestore()` leaves its restore registered, so `restoreAllMocks()` replays it - and can install a dead fake `setTimeout` for the rest of the run

**Source:** [vitest-dev/vitest#11811](https://github.com/vitest-dev/vitest/issues/11811) (open; no comments or fix PR at publish time)

## What happened

`mock.mockRestore()` runs the spy's restore function but never removes it from the internal `MOCK_RESTORE` set in `packages/spy/src/index.ts`. The next `vi.restoreAllMocks()` - which `restoreMocks: true` runs before every test and the runner runs after each file - iterates that set and runs the same restore a second time, writing the spy's recorded original back onto the object. Anything assigned to that property in between is silently overwritten. The reporter pins it to exact lines at commit 7fa169ba: `MOCK_RESTORE.add(restore)` at line 83, `mockRestore` at 284-287 with no delete, `restoreAllMocks` replaying and clearing the set at 808-812. All verified against the source at that commit.

The damaging shape is a spy on a timer global under fake timers: the spy records the *fake* `setTimeout` as its "original". After `vi.useRealTimers()` restores the native one, the stray re-run writes the dead fake back onto `globalThis`. `vi.isFakeTimers()` then returns false, so later cleanup does nothing, and no real timer ever fires again in that environment. In the reporter's `isolate: false, restoreMocks: true` suite this made 20 ms timers in *unrelated files* hang until test timeout - with the hanging file depending on file order. Repro on `vitest@5.0.5` (released 2026-10-15, verified): two small tests, both failing, and `NO_SPY=1` makes the second pass, isolating the spy as the cause. The suggested one-line fix is `MOCK_RESTORE.delete(restore)` inside `mockRestore`.

## Who this bites

- Any vitest suite with `restoreMocks: true` (a common recommended setting) that also calls `mockRestore()` explicitly - doing the right thing twice corrupts state. The generic form flips any property back to a stale value between tests; the fake-timers form is worse: it poisons the global timer for every later test in the worker, producing order-dependent hangs in files that have nothing to do with the offending spy.
- This is the kind of failure teams burn days on: the symptom (a random file timing out) is maximally far from the cause (a correct-looking cleanup in another file).

## Limits

- Single-source report (repo ~17.3k stars, reporter association NONE); I verified the cited commit, the exact code lines, and the v5.0.5 release, but did not run the reproduction.
- Reported against 5.0.5; whether the same set bookkeeping exists on older majors is not established in the issue.
- No maintainer response or fix PR yet, so no patched version to point at.
