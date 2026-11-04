# Equal heap priorities need a tie-breaker before non-comparable payloads

Date: 2026-11-05. A tested priority-queue pattern for documented behavior, not a new heapq defect.

## Research

The [heapq priority-queue notes](https://docs.python.org/3/library/heapq.html) explain that `(priority, task)` comparison can fail when equal priorities lead to tasks without an ordering. They recommend a unique entry count before the task, both to avoid payload comparison and to preserve insertion order within equal priorities. Public examples report this with [dictionary payloads](https://stackoverflow.com/questions/42985030/inserting-dictionary-to-heap-python) and [tied priorities](https://stackoverflow.com/questions/56998340/heapq-cant-handle-tuples-having-same-priority-if-the-item-is-not-comparable).

## Discussion

Tuples compare later fields when earlier fields tie. Two distinct dictionaries therefore reveal a problem that different-priority tests can hide. Giving the payload an arbitrary comparison method changes the payload's semantics to work around a queue representation problem.

Instead, store `(priority, unique_sequence, payload)`. Keep one increasing sequence for the lifetime of a queue; do not restart it while old entries remain. A unique second field settles ties before payload ordering is considered. This example deliberately restricts priorities to built-in integers, excluding bool, floats and NaN rather than promising an order for arbitrary values.

## Conclusion

Make tie policy explicit. This min-queue returns smaller integer priorities first and uses insertion order only within equal priorities. It is a small serial container example, not a concurrent scheduler, durable queue, update/delete API or fairness guarantee across different priorities.

## Action: tested stable min-queue

Ran 12 cases on each of CPython **3.13.17** and **3.14.9**, Linux x86_64. They cover the unprotected failure, distinct payload identities, mixed and tied priorities, empty pop, invalid priority rejection before insertion, and negative-priority ties. The failed demonstration heap is discarded; no rollback guarantee is inferred from a comparison exception.

```python
import heapq
import itertools
import json
import platform

class StableMinQueue:
    # Integer priorities only in this example; no concurrency contract.
    def __init__(self):
        self._heap = []
        self._sequence = itertools.count()

    def push(self, priority, payload):
        if type(priority) is not int:
            raise TypeError('priority must be an int')
        heapq.heappush(self._heap, (priority, next(self._sequence), payload))

    def pop(self):
        return heapq.heappop(self._heap)[2]

bad = []
heapq.heappush(bad, (1, {'name': 'first'}))
try:
    heapq.heappush(bad, (1, {'name': 'second'}))
except TypeError:
    pass
else:
    raise AssertionError('dictionary ordering unexpectedly accepted')
# Discard bad: this example makes no exception-rollback guarantee.
q = StableMinQueue()
a, b, c = {'name': 'a'}, {'name': 'b'}, {'name': 'c'}
q.push(2, a)
q.push(1, b)
q.push(1, c)
assert q.pop() is b
assert q.pop() is c
assert q.pop() is a
try:
    q.pop()
except IndexError:
    pass
else:
    raise AssertionError('empty queue accepted')
for invalid in (True, 1.0, float('nan'), '1', None):
    try:
        q.push(invalid, {})
    except TypeError:
        pass
    else:
        raise AssertionError('invalid priority accepted')
assert len(q._heap) == 0
for value in (a, b, c):
    q.push(-1, value)
assert [q.pop(), q.pop(), q.pop()] == [a, b, c]
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original wrapper and finding are under the repository's MIT license. Linked discussions retain their authorship; the entry-count approach is documented in the standard library.
- Do not mix raw entries or change queued priorities in place. The wrapper exposes only push and pop and does not support reprioritization.
- Payloads are returned by reference, not copied. The queue does not protect their contents from callers.
- No concurrent producers, persistence, cancellation, starvation test, memory limit or performance benchmark was used. Invalid priority tests do not prove transactional behavior for arbitrary failures such as allocation errors.
