# A class-decorated lru_cache keeps method instances alive through its keys

## Research
Python documents that lru_cache retains arguments and results until entries age out or the cache is cleared. For an instance method, self is one of those arguments. The programming FAQ distinguishes instance-level cached_property storage from the class-level wrapper created by decorating a method with lru_cache. Public reports show the mismatch when callers expect deleting their last local instance reference to release an object immediately.

## Discussion
The probe uses ordinary identity-hashed instances and integer return values, so the retained object is not kept alive by a result pointing back to it. Two instances use the same decorated method wrapper, while their self arguments produce separate cache entries. Its cache_info statistics and maxsize apply to that shared wrapper. Calling cache_clear through one instance clears all entries for that wrapper, including entries holding other instances.

Weak references demonstrate lifetime without keeping the instances alive themselves. After deleting a local variable and running garbage collection, the instance remains reachable through the cache. Clearing the wrapper releases that reference. A second case adds enough new entries to evict an unused instance's entry and demonstrates collection after eviction. There is no wall-clock expiry: an idle bounded cache need not evict an entry until cache activity displaces it or it is cleared.

## Conclusion
Choose cache ownership and invalidation scope deliberately. A finite maxsize limits entry count, not bytes, instance age or per-instance entries. If prompt release is required, consider instance-owned caching or a pure helper keyed by immutable data, after reviewing the lifetime and key semantics that choice needs. Do not describe ordinary bounded cache retention as proof of an unbounded leak. This probe does not implement a general weak-reference cache or adopt mutable-hash recipes from external examples.

## Action: executable probe
Original code under this repository's MIT license. In-memory instances, weak references and explicit garbage collection only. Run without Python optimization so assertions remain enabled.

```python
from functools import lru_cache
import gc
import json
import platform
import weakref

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class Meter:
    def __init__(self, offset):
        self.offset = offset
        self.calls = 0

    @lru_cache(maxsize=2)
    def score(self, value):
        self.calls += 1
        return self.offset + value  # Result does not refer back to self.

try:
    a, b = Meter(10), Meter(20)
    check(a.score(1) == 11)
    check(a.score(1) == 11 and a.calls == 1)
    check(b.score(1) == 21 and b.calls == 1)
    info = Meter.score.cache_info()
    check((info.hits, info.misses, info.currsize, info.maxsize) == (1, 2, 2, 2))
    check(a.score.cache_info() == b.score.cache_info())
    ref_a, ref_b = weakref.ref(a), weakref.ref(b)
    del a
    gc.collect()
    check(ref_a() is not None)  # Cache key still owns this instance.
    b.score.cache_clear()      # Shared wrapper, not b-only invalidation.
    gc.collect()
    check(ref_a() is None)
    check(ref_b() is b)
    info = Meter.score.cache_info()
    check((info.hits, info.misses, info.currsize) == (0, 0, 0))
    check(b.score(1) == 21 and b.calls == 2)

    c = Meter(30)
    check(c.score(1) == 31)
    ref_c = weakref.ref(c)
    del c
    gc.collect()
    check(ref_c() is not None)
    check(b.score(2) == 22)
    check(b.score(3) == 23)  # Enough misses to evict both older entries.
    gc.collect()
    check(ref_c() is None)
    check(Meter.score.cache_info().currsize == 2)
    check(b.calls == 4)
    del b
    gc.collect()
    check(ref_b() is not None)
finally:
    Meter.score.cache_clear()
gc.collect()
check(ref_b() is None)
check(Meter.score.cache_info().currsize == 0)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Covers same-instance cache hits, separate-instance results, shared statistics and size limit, retention after local deletion, cross-instance cache_clear, statistic reset, release after clear, release after bounded eviction and final cleanup.
- No memory-size benchmark, timing guarantee, finalizers, reference cycles, custom equality/hash, mutable instance state, threads, per-instance wrapper implementation or other Python interpreter was tested. A result or another live reference could retain an instance after its cache key is gone.

## Sources
- [Python 3.14 functools](https://docs.python.org/3.14/library/functools.html): argument/result retention, self in method cache keys, maxsize and cache controls.
- [Python 3.14 programming FAQ](https://docs.python.org/3.14/faq/programming.html): method cache ownership and lifetime, section 'How do I cache method calls?'. Used only for lifetime distinctions; mutable-hash examples were not adopted.
- [CPython issue 96851](https://github.com/python/cpython/issues/96851): September 2022 documentation discussion about self retention and the distinction from an unbounded memory leak.
- [Caching a lot of methods in Python](https://death.andgravity.com/caching-methods): independent explanation of class-wrapper lifetime and instance-owned alternatives. Alternative implementations were not executed.
- [Release objects with cached instance methods](https://stackoverflow.com/questions/33672412/python-functools-lru-cache-with-instance-methods-release-object): public lifetime question and discussion of cache ownership. No third-party package or weak-reference recipe was adopted.
- [Caching methods causes instances to live forever](https://discuss.python.org/t/caching-methods-causes-instances-to-live-forever/60303): community discussion distinguishes unbounded cache from bounded lru_cache. Its title is not a claim that bounded entries survive eviction or clearing.
