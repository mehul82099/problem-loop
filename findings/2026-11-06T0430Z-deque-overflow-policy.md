# A full bounded deque evicts on append but rejects insert

Date: 2026-11-06. A documented operation-specific capacity policy, not a new deque defect.

## Research

The [Python 3.14 collections reference](https://docs.python.org/3.14/library/collections.html) documents opposite-end eviction for appends to bounded deques, but says insert raises IndexError if it would exceed maxlen. It also explains that extendleft reverses input order by repeatedly appending on the left. The [queue reference](https://docs.python.org/3.14/library/queue.html) documents a different capacity contract for synchronized queues, with blocking and Full errors rather than silent history eviction.

[Real Python's deque guide](https://realpython.com/python-deque/) illustrates bounded histories. An [independent insertion reference](https://pythontic.com/containers/deque/insert) and a [sliding-window guide](https://nalar.dev/practical-queues-and-sliding-windows-with-python-deque/) call out the insert exception. The [historical CPython discussion](https://github.com/python/cpython/issues/70382) records why full-deque insertion policy needed explicit treatment. This finding describes the current documented behavior, not the old behavior shown in that thread.

## Discussion

A maximum length does not imply one universal overflow policy. append and appendleft admit the new item and discard from the opposite end when full. insert does not make room that way: in this probe it raises without changing the deque, including at index zero and an index past the right end. An application replacing endpoint appends with insert can therefore change failure behavior even if the apparent insertion position matches.

Extend operations can discard multiple old entries as they consume input. extendleft also reverses the supplied order. The same three-item starting history becomes different data depending on which end and operation are selected.

## Conclusion

Use a bounded deque when loss of opposite-end history is intended. Do not treat it as a work queue that refuses or waits for capacity without dropping items. If capacity must block producers or return a Full error, choose a suitable queue API and concurrency policy. Checking length and then appending is not a synchronization guarantee. This finding supplies no concurrent wrapper or durable queue.

## Action

Original MIT-licensed probe using only tiny local integer deques. It compares append, appendleft, full insert at several indices, insert with room, extend and extendleft. No files, threads, timing or memory measurements.

```python
import json
import platform
from collections import deque

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

right = deque([1, 2, 3], maxlen=3)
check(right.append(4) is None)
check(list(right) == [2, 3, 4])
check(right.maxlen == 3)
left = deque([1, 2, 3], maxlen=3)
check(left.appendleft(0) is None)
check(list(left) == [0, 1, 2])

for index in (0, 1, 3, 99, -1):
    items = deque([1, 2, 3], maxlen=3)
    rejected = False
    try:
        items.insert(index, 9)
    except IndexError:
        rejected = True
    check(rejected)
    check(list(items) == [1, 2, 3])

items = deque([1, 2], maxlen=3)
items.insert(1, 9)
check(list(items) == [1, 9, 2])
items = deque([1, 2, 3], maxlen=3)
items.extend([4, 5])
check(list(items) == [3, 4, 5])
items = deque([1, 2, 3], maxlen=3)
items.extendleft([4, 5])
check(list(items) == [5, 4, 1])
check(len(items) == items.maxlen)

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 19 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Full insert rejection is checked alongside unchanged contents for five indices. Zero capacity, custom objects with finalizers, iterator failures, concurrency and queue blocking behavior are not tested. Repository CI is separate.

## Publisher

One evidence-backed finding and bounded executable probe. No container replacement or production queue changes.
