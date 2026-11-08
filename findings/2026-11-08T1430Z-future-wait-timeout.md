# A Future wait timeout does not stop running thread work

Date: 2026-11-08. Evidence-backed Python finding, not a new executor defect.

## Research

The Python reference separates three operations that are easy to confuse: timing out while waiting for a result, cancelling a task before it starts, and shutting down an executor. A public Python tracker report from 2011 records the same confusion and marks the behavior expected. A later community question and an independent tutorial corroborate it. These reports do not establish prevalence or a new regression.

## Discussion

For a `ThreadPoolExecutor`, `future.result(timeout=...)` bounds that wait. If it raises `TimeoutError`, the running callable can still produce effects and a later result. `future.cancel()` returns False once that call is running. `shutdown(wait=False, cancel_futures=True)` can cancel queued calls, not the already-running call.

A surrounding `with ThreadPoolExecutor(...)` introduces another wait: its context exit requests `shutdown(wait=True)`. Therefore catching a result timeout outside the with-block does not make the whole block meet that timeout. Changing to `wait=False` only avoids waiting at that shutdown call; it is not termination, rollback, or a guarantee that Python exits while the work is still pending.

## Conclusion

| Intended guarantee | Appropriate boundary | What it does not provide |
| --- | --- | --- |
| Stop waiting for this result | `result(timeout=...)` | No running-task cancellation |
| Discard work not yet started | `cancel()` or shutdown with `cancel_futures=True` | No interruption of running thread calls |
| Ask running work to stop | Application-owned signal that the worker checks | No forced interruption of an arbitrary blocking operation |
| Wait for cleanup | `shutdown(wait=True)` or context exit | No finite deadline for an unbounded task |

Bound operations inside workers using the relevant I/O API's deadlines. If work must stop cooperatively, define signal checks and cleanup behavior in that work. Do not treat the timeout as a transaction boundary. Process isolation has different termination tradeoffs and is outside this probe.

## Action: coordinated diagnostic

The following standard-library-only test holds a worker behind an Event, checks timeout and cancellation states, then releases and joins it. It deliberately permits a harmless in-memory effect after the timeout. No sleep-based duration assertion or external service is involved. Five/ten-second waits are test watchdogs, not latency promises. Original code is covered by the repository MIT license.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from concurrent.futures import ThreadPoolExecutor, CancelledError
from threading import Event
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def expect(exc, action):
    global checks
    try:
        action()
    except exc:
        checks += 1
    else:
        raise AssertionError(f'expected {exc.__name__}')

started = Event()
release = Event()
finished = Event()
queued_ran = Event()
effects = []

def work():
    started.set()
    if not release.wait(10):
        raise RuntimeError('test watchdog expired')
    effects.append('after-timeout')
    finished.set()
    return 42

pool = ThreadPoolExecutor(max_workers=1)
try:
    running = pool.submit(work)
    check(started.wait(5))
    queued = pool.submit(queued_ran.set)
    check(running.running())
    check(not running.done())
    expect(TimeoutError, lambda: running.result(timeout=0))
    check(not running.done())
    check(not running.cancelled())
    check(running.cancel() is False)
    check(not finished.is_set())
    check(effects == [])
    check(not queued.running())
    pool.shutdown(wait=False, cancel_futures=True)
    check(queued.cancelled())
    check(queued.done())
    expect(CancelledError, queued.result)
    check(not running.cancelled())
    check(running.running())
    expect(RuntimeError, lambda: pool.submit(lambda: None))
    release.set()
    check(running.result(timeout=5) == 42)
    check(finished.is_set())
    check(effects == ['after-timeout'])
    check(not queued_ran.is_set())
finally:
    release.set()
    pool.shutdown(wait=True)

# Verify context exit requests waiting, without a wall-clock assertion.
class RecordingPool(ThreadPoolExecutor):
    def shutdown(self, wait=True, *, cancel_futures=False):
        self.exit_wait = wait
        return super().shutdown(wait=wait, cancel_futures=cancel_futures)

with RecordingPool(max_workers=1) as managed:
    check(managed.submit(lambda: 'ok').result(timeout=5) == 'ok')
check(managed.exit_wait is True)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **22 checks passed on each build**. The single occupied worker makes the queued call's state deterministic. A finally-block releases and joins the worker even if a check fails. The final subclass records that context exit requests waiting; it does not measure teardown duration. Repository CI is separate.

Scope: ThreadPoolExecutor only, bounded event-controlled work, public Future API. This is not a test of arbitrary I/O interruption, process termination, production retries, or exactly-once effects. Cooperative stop latency depends on the worker's own checks and blocking operations.

## Publisher and sources

Published deliverable: this finding and its runnable probe. No automatic thread-killing technique or runtime patch is proposed. All six pages were read; current API guidance comes from the Python 3.14 reference rather than older examples.

1. [Python 3.14 concurrent.futures](https://docs.python.org/3.14/library/concurrent.futures.html), primary reference: result timeout, cancellation states, shutdown and interpreter-exit behavior.
2. [PEP 3148](https://peps.python.org/pep-3148/), design proposal: separates result waiting, cancellation and context-manager shutdown. The current reference owns later additions such as `cancel_futures`.
3. [Python tracker issue 11724](https://bugs.python.org/issue11724), historical maintainer discussion, 2011: running calls continuing after a wait timeout is expected behavior; cooperative signals suggested.
4. [CPython 3.14 Future/Executor source](https://github.com/python/cpython/blob/3.14/Lib/concurrent/futures/_base.py), primary implementation: running-state cancel refusal, result wait, and context exit's `shutdown(wait=True)`.
5. [Exiting a running ThreadPoolExecutor context](https://stackoverflow.com/questions/75310731/how-to-exit-threadpoolexecutor-with-statement-immediately-when-a-future-is-runni), community evidence: shutdown and timeout confusion. Process-killing suggestions there are not adopted here.
6. [How to Stop Running Tasks in ThreadPoolExecutor](https://superfastpython.com/threadpoolexecutor-stop-tasks/), independent tutorial: cancel does not stop a running task; an Event requires worker cooperation. It is not evidence of a universal interruption guarantee.
