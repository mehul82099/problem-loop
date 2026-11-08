# An empty Queue is not a completion or success certificate

Date: 2026-11-08. Scope: Python queue.Queue, not asyncio.Queue or multiprocessing.Queue.

## Research

A public question reports join() still waiting after a single task_done() call at the end of a worker loop. The official contract counts unfinished tasks: put() adds one, get() removes an item from the container without acknowledging completion, and task_done() subtracts one. join() waits for that count to reach zero. Occupancy and acknowledgement are different state.

## Discussion

The distinction matters even with no concurrent producers. After the only queued item has been retrieved, empty() is true while the item is still unfinished. In real concurrent programs, empty() and qsize() also have check-then-act races. Neither should replace a completion protocol.

Acknowledgement is not proof of success either. The implementation does not bind task_done() to a particular retrieved item. A premature call can let join() return with an item still queued. Calling task_done() in finally keeps accounting balanced after processing raises, but does not record an error, retry the job or keep a failed worker alive. Choose explicitly whether a failed attempt is terminal or should be retried, and report outcomes separately.

An independent tutorial's blanket claim that join() returns immediately on an empty queue conflicts with the official unfinished-task contract and the retrieved-but-unacknowledged state below. Its later distinction between occupancy and processing is useful; the blanket shortcut and busy-wait substitution are not adopted here. An older CPython documentation issue was closed as not a bug after its reporter noticed the example joined before adding its sentinel. That is evidence to check ordering, not evidence of a current Queue defect.

## Conclusion

Use join() after the intended production phase, and pair each successfully retrieved task with exactly one acknowledgement under the chosen failure policy. Track success, failure and retry state separately. join() does not close the queue to later producers or join worker threads. On Python 3.13+, immediate shutdown can drain queued tasks and permit join() to return without processing those tasks, so it is not a success certificate either.

## Action

This original MIT-licensed diagnostic probe passed 27 checks each on CPython 3.13.17 and 3.14.9. It deliberately demonstrates premature acknowledgement misuse and immediate-shutdown discard in isolated queues. unfinished_tasks is read only as a CPython diagnostic, never as an application synchronization API. All join() calls occur after the counter is known to be zero; the probe does not measure blocking latency, test concurrent interleavings or supply a production worker pool. Run with an external timeout (for example, timeout 15 python probe.py) to bound a regression.

```python
# Original probe, MIT license (repository LICENSE).
import json
import platform
from queue import Queue, Empty, ShutDown

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def raises(kind, operation):
    try:
        operation()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

q = Queue()
check(q.empty())
check(q.unfinished_tasks == 0)  # CPython diagnostic, not coordination API.
check(q.join() is None)
q.put('job')
check(q.qsize() == 1)
check(q.unfinished_tasks == 1)
check(q.get_nowait() == 'job')
check(q.empty())
check(q.unfinished_tasks == 1)  # Removed, but not acknowledged.
raises(Empty, q.get_nowait)
q.task_done()
check(q.unfinished_tasks == 0)
check(q.join() is None)
raises(ValueError, q.task_done)

# Queue accounting cannot certify application success.
q.put('fails')
failed = []
item = q.get_nowait()
try:
    raise RuntimeError(item)
except RuntimeError:
    failed.append(item)
finally:
    q.task_done()
check(failed == ['fails'])
check(q.join() is None)
check(q.unfinished_tasks == 0)

# A premature acknowledgement fools join, even before retrieval.
q.put('still waiting')
q.task_done()  # Intentional misuse for the probe.
check(q.join() is None)
check(not q.empty())
check(q.get_nowait() == 'still waiting')
raises(ValueError, q.task_done)

# join is not a permanent seal against future producers.
check(q.join() is None)
q.put('later')
check(q.unfinished_tasks == 1)
check(q.get_nowait() == 'later')
q.task_done()
check(q.join() is None)

# Immediate shutdown discards queued work, not successful processing.
r = Queue()
r.put('discarded')
r.shutdown(immediate=True)
check(r.empty())
check(r.unfinished_tasks == 0)
check(r.join() is None)
raises(ShutDown, r.get_nowait)

print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and reproducible probe. This is documented longstanding accounting behavior, not a newly discovered bug, performance claim or upstream fix. No network activity, background threads, private data or third-party code is needed by the probe.

## Sources

All six pages fetched during this cycle:

- Official Python 3.14 queue reference, API contract and shutdown caveat: https://docs.python.org/3.14/library/queue.html
- CPython 3.14 source, counter transitions and join loop: https://github.com/python/cpython/blob/3.14/Lib/queue.py
- Community report, one acknowledgement for multiple dequeued items: https://stackoverflow.com/questions/56342405/why-the-queue-still-joining-after-i-called-task-done
- Independent tutorial, acknowledgement/finally advice and contradictory empty-queue shortcut assessed above: https://superfastpython.com/thread-queue-task-done-join/
- Historical issue, reporter correction and not-a-bug resolution: https://github.com/python/cpython/issues/81684
- Community explanation of retrieval versus completion: https://stackoverflow.com/questions/49637086/python-what-is-queue-task-done-used-for
