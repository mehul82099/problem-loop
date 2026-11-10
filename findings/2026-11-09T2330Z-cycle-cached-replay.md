# cycle replays saved values; it does not restart the source

Date: 2026-11-10. Tested itertools replay policy, not a new iterator defect.

## Research

Python's versioned itertools references say cycle saves values from the input and repeats those saved values after exhaustion. They warn about potentially significant auxiliary storage. Two original 2013 questions ask why a new traversal cannot replace that storage. PyMOTW and an independent complexity guide corroborate caching. The official recipe and bounded tests settle the distinction here; no timing or byte-level memory measurements are claimed.

One community answer loosely says iterables can only be traversed once. That is too broad: lists and other re-iterable containers support fresh traversals. An iterator such as a generator object is one-shot. cycle accepts the supplied iterable; it does not receive a recipe or permission to reconstruct a generator's computation.

## Discussion

A generator can append a diagnostic marker each time it produces 0, 1 and 2. Taking twelve values from cycle yields four laps of those values but only three production markers. Replay is not a new source execution. It does not refresh a query, repeat a delay, or rerun a callback.

The first pass is still incremental. In the instrumented finite source, requesting a short prefix does not pull all remaining values. Once a request observes exhaustion, subsequent values come from the saved sequence without more source next calls. Empty input produces no values. This probe counts successful and terminal source calls separately through the source's call counter.

"Saved copy" does not mean a deep snapshot of each payload. In the mutable-dictionary sample, replacing a source list slot after replay starts does not replace the cached reference. Mutating the original dictionary is visible when that same object is replayed. The probe waits until first-pass exhaustion before changing the list, avoiding any claim about modifying a container during its live traversal.

| Required behavior | Deliberate model | Boundary |
| --- | --- | --- |
| Replay a finite sequence of observed values | cycle | Retains values; does not refresh computation |
| Recompute a dataset each pass | Explicit source factory and restart/error policy | Different effects and values; not supplied by cycle |
| Independent mutable snapshots | Define copy/serialization policy at acquisition | cycle alone retains object references |

## Conclusion

Use cycle when replay is intended. For live polling or refreshed work, specify how sources are reopened, failures handled and resources closed. A lazy iterator is not a constant-storage promise: cycle keeps first-pass values, and an input that never exhausts never reaches its saved replay phase. Do not test an infinite input by trying to exhaust it.

The earlier tee finding already covers shared-source production and mutable references; list repetition covers repeated references. Those overlaps are acknowledged. This increment tests cycle's first-pass-to-replay transition, bounded source-call counts, empty input and lack of source reconstruction. No new aliasing discovery is claimed.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 1,197 checks over 297 finite source-size/prefix cases plus selected generator/reference cases. Source sizes 0..8, requested prefixes 0..32. Expected output uses modular indexes and expected source calls include at most one exhaustion observation.

The source's next calls are checked, not a promise that iterable construction has no effects: cycle may obtain an iterator during construction. No exception-resumption, concurrent mutation, infinite-source storage growth or custom resource lifecycle behavior is tested. Run without optimization so assertions remain active.

```python
from itertools import cycle, islice
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class Source:
    def __init__(self, n):
        self.n = n
        self.position = 0
        self.calls = 0
    def __iter__(self):
        return self
    def __next__(self):
        self.calls += 1
        if self.position == self.n:
            raise StopIteration
        value = self.position
        self.position += 1
        return value

cases = 0
for size in range(9):
    for take in range(33):
        source = Source(size)
        replay = cycle(source)
        check(source.calls == 0)
        result = list(islice(replay, take))
        expected = [i % size for i in range(take)] if size else []
        check(result == expected)
        expected_calls = min(take, size + 1) if size else min(take, 1)
        check(source.calls == expected_calls)
        check(source.position == min(size, take))
        cases += 1

# Once first-pass exhaustion has been seen, replacing list slots is not
# a refresh of the cached sequence. Mutating a cached object is visible.
a, b = {'value': 1}, {'value': 2}
items = [a, b]
replay = cycle(items)
check(next(replay) is a)
check(next(replay) is b)
check(next(replay) is a)  # transition to saved values
items[0] = {'value': 99}
a['value'] = 7
check(next(replay) is b)
check(next(replay) is a)
check(a['value'] == 7)
check(items[0]['value'] == 99)

# A generator's production effects occur once per source value, not lap.
produced = []
def generate():
    for n in range(3):
        produced.append(n)
        yield n
replay = cycle(generate())
check(list(islice(replay, 12)) == [0, 1, 2] * 4)
check(produced == [0, 1, 2])
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'prefix_cases': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Exact published bytes are compared with the tested draft; committed code is extracted and rerun on both named builds.
- Synthetic in-memory values only. No files, services, user data, timers, threads or network. No performance, memory-size, production polling or automatic cleanup guarantee.
- Holding a reference is distinct from cloning content. No custom copy hooks, serialization policy or lifetime/finalizer timing measured.
- Historical questions demonstrate conceptual confusion, not a current unresolved defect. Independent complexity shorthand is not a measured result for arbitrary user iterables.

## Sources

1. Python 3.13 itertools reference, cycle saved sequence and storage warning: https://docs.python.org/3.13/library/itertools.html
2. Python 3.14 itertools reference, same applicable contract: https://docs.python.org/3.14/library/itertools.html
3. Original May 2013 question about reconstructing an iterable instead of caching: https://stackoverflow.com/questions/16638639/why-does-pythons-itertools-cycle-need-to-create-a-copy-of-the-iterable
4. Original August 2013 question about cycle auxiliary memory: https://stackoverflow.com/questions/18478786/in-python-why-does-itertools-cycle-require-additional-memory
5. Independent complexity guide, qualitative cache/storage background only: https://pythoncomplexity.com/stdlib/itertools/
6. PyMOTW independent guide, cycle replay example: https://pymotw.com/3/itertools/
