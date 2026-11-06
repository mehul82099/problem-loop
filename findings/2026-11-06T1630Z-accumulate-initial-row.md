# accumulate initial adds an output, not just a starting balance

## Research
Python documents that a non-None initial value adds one result to itertools.accumulate output. Public discussion also asks how to use None as a real seed: initial=None is the sentinel for the ordinary first-input behavior, not a request to emit a None seed. Both details matter when aligning running state with input rows.

## Discussion
For [2, 3, 4], the default running totals are [2, 5, 9]. With initial=0 they are [0, 2, 5, 9]. Zipping the original input with that seeded output pairs each row with its pre-update total and omits the final total because zip stops at the shorter input. If after-update alignment is intended, explicitly skip the emitted seed before pairing. If before-update alignment is intended, those pairs may be correct. Name the convention rather than treating either as universally wrong.

An empty input yields no default results, but a non-None initial still yields one. initial=None behaves like omission: the first input becomes the initial result without calling the step function for it. For a literal None seed, chain a one-element [None] prefix onto the input and let the step function handle None. This emits the seed as well, so the same alignment question remains.

## Conclusion
Treat a scan's initial state as a separate row from its state after each input. Specify whether output includes that initial row, how empty input behaves, and how many step calls are expected. These are documented semantics, not a new defect. The small probe checks both conventions and the None sentinel without building a general aggregation API.

## Action: executable probe
Original code under this repository's MIT license. Tiny finite in-memory iterables only. Run without Python optimization so assertions remain enabled.

```python
from itertools import accumulate, chain, islice
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

values = [2, 3, 4]
check(list(accumulate(values)) == [2, 5, 9])
check(list(accumulate(values, initial=0)) == [0, 2, 5, 9])
check(list(accumulate(values, initial=10)) == [10, 12, 15, 19])
check(list(accumulate([])) == [])
check(list(accumulate([], initial=0)) == [0])
check(list(accumulate(values, initial=None)) == [2, 5, 9])
check(list(accumulate([], initial=None)) == [])

# A common alignment error: zip truncates to the shorter input.
check(list(zip(values, accumulate(values, initial=0)))
      == [(2, 0), (3, 2), (4, 5)])
check(list(zip(values, islice(accumulate(values, initial=0), 1, None)))
      == [(2, 2), (3, 5), (4, 9)])

calls = []
def step(state, item):
    calls.append((state, item))
    return item if state is None else state + item

check(list(accumulate(values, step, initial=None)) == [2, 5, 9])
check(calls == [(2, 3), (5, 4)])
calls.clear()
check(list(accumulate(chain([None], values), step)) == [None, 2, 5, 9])
check(calls == [(None, 2), (2, 3), (5, 4)])
check(list(accumulate(chain([None], []), step)) == [None])

seen = []
def source():
    for item in values:
        seen.append(item)
        yield item

running = accumulate(source(), initial=10)
check(next(running) == 10)
check(seen == [])
check(next(running) == 12)
check(seen == [2])
check(list(running) == [15, 19])
check(seen == values)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Tests ordinary/seeded totals, empty input, explicit None, before/after-update row alignment, step-call arguments, literal None via chain, and emitted seed before source values are fetched.
- No mutable accumulator state, custom numeric classes, infinite streams, concurrent consumers, performance benchmark, database aggregation or production workload was tested. No cache or historical-result storage guarantee is implied.

## Sources
- [Python 3.14 itertools](https://docs.python.org/3.14/library/itertools.html): current accumulate output contract and equivalent implementation.
- [CPython 3.14 documentation source](https://github.com/python/cpython/blob/3.14/Doc/library/itertools.rst): None sentinel and initial output; rolling branch, not an immutable release snapshot.
- [None-as-seed question](https://stackoverflow.com/questions/66056688/use-none-as-initial-for-itertools-accumulate): concrete sentinel mismatch and chain approach.
- [nkmk accumulate guide](https://note.nkmk.me/en/python-itertools-accumulate/): independent initial-count examples.
- [Programming notes](https://szuckerman.github.io/itertools_accumulate.html): independent initial example. Its broad caching/performance statements are not used.
- [Python-ideas, April 2018](https://mail.python.org/archives/list/python-ideas@python.org/message/SUASIWNESTFXB7DOLXDCYGIXORBUQWZ4/): historical output-count design discussion, not the current signature.
