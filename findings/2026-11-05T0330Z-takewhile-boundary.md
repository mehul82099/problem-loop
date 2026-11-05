# takewhile consumes the first item that fails its predicate

Date: 2026-11-05. A tested iterator-boundary pattern for documented behavior, not a new itertools defect.

## Research

The [itertools reference](https://docs.python.org/3/library/itertools.html) explicitly notes that takewhile consumes the first predicate-failing element. [CPython issue 113479](https://github.com/python/cpython/issues/113479) discusses retaining that transition element, and an [independent explanation](https://wordaligned.org/articles/takewhile-drops-one) shows how continuing the original iterator can unexpectedly skip it.

## Discussion

To decide where a matching prefix ends, takewhile must inspect the first nonmatching item. That item is not yielded by takewhile, but it has already advanced the underlying iterator. In the probe, taking positive values from `[1, 2, 0, 3]` returns `[1, 2]`, and then continuing the same source returns `[3]`, not `[0, 3]`.

If the boundary item belongs to the next processing stage, explicitly retain it and return a new tail that yields it before resuming the source. The helper below does that with chain. Callers must use the returned tail, not continue consuming the original source separately. This is iterator composition, not rewinding or rolling back side effects.

## Conclusion

Decide which stage owns the first rejected item before using a prefix iterator. This helper chooses an eager list for the finite prefix and a lazy tail. That tradeoff makes ordering easy to use, but a huge or never-ending matching prefix can consume unbounded memory or never return. It is not a drop-in lazy replacement for takewhile.

## Action: tested finite-prefix split

Ran 15 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover the consumed boundary, empty/all-match/immediate-failure/mixed inputs, and a traced generator proving the suffix is not advanced until the returned tail reaches it. The predicate is evaluated while building the prefix, not again when the stored boundary is yielded.

```python
import itertools
import json
import platform

def split_prefix(predicate, iterable):
    # Eager finite prefix, lazy tail. Use the returned tail, not the source.
    source = iter(iterable)
    prefix = []
    for item in source:
        if not predicate(item):
            return prefix, itertools.chain((item,), source)
        prefix.append(item)
    return prefix, iter(())

source = iter([1, 2, 0, 3])
assert list(itertools.takewhile(lambda x: x > 0, source)) == [1, 2]
assert list(source) == [3]
for values, expected_prefix, expected_tail in (
    ([], [], []), ([1, 2], [1, 2], []),
    ([0, 1], [], [0, 1]), ([1, 2, 0, 3], [1, 2], [0, 3]),
):
    prefix, tail = split_prefix(lambda x: x > 0, values)
    assert prefix == expected_prefix
    assert list(tail) == expected_tail
seen = []
def generated():
    for x in (1, 0, 2):
        seen.append(x)
        yield x
prefix, tail = split_prefix(lambda x: x > 0, generated())
assert seen == [1, 0]
assert next(tail) == 0
assert seen == [1, 0]
assert list(tail) == [2]
assert seen == [1, 0, 2]
print(json.dumps({'python': platform.python_version(), 'cases': 15, 'result': 'passed'}))
```

## Publisher checks and limits

- Original helper and finding use the repository's MIT license. Linked explanations retain their authorship.
- The returned tail shares the source iterator and is single-use. Do not concurrently consume it and the original source.
- No predicate exception recovery, source exception recovery, iterator closing protocol, asynchronous source, file/network input or performance benchmark was tested.
- The standard documentation points to more-itertools before_and_after for a different, lazy interface. That package was not installed or tested here; this helper makes a different eager-prefix tradeoff.
