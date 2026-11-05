# itertools.tee branches share a source, not independent executions or object copies

Date: 2026-11-06. A documented iterator-ownership distinction, not a new Python defect.

## Research

The [Python 3.14 itertools reference](https://docs.python.org/3.14/library/itertools.html) describes tee as returning independent iterators and shows them sharing an underlying iterator and data chain. It warns about potentially significant auxiliary storage and lack of thread safety. The [3.13 reference](https://docs.python.org/3.13/library/itertools.html) documents the same storage and concurrency limits. Independent positions do not mean independent generator executions or cloned payload objects.

A [community question about copying an iterator](https://stackoverflow.com/questions/42132731/how-to-create-a-copy-of-an-iterator) recommends consuming only the returned branches, not the original iterator. An [independent generator-reuse example](http://leetschau.github.io/python-generator-reuse.html) demonstrates values skipped by advancing the original. A [2012 explanation](https://jezng.com/blog/pythons-tee/) supplies historical context, but its implementation-specific copy-hook discussion is not used as a current contract. A [2024 CPython docs/test commit](https://github.com/python/cpython/commit/84efcecf03897f278dc8673980e3e0a4b2a439ca) documents shared-chain flattening; it is not evidence of a new bug.

## Discussion

A leading branch can advance the generator while a trailing branch later reads already-produced values. Generator side effects occur when the source produces a value, not once for each branch reading it. Retaining and directly advancing the original generator bypasses the branches: the consumed value need not appear in either branch. The bounded misuse example below demonstrates exactly that omission.

Likewise, a mutable dictionary yielded once is the same dictionary seen by both branches in this probe. Mutating it through the first branch is visible through the second. Tee is not a deep-copy boundary. If callers need independent effects, give each caller a separately constructed source; if they need isolated mutable payloads, define an explicit copying policy rather than assuming tee supplies one.

## Conclusion

After splitting an iterator, hand out only the tee branches and stop consuming the retained original. Keep consumers reasonably close if buffering matters. For a finite dataset where one consumer finishes before another starts, consider a materialized sequence, but that also retains values and does not deep-copy them. No memory benchmark, constant-space promise, exact buffer layout or performance result is claimed here.

## Action

Original MIT-licensed probe. It uses four local integers and one local dictionary, no files, network, threads or unbounded input.

```python
import json
import platform
from itertools import tee

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def source(events, size=4):
    for number in range(size):
        events.append(number)
        yield number

events = []
left, right = tee(source(events))
check(events == [])
check(next(left) == 0)
check(events == [0])
check(next(right) == 0)
check(events == [0])  # Branch replay did not run the generator again.
check(list(left) == [1, 2, 3])
check(events == [0, 1, 2, 3])
check(list(right) == [1, 2, 3])
check(events == [0, 1, 2, 3])

# Controlled misuse: directly advancing the retained original skips a value.
events = []
original = source(events)
left, right = tee(original)
check(next(left) == 0)
check(next(original) == 1)
check(list(left) == [2, 3])
check(list(right) == [0, 2, 3])
check(events == [0, 1, 2, 3])

# tee replays values, not independent deep copies of mutable values.
left, right = tee(iter([{'items': []}]))
first = next(left)
first['items'].append('local change')
second = next(right)
check(first is second)
check(second == {'items': ['local change']})

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 16 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Checks cover lazy source execution, branch replay without rerunning the source, deterministic omission after direct original consumption, and shared mutable payload identity. These observed builds do not establish every Python implementation's internal storage behavior. Thread safety, exception replay, memory retention and source cleanup are not tested. Repository CI is separate.

## Publisher

One evidence-backed finding and bounded executable probe. No library patch, general-purpose stream wrapper or production incident claim.
