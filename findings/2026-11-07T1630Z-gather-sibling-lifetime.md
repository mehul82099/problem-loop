# A failed gather is done; its siblings may not be

## Research
A public asyncio issue describes a keepalive task and a connection reader that should stop together, but do not when one fails inside `gather`. A separate public question shows the tempting cleanup pattern: catch the first failure and call `batch.cancel()`. Python 3.14 documents why that can be too late. Default `gather` propagates the first raised exception without cancelling the other submitted awaitables; once the aggregate is done, cancelling it does not cancel those children.

## Discussion
The aggregate's terminal state and the children's terminal states are different facts. Catching the error does not establish that sibling work stopped, that its cleanup finished, or that external side effects were undone. Conversely, a short program that exits `asyncio.run` immediately after the exception can make the sibling appear to stop because of runner shutdown. That is a different owner ending the work, not gather's first-exception policy.

This is longstanding documented behavior, not a newly discovered CPython defect. It is distinct from the repository's earlier invalid-argument awaited-by metadata finding and wait_for cancellation-handshake probe.

## Conclusion
Choose the lifetime policy explicitly:

| Intended policy | Approach | Important boundary |
| --- | --- | --- |
| Independent outcomes, wait for all | `gather(..., return_exceptions=True)` | Inspect each outcome; errors become result entries. |
| Related work should fail together | Consider `TaskGroup` | Its documented failure policy cancels remaining tasks and waits; exception handling differs. |
| Keep an existing gather design with owned tasks | Retain task handles, request cancellation on unfinished children, then await their terminal outcomes | Only cancel work this scope owns. Cancellation is cooperative, not rollback. |

Do not substitute `batch.cancel()` after first-error propagation for child cleanup. Do not cancel every task in the loop to fix an ownership problem. TaskGroup is a documented option here, not part of the executable comparison below.

## Action: deterministic probe
Original code under this repository's MIT license. Events hold sibling work until the harness either releases or cancels it. No sleep duration is used to infer task state. Run without `-O` so assertions remain active.

```python
import asyncio
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

async def case(mode):
    started = asyncio.Event()
    release = asyncio.Event()
    failed = asyncio.Event()
    events = []

    async def sibling():
        started.set()
        try:
            await release.wait()
            events.append('work')
            return 7
        finally:
            events.append('cleanup')

    async def failure():
        await started.wait()
        failed.set()
        raise ValueError('expected')

    tasks = [asyncio.create_task(sibling()), asyncio.create_task(failure())]
    batch = asyncio.gather(*tasks, return_exceptions=(mode == 'collect'))
    try:
        if mode == 'collect':
            await asyncio.wait_for(failed.wait(), 2)
            check(not batch.done())
            check(not tasks[0].done())
            check(events == [])
            release.set()
            results = await asyncio.wait_for(batch, 2)
            check(isinstance(results, list))
            check(results[0] == 7)
            check(isinstance(results[1], ValueError))
            check(events == ['work', 'cleanup'])
        else:
            caught = False
            try:
                await asyncio.wait_for(batch, 2)
            except ValueError:
                caught = True
            check(caught)
            check(batch.done())
            check(not batch.cancelled())
            check(not tasks[0].done())
            check(batch.cancel() is False)
            check(not tasks[0].done())
            check(events == [])
            if mode == 'release':
                release.set()
                check(await asyncio.wait_for(tasks[0], 2) == 7)
                check(events == ['work', 'cleanup'])
            else:
                tasks[0].cancel()
                results = await asyncio.gather(*tasks, return_exceptions=True)
                check(isinstance(results[0], asyncio.CancelledError))
                check(isinstance(results[1], ValueError))
                check(events == ['cleanup'])
        check(all(task.done() for task in tasks))
    finally:
        release.set()
        for task in tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        await asyncio.gather(batch, return_exceptions=True)

async def main():
    for mode in ('release', 'cancel', 'collect'):
        await case(mode)

asyncio.run(main())
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 29 checks passed on CPython 3.13.17 and 3.14.9, each under an external 15-second process timeout.
- The default-error cases verify the aggregate is done, late cancel returns false, and the sibling remains pending. Releasing it produces its result and cleanup; explicitly cancelling it produces cancellation and cleanup without the held work.
- The collection case verifies the aggregate remains pending while the sibling is held, then returns a list in input order containing its value and the exception, even though the second input failed first. A tutorial below incorrectly calls this return value a tuple; the official contract and both tested builds return a list.
- Every explicitly created task is joined in finally. Two-second in-loop watchdogs bound harness waits, not application latency. Repeated external cancellation during cleanup, cancellation suppression, TaskGroup, third-party event loops, real I/O, production impact and remote rollback are not tested. This is a bounded demonstration, not a reusable cancellation wrapper.

## Sources
- [Python 3.14 task documentation](https://docs.python.org/3.14/library/asyncio-task.html): gather exception, cancellation, result ordering, TaskGroup and task cancellation contracts.
- [CPython 3.14 tasks implementation](https://github.com/python/cpython/blob/3.14/Lib/asyncio/tasks.py): completed gathering future rejects cancellation; branch source can change.
- [Historical asyncio issue 238](https://github.com/python/asyncio/issues/238): original keepalive/reader lifetime problem and discussion, not evidence of a current regression.
- [Public cancellation question](https://stackoverflow.com/questions/59073556/how-to-cancel-all-remaining-tasks-in-gather-if-one-fails): late aggregate cancellation pitfall and explicit-child approaches. Community examples are not copied as a general wrapper.
- [Public runner-lifetime question](https://stackoverflow.com/questions/79038753/coroutines-are-stopped-in-asyncio-gatheraws-return-exceptions-false-when-exc): confusion between gather behavior and ending the runner.
- [Independent gather tutorial](https://python-tutorials.in/python-asyncio-gather/): corroborates first-error propagation, but its tuple claim is contradicted by the official documentation and this probe.
