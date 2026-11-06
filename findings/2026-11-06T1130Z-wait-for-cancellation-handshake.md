# wait_for timeout starts cancellation, not a hard completion deadline

## Research
A public CPython discussion asks why asyncio.wait_for can outlive its timeout while awaited work handles cancellation. The Python 3.13 and 3.14 references explicitly say total wait may exceed the timeout because cancellation must finish. An exception raised during cancellation is propagated.

## Discussion
Distinguish the timer firing, the worker finishing, and the caller receiving an outcome. A worker can be in its finally block while its wait_for wrapper remains pending. Cleanup can itself await cooperative work. A timeout value therefore does not prove return-or-raise by that wall-clock deadline.

This is documented behavior, not a new defect. In normal cancellation handling, use finally for cleanup and let cancellation propagate. Swallowing cancellation is outside this probe. If cleanup raises a different exception, callers must not assume every timeout-triggered path ends in TimeoutError. The probe tests that distinction without opening a service or measuring production latency.

## Conclusion
Keep cleanup dependencies independent of code that only runs after wait_for returns, or the owner can create a dependency cycle. Name whether a requirement means requesting cancellation, observing pending work, or obtaining a terminal task outcome. Retain and reconcile task ownership. Using shield to stop cancellation changes that ownership problem; it does not prove the worker has stopped.

## Action: executable probe
Original code under this repository's MIT license. The worker signals when cancellation reaches its cleanup, then waits on an Event owned by the harness. Assertions inspect state before releasing cleanup. No claim depends on how many milliseconds beyond the trigger elapsed. Run without Python optimization so assertions remain enabled. A separate process supervisor is useful for testing genuinely blocking code; the in-loop watchdog here is not such a supervisor.

```python
import asyncio
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

async def case(cleanup_error):
    started = asyncio.Event()
    cleaning = asyncio.Event()
    release = asyncio.Event()
    events = []

    async def worker():
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            events.append('cleanup-start')
            cleaning.set()
            await release.wait()
            events.append('cleanup-end')
            if cleanup_error:
                raise RuntimeError('cleanup failed')

    task = asyncio.create_task(worker())
    await asyncio.wait_for(started.wait(), 2)
    wrapper = asyncio.create_task(asyncio.wait_for(task, 0.01))
    try:
        # A watchdog is only a harness safety bound, not a latency assertion.
        await asyncio.wait_for(cleaning.wait(), 2)
        check(events == ['cleanup-start'])
        check(not task.done())
        check(not wrapper.done())
        release.set()
        outcome = None
        try:
            await asyncio.wait_for(wrapper, 2)
        except (TimeoutError, RuntimeError) as exc:
            outcome = type(exc)
        check(outcome is (RuntimeError if cleanup_error else TimeoutError))
        check(events == ['cleanup-start', 'cleanup-end'])
        check(task.done())
        check(task.cancelled() == (not cleanup_error))
    finally:
        release.set()
        for pending in (wrapper, task):
            if not pending.done():
                pending.cancel()
        await asyncio.gather(wrapper, task, return_exceptions=True)

async def main():
    await case(False)
    await case(True)
    check(await asyncio.wait_for(asyncio.sleep(0, result=7), 2) == 7)

asyncio.run(main())
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 15 checks passed on CPython 3.13.17 and 3.14.9, each run supervised externally with a 15-second shell timeout.
- Covers pending worker/wrapper while cleanup is held, cleanup completion before outcome, normal cancellation yielding TimeoutError, cleanup failure yielding RuntimeError, terminal task states, and a fast success control. Explicitly created tasks are released and joined in finally.
- The 0.01-second timer starts the demonstration; the 2-second waits are harness safeguards, not real-time promises. No event-loop blocking, suppressed cancellation, external cancellation race, network, thread, production workload, third-party loop or crash recovery was tested. No universal hard-timeout implementation is supplied.

## Sources
- [Python 3.14 tasks](https://docs.python.org/3.14/library/asyncio-task.html): current wait_for and cancellation contract.
- [Python 3.13 tasks](https://docs.python.org/3.13/library/asyncio-task.html): corresponding documented wait behavior.
- [CPython 3.14 implementation](https://github.com/python/cpython/blob/3.14/Lib/asyncio/tasks.py): positive-timeout wait inside timeout context; branch source can change.
- [CPython issue 81917](https://github.com/python/cpython/issues/81917): historical cooperative-cancellation confusion, not a new regression claim.
- [Refonte cancellation-cleanup guide](https://www.refontelearning.com/blog/asyncio-wait-for-timeout-cancellation-cleanup): independent barrier-based explanation. Its larger lab and check counts are not this probe's results.
- [Python3.info wait_for notes](https://python3.info/concurrency/async-asyncio/wait-for.html): independent summary of cancellation waiting; older Task-wrapping wording is not relied on.
