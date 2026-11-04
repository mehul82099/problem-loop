# lru_cache reuses return objects; fresh mutable results need an outer boundary

Date: 2026-11-05. A tested aliasing pattern for documented cache behavior, not a new cache defect.

## Research

The [functools reference](https://docs.python.org/3/library/functools.html) says the cache retains references to arguments and return values and is unsuitable when each call must create a distinct mutable object. [Python issue 35300](https://bugs.python.org/issue35300) reports a returned list being changed by its caller and records the documentation response. A [developer question](https://stackoverflow.com/questions/67061210/is-there-way-to-work-with-lru-cache-while-returning-mutable-objects-without-side) describes the same concern with mutable results.

## Discussion

A cache hit is reuse, not a fresh execution or automatic copy. If the cached function returns a list, later callers may receive the very list an earlier caller changed. Decorating a factory changes its object-ownership contract even if the original computation is deterministic.

For the simple integer list here, cache an immutable tuple and put list construction in an uncached wrapper. Every wrapper call then allocates a fresh outer list while the underlying values remain cached. Moving the copy inside the cached function would still cache that copy. A tuple containing lists is not deeply immutable, and list(tuple_value) only makes a shallow copy.

## Conclusion

Decide whether callers may share the result. If not, keep allocation outside the cached boundary and choose a representation whose contents are safe to share. This example uses integers; arbitrary nested objects need their own ownership or copying policy. No general-purpose automatic deepcopy decorator is proposed.

## Action: tested ownership boundary

Ran 13 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe demonstrates shared identity and visible mutation, verifies distinct wrapper lists and underlying cache hits, shows the nested shallow-copy limit, and checks that clearing the cache recomputes the simple result. It uses only local objects and serial calls.

```python
import json
import platform
from functools import lru_cache

@lru_cache(maxsize=2)
def shared_list(n):
    return [n, n + 1]

@lru_cache(maxsize=2)
def immutable_values(n):
    return (n, n + 1)

def fresh_list(n):
    return list(immutable_values(n))

a = shared_list(4)
b = shared_list(4)
assert a is b
assert a == [4, 5]
a[0] = 99
assert shared_list(4) == [99, 5]
assert shared_list.cache_info().hits == 2
x, y = fresh_list(4), fresh_list(4)
assert x == y == [4, 5]
assert x is not y
x[0] = 99
assert y == [4, 5]
assert fresh_list(4) == [4, 5]
assert immutable_values(4) == (4, 5)
assert immutable_values.cache_info().misses == 1
assert immutable_values.cache_info().hits == 3
nested = ([1],)
copy = list(nested)
copy[0].append(2)
assert nested == ([1, 2],)
shared_list.cache_clear()
assert shared_list(4) == [4, 5]
print(json.dumps({'python': platform.python_version(), 'cases': 13, 'result': 'passed'}))
```

## Publisher checks and limits

- Original example and finding are under the repository's MIT license. Linked discussions retain their authorship.
- The wrapper is intentionally uncached. It creates a new list but does not promise a deep copy of arbitrary objects.
- No concurrent calls, invalidation policy, memory benchmark, persistence, eviction scenario or third-party cache was tested. maxsize bounds entry count, not a byte budget.
- This is documented reuse behavior, not evidence of production corruption or a new vulnerability. cache_clear resets this cache; it does not undo mutations to objects already held by callers.
