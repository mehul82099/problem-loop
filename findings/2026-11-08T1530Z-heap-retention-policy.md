# Fixed heap size is not a largest-k retention policy

Date: 2026-11-08. Evidence-backed Python finding, not a new heapq defect.

## Research

The Python reference distinguishes `heappushpop` from `heapreplace`. Both preserve the size of a nonempty heap, but they do not preserve the same values. Community questions about the difference and fixed-size heaps show how a size invariant can be mistaken for a retention policy. Independent tutorials corroborate the operation order; the current reference is the API authority.

## Discussion

For a min-heap containing `[5, 8, 9]`, offering candidate `1` to `heappushpop` returns `1` and retains `[5, 8, 9]`. Calling `heapreplace` instead returns the old minimum `5` and retains `[1, 8, 9]`. An unconditional replacement lost a better value even though the heap still contains three values.

To retain the largest k values seen so far, fill the heap with `heappush` until it reaches k, then offer each new value through `heappushpop`. Alternatively, use `heapreplace` only after checking that the candidate is greater than the root. Calling `heappushpop` on an empty heap returns the candidate and leaves the heap empty; it does not fill your capacity automatically. `heapreplace` on an empty heap raises `IndexError`.

## Conclusion

| Goal | Operation or policy | Boundary |
| --- | --- | --- |
| Always evict the current minimum and admit the new value | `heapreplace` | Requires a nonempty heap; candidate can be worse |
| Keep the larger values after considering a candidate | `heappushpop` | Fill capacity first |
| Get largest k values from an iterable without custom streaming state | `heapq.nlargest` | Prefer the standard helper when it fits |
| Return values in descending order | Sort the retained heap at the boundary | Heap storage is not a fully sorted result |

This increment handles integer values, duplicates by value, and a finite input. It does not define identity or stability among equal-scoring records, arbitrary comparators, NaNs, concurrent updates, or record payload tie-breaking. For those, define the ordering contract separately. The helper validates k, not every input value.

## Action: bounded helper and exhaustive small-domain probe

The helper below retains up to k largest values and returns them descending. k=0 intentionally returns without consuming its input. Original code is covered by the repository MIT license. No network or third-party package is needed.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from heapq import heapify, heappush, heappushpop, heapreplace
from itertools import product
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def largest_k(values, k):
    """Retain up to k largest integer values; return descending values."""
    if type(k) is not int or k < 0:
        raise ValueError('k must be a nonnegative integer')
    if k == 0:
        return []  # Deliberately does not consume values.
    heap = []
    for value in values:
        if len(heap) < k:
            heappush(heap, value)
        else:
            heappushpop(heap, value)
    return sorted(heap, reverse=True)

base = [5, 8, 9]
heapify(base)
a, b = list(base), list(base)
check(heappushpop(a, 1) == 1)
check(sorted(a) == [5, 8, 9])
check(heapreplace(b, 1) == 5)
check(sorted(b) == [1, 8, 9])
check(len(a) == len(b) == 3)
for candidate in (5, 7, 20):
    h = list(base)
    removed = heappushpop(h, candidate)
    check(removed == min(base + [candidate]))
    check(sorted(h) == sorted(base + [candidate])[1:])
    check(len(h) == len(base))
empty = []
check(heappushpop(empty, 7) == 7)
check(empty == [])
try:
    heapreplace(empty, 7)
except IndexError:
    checks += 1
else:
    raise AssertionError('heapreplace accepted empty heap')
check(empty == [])
# All 364 sequences of lengths 0..5 over {-1, 0, 1}, for six k values.
for length in range(6):
    for values in product((-1, 0, 1), repeat=length):
        for k in range(6):
            result = largest_k(iter(values), k)
            check(result == sorted(values, reverse=True)[:k])
            check(len(result) == min(k, length))
for invalid in (-1, True, 1.5):
    try:
        largest_k([1, 2], invalid)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('invalid k accepted')
source = iter([1, 2])
check(largest_k(source, 0) == [])
check(next(source) == 1)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **4,391 checks passed on each build**. These include a below-minimum counterexample, equal/above-root candidates, empty-heap behavior, invalid k, zero-capacity consumption policy, and every sequence of lengths 0 through 5 over {-1, 0, 1} for k=0 through 5. That is 364 sequences and 2,184 helper cases, each checked against descending sort/slice and expected size.

This finite exhaustive domain is not a proof for all comparators or a performance benchmark. The result is an original small diagnostic/helper plus a finding, not a change to heapq. Repository CI is separate from these local executions.

## Publisher and sources

All six pages were read. Documentation describes longstanding semantics; public questions are examples of confusion, not an incident-rate estimate.

1. [Python 3.14 heapq reference](https://docs.python.org/3.14/library/heapq.html), primary documentation: push/pop and pop/push contracts, empty replacement, and `nlargest`.
2. [CPython 3.14 heapq source](https://github.com/python/cpython/blob/3.14/Lib/heapq.py), primary implementation: conditional root replacement for push/pop versus unconditional replacement. Pure Python definitions can be overridden by the C implementation; tests use the installed public API.
3. [Difference between heappushpop and heapreplace](https://stackoverflow.com/questions/33701160/python-heapq-difference-between-heappushpop-and-heapreplace), community question and examples: below-minimum candidate distinguishes behavior. Community timing explanations are not adopted as measured results.
4. [Maintain a fixed-size heap](https://stackoverflow.com/questions/30443150/maintain-a-fixed-size-heap-python), community examples: capacity handling and retention direction can be confused. Its smallest-k question is not the same as this helper's largest-k contract; old claims about max-heap API availability are not current guidance.
5. [PyMOTW heapq tutorial](https://pymotw.com/3/heapq/index.html), independent tutorial: replacement and high-level selection helpers.
6. [Real Python heapq tutorial](https://realpython.com/python-heapq-module/), independent explanation: operation order and smallest-root convention. This finding uses only the longstanding min-heap APIs on both tested versions.
