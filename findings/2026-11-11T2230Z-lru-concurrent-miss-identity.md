# A thread-safe lru_cache is not a single-flight factory

Date: 2026-11-12. A bounded concurrent-miss diagnostic for documented behavior.

## Research

[CPython issue 141831](https://github.com/python/cpython/issues/141831) describes using lru_cache(maxsize=1) for singleton creation and observing distinct returned objects under concurrent cold calls. The issue is **closed**. This report does not present it as an unresolved cache bug, adopt its search-hit usage estimates, or infer a release fix from closure.

The [Python 3.14 functools reference](https://docs.python.org/3.14/library/functools.html) defines thread safety as cache data-structure coherence and explicitly permits the wrapped function to run more than once before the first result is cached. Coherent updates are different from sharing one in-progress computation. Whether a duplicate call returns a distinct object depends on what the wrapped function does: this diagnostic deliberately returns a new object each time, not a claim about every cached function.

The [v3.10.12 C implementation](https://github.com/python/cpython/blob/v3.10.12/Modules/_functoolsmodule.c), bounded_lru_cache_wrapper, calls the user function after a miss and checks again for a newly inserted key afterward. If another call inserted that key meanwhile, it returns its own computed result. That source branch supports the observed bounded-cache mechanism; it is not presented as a universal implementation or cache-winner guarantee.

The fixture uses the documented [threading Barrier](https://docs.python.org/3.10/library/threading.html) and [ThreadPoolExecutor/Future](https://docs.python.org/3.10/library/concurrent.futures.html) APIs. A barrier inside the cached function ensures every worker has entered the body before any body can return. Its five-second timeout breaks a failed rendezvous rather than depending on a guessed sleep. Future results use a ten-second wait; that timeout alone is not thread cancellation or a whole-program deadline.

## Discussion

**108 checks passed across nine concurrent configurations** on installed CPython **3.10.12**, Linux. Each configuration also runs a serial cold/warm control. Capacities are 1, 128 and None; worker counts are 2, 3 and 4. Every worker calls the same positional string key on a fresh cache.

| Workers | Body entries per concurrent configuration | Distinct objects returned | Cached entries afterward |
| --- | --- | --- | --- |
| 2 | 2 | 2 | 1 |
| 3 | 3 | 3 | 1 |
| 4 | 4 | 4 | 1 |

All three capacities produce this table on the tested build. Two later warm calls reuse one of the returned objects without another body entry. The diagnostic deliberately does not assert which worker's object becomes cached. After cache_clear, two serial calls produce one body entry and reuse one object. Results are retained while identity is checked, so object-id recycling does not explain the distinctness.

## Conclusion

Do not use maxsize=1 as an exactly-once or singleton-construction guarantee under concurrent cold calls. Use explicit initialization ownership or a separate in-progress coordination design if the application truly requires shared work. Its failure, retry, cancellation, reentrancy and key-lifetime rules need their own contract. No production single-flight implementation is supplied here, and no recommendation is made to place one global lock around arbitrary user code.

The GIL does not establish this call-once property: the tested workers wait at a synchronization barrier, allowing other threads to enter the wrapped function. These are overlapping threaded calls, not a CPU-parallel throughput claim or a free-threaded Python test. The function creates only disposable in-memory objects, not connections, models, remote requests or other real resources.

## Action

Run `python3 lru_concurrent_misses.py`. Original MIT diagnostic; no network, files, private data, third-party packages or wall-clock benchmark. Barrier and future timeouts are test-failure guardrails, not performance requirements. A failure raises rather than silently reporting a passing configuration.

```python
# Original diagnostic, MIT licensed. No external resource creation.
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from threading import Barrier, Lock
import json
import platform

checks = 0
cases = []


def check(condition):
    global checks
    if not condition:
        raise AssertionError('check failed')
    checks += 1


for capacity in (1, 128, None):
    for workers in (2, 3, 4):
        gate = Barrier(workers, timeout=5)
        lock = Lock()
        entered = []

        @lru_cache(maxsize=capacity)
        def build(key):
            value = object()
            with lock:
                entered.append((key, value))
            if gate is not None:
                gate.wait()
            return value

        # All bodies must enter before any body can return/cache its value.
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = [pool.submit(build, 'same-key') for _ in range(workers)]
            outputs = [future.result(timeout=10) for future in pending]
        cold = build.cache_info()
        check(len(entered) == workers)
        check(all(key == 'same-key' for key, _ in entered))
        check(len({id(value) for value in outputs}) == workers)
        check({id(value) for value in outputs} == {id(value) for _, value in entered})
        check((cold.hits, cold.misses, cold.currsize) == (0, workers, 1))
        gate = None
        warm = build('same-key')
        check(any(warm is value for value in outputs))
        check(build('same-key') is warm)
        check(len(entered) == workers)
        check((build.cache_info().hits, build.cache_info().misses) == (2, workers))

        # Serial cold/warm control with a fresh cache and no synchronization gate.
        build.cache_clear()
        entered.clear()
        first = build('same-key')
        second = build('same-key')
        check(first is second)
        check(len(entered) == 1)
        check((build.cache_info().hits, build.cache_info().misses,
               build.cache_info().currsize) == (1, 1, 1))
        cases.append({'capacity': capacity, 'workers': workers,
                      'cold_entries': workers, 'distinct_cold_results': workers,
                      'warm_reused_one_result': True})
        build.cache_clear()
print(json.dumps({'python': platform.python_version(), 'platform': platform.system(),
                  'checks': checks, 'cases': len(cases), 'results': cases}, indent=2))
```

## Publisher and limits

Only this installed build, ordinary hashable string key and the stated worker/capacity matrix were executed. Documentation pages may identify newer patch releases; they establish API meaning, not execution on those releases. No free-threaded build, process workers, async tasks, other Python implementation, maxsize=0, exceptions from the factory, custom hash/equality, eviction contention, recursive calls, cache clearing during an active call, invalidation policy, stress/probability estimate or memory/speed result is claimed.

Earlier repository cache findings concern serial mutable-result aliasing and retained method instances; both were read fully. This increment tests overlapping cold misses and singleton identity, not those serial ownership/lifetime cases again. No external side effect is used to demonstrate duplicate execution.
