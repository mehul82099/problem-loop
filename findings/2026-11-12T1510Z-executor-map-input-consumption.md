# An Executor.map result iterator does not make its input lazy

Date: 2026-11-12. A documented input-consumption distinction, not a new CPython defect.

## Research

The Python 3.10 concurrent.futures reference says Executor.map collects its input iterables immediately rather than lazily. Historical CPython issues 74028 and 74508 and a Python Help discussion show developers expecting generator inputs to provide streaming behavior. Those reports motivate the question; their large-memory examples are not reproduced here.

The Python 3.14 reference documents an explicit buffersize option, added in 3.14, that limits submitted work whose results have not been yielded. It also says the default remains immediate collection. PR 125663 is merged. This report does not describe the historical request as an unresolved defect, and does not test the newer buffer implementation.

## Discussion

There are two different boundaries: pulling input to submit work and retrieving output from the result iterator. On the tested CPython 3.10.12 build, ThreadPoolExecutor.map consumes all of a finite generator before returning its result iterator, even while a gate prevents workers from returning successfully. max_workers bounds worker threads, not the number of input values pulled. Waiting to call next on the result iterator does not defer that input consumption.

A built-in map control leaves the same finite generator untouched at construction and pulls its first value on the first next call. That contrast does not mean replacing executor.map with built-in map preserves parallel execution.

This is separate from the repository's earlier multiprocessing.Pool.imap semaphore-retention report. The API here is concurrent.futures.ThreadPoolExecutor, and the measured boundary is input consumption, not retained semaphore registrations.

## Conclusion

Do not infer input backpressure from the returned iterator or from max_workers. On an applicable Python 3.14+ deployment, consider the documented buffersize option and test the intended workload and version. On older versions, use an explicitly bounded submission design if input backpressure is required. Neither a generator expression alone nor a worker-count setting establishes that policy. This finding supplies a small regression probe, not a replacement executor or a universal memory bound.

## Action

Original code under this repository's MIT license. Run without Python optimization so assertions remain enabled. Only finite synthetic inputs and local threads/events are used. The gate is released in finally; event timeouts fail the test instead of allowing a silent hang. No sleep-based timing assertion, file data, network or external service is involved.

```python
import json
import platform
from concurrent.futures import ThreadPoolExecutor
from threading import Event

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

for size in (0, 1, 3, 8):
    # A lazy built-in map does not pull input at construction.
    pulled = []
    def source():
        for value in range(size):
            pulled.append(value)
            yield value
    lazy = map(lambda value: value * 2, source())
    check(pulled == [])
    if size:
        check(next(lazy) == 0)
        check(pulled == [0])
    check(list(lazy) == [value * 2 for value in range(1 if size else 0, size)])
    check(pulled == list(range(size)))

    for workers in (1, 2, 4):
        pulled = []
        gate = Event()
        started = Event()
        def source():
            for value in range(size):
                pulled.append(value)
                yield value
        def work(value):
            started.set()
            if not gate.wait(10):
                raise RuntimeError('test gate timed out')
            return value * 2
        with ThreadPoolExecutor(max_workers=workers) as executor:
            try:
                results = executor.map(work, source())
                # No result has been retrieved, yet every input was pulled.
                check(pulled == list(range(size)))
                check(not gate.is_set())
                if size:
                    check(started.wait(5))
                # The gate ensures work has not completed successfully yet.
            finally:
                gate.set()
            check(list(results) == [value * 2 for value in range(size)])
            check(list(results) == [])

print(json.dumps({'python': platform.python_version(),
                  'implementation': platform.python_implementation(),
                  'checks': checks, 'executor_cases': 12,
                  'builtin_controls': 4, 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.10.12**, Linux: **75 checks passed**, across **12 executor cases** (input lengths 0, 1, 3, 8 by worker counts 1, 2, 4) and **4 built-in map controls**. Every executor case pulls all input before any result retrieval; nonempty cases confirm a worker started while the gate was closed. After release, all expected doubled values are retrieved in order and the result iterator is exhausted.

No infinite input, RSS measurement, production workload, process pool, exceptions from the input generator, cancellation, timeout contract or shutdown race was tested. This does not establish how many workers start before map returns, their completion order, a byte-size memory bound or Python 3.14 buffer behavior. The newer option is documentation-grounded guidance only. The probe uses default map options on the named build.

## Publisher

One bounded, standalone finding and probe. No upstream repository or third-party service changed. Source reports are historical motivation; local observations and version-specific documentation are kept separate.

## Sources

1. [Python 3.10 concurrent.futures reference](https://docs.python.org/3.10/library/concurrent.futures.html): immediate collection, asynchronous calls and max_workers contract.
2. [Python 3.14 concurrent.futures reference](https://docs.python.org/3.14/library/concurrent.futures.html): buffersize addition and unchanged eager default.
3. [CPython issue 74028](https://github.com/python/cpython/issues/74028), closed: historical large/infinite-input request, not a claim that it remains unresolved.
4. [CPython issue 74508](https://github.com/python/cpython/issues/74508), closed: historical generator memory concern; no memory figures adopted here.
5. [Python Help discussion](https://discuss.python.org/t/lazy-collection-of-iterables-for-concurrent-futures-executor-map/21045), November 2022: developer expectations and why naive lazy submission changes concurrency.
6. [CPython PR 125663](https://github.com/python/cpython/pull/125663), merged: buffersize design and preserving the default behavior.
7. [CPython 3.10 Executor source](https://github.com/python/cpython/blob/3.10/Lib/concurrent/futures/_base.py): list-based submission before returning the result iterator. Branch source is supporting evidence, not a claim it is the exact installed patch source.
