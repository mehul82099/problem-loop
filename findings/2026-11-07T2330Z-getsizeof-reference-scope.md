# getsizeof measures the container, not everything reachable from it

## Research
A public question asks why nested lists do not grow in reported size as expected. The current sys reference gives the boundary: getsizeof accounts for memory directly attributed to an object, not the objects it refers to. Ned Batchelder's independent explanation adds the second problem with simply summing nested sizes: objects can be shared, so the answer depends on what the measurement is meant to count.

## Discussion
A one-slot list pointing to a small bytearray and a one-slot list pointing to a larger bytearray have equal shallow sizes in this probe. Growing the larger referent leaves its containing list's reported size unchanged. That does not mean the additional data is free or that the process did not grow.

Two equal-valued lists can also have different reference topology. One fixture contains the same bytearray twice; another contains two distinct equal bytearrays. The shallow list sizes match. Adding every referent's getsizeof result double-counts the shared object in the first fixture. Deduplicating by identity answers one graph-accounting question, not exclusive ownership: another root may still refer to that object.

This is documented behavior, not a new memory-reporting bug. The sys reference also says getsizeof calls __sizeof__ and adds applicable collector overhead. Its result is not a serialized payload length, an allocation trace, a retained-size analysis or the process's resident-memory footprint.

## Conclusion
State the metric before collecting a number:

| Question | Relevant metric | Boundary |
| --- | --- | --- |
| Immediate object representation | `sys.getsizeof` | Excludes separately referenced objects; implementation-specific. |
| Selected reachable objects under a declared traversal rule | Identity-aware accounting for that rule | Sharing, cycles and traversal scope need explicit handling. |
| Python allocation changes during work | Consider `tracemalloc` snapshots | Tracing must start early; not a universal process-memory meter. |
| Wire/storage payload | Measure the actual encoded representation | Different from in-memory object overhead. |
| Whole-process memory pressure | Process-level measurement | Not derived by summing a few Python objects. |

The helper below is deliberately limited to one two-level list/bytearray fixture. It is not a generic deep-size implementation and must not be reused for arbitrary graphs. A general traversal must define what edges to follow, handle cycles, avoid accidental double-counting and explain shared objects. No universal "total size of this value" number is supplied.

## Action: bounded reference-topology probe
Original code under this repository's MIT license. Small in-memory objects only. Assertions compare relationships, not fixed built-in object byte constants. Run without `-O` so assertions remain enabled.

```python
import json
import platform
import sys

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

small = bytearray(1)
large = bytearray(4096)
left = [small]
right = [large]
check(len(left) == len(right) == 1)
check(sys.getsizeof(left) == sys.getsizeof(right))
check(sys.getsizeof(large) > sys.getsizeof(small))
before = sys.getsizeof(right)
large.extend(b'x' * 4096)
check(sys.getsizeof(right) == before)
check(len(right[0]) == 8192)

shared = bytearray(b'abc')
aliased = [shared, shared]
distinct = [bytearray(b'abc'), bytearray(b'abc')]
check(aliased == distinct)
check(aliased[0] is aliased[1])
check(distinct[0] is not distinct[1])
check(sys.getsizeof(aliased) == sys.getsizeof(distinct))

# Explicit accounting only for this two-level list/bytearray fixture.
def unique_fixture_size(rows):
    unique = {id(item): item for item in rows}
    return sys.getsizeof(rows) + sum(sys.getsizeof(item) for item in unique.values())

naive = sys.getsizeof(aliased) + sum(sys.getsizeof(item) for item in aliased)
unique = unique_fixture_size(aliased)
check(naive - unique == sys.getsizeof(shared))
check(unique_fixture_size(distinct) > unique)
check(unique == sys.getsizeof(aliased) + sys.getsizeof(shared))
cycle = []
cycle.append(cycle)
check(cycle[0] is cycle)
check(sys.getsizeof(cycle) > 0)  # Does not recursively traverse the cycle.
cycle.clear()
check(cycle == [])

class ReportedSize:
    def __sizeof__(self):
        return 123

sample = ReportedSize()
check(sample.__sizeof__() == 123)
check(sys.getsizeof(sample) >= 123)  # Includes implementation overhead.
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 17 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Covers equal-shape shallow list sizes despite differing referents, referent growth, equal values with shared versus distinct identities, double-counting under a naive two-level sum, nonrecursive handling of a self-reference, and a custom __sizeof__ report with implementation overhead.
- No exact built-in byte sizes, allocator arena behavior, RSS, leak diagnosis, tracemalloc results, external buffers, third-party extensions, custom graph traversal or freed-memory return to the OS were measured. Equal shallow list sizes are verified for these constructions and builds, not promised for all equal-length lists with different allocation histories.

## Sources
- [Python 3.14 sys reference](https://docs.python.org/3.14/library/sys.html): getsizeof scope, __sizeof__ and implementation-specific caveats.
- [Python 3.14 tracemalloc reference](https://docs.python.org/3.14/library/tracemalloc.html): Python allocation tracing and allocations before tracing starts being absent from snapshots. No tracing experiment is claimed here.
- [CPython 3.14 list implementation](https://github.com/python/cpython/blob/3.14/Objects/listobject.c): list __sizeof__ storage accounting; mutable branch.
- [Public nested-list question](https://stackoverflow.com/questions/41318803/python-in-memory-size-of-nested-empty-lists): real confusion about outer containers and referents. Historical byte constants are not copied as current results.
- [Public object-memory question](https://stackoverflow.com/questions/33978/find-out-how-much-memory-is-being-used-by-an-object-in-python): community discussion of reference graphs and measurement scope. General recursive recipes are not adopted as a universal answer.
- [Ned Batchelder's explanation](http://nedbatchelder.com/blog/202002/sysgetsizeof_is_not_what_you_want): independent 2020 discussion of shallow sizes, sharing and serialized versus in-memory representations.
