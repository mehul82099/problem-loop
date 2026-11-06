# islice selects outputs but consumes skipped input positions

## Research
A public Python question asks why islice(source, 5, 0) yields nothing but still consumes five inputs. The Python 3.14 documentation states that fully consuming a finite-stop islice advances an input iterator by max(start, stop), regardless of step. That count is bounded by available input: an already exhausted source cannot supply more values.

## Discussion
This is documented behavior, not a new defect. Output count is not input-consumption count. A large step reduces yielded values, not necessarily how far the shared source advances. Even an empty slice can consume a prefix. Source work and side effects can therefore happen without corresponding output.

Construction is lazy with respect to fetching these generator values. Partial consumption is different from exhaustion: after its last yielded value, an islice may still have skipped input to consume when asked for another result. Do not apply the full-consumption rule to a loop that broke early. Passing a list does not mutate that list: islice gets its own iterator, unlike sharing an existing single-pass iterator.

## Conclusion
Give a shared input iterator one clear owner. If skipped values must remain available, use an independently repeatable source or explicitly retain a bounded collection before slicing. That changes storage and source-work costs; it is not a free streaming substitute. Do not treat an empty output list or a small output count as proof of no upstream work.

## Action: executable probe
Original code under this repository's MIT license. Run with Python 3.13 or 3.14. Tiny finite in-memory inputs only.

```python
from itertools import islice
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def tracked(n, seen):
    for value in range(n):
        seen.append(value)
        yield value

seen = []
source = tracked(10, seen)
selected = islice(source, 1, 6, 4)
check(seen == [])
check(next(selected) == 1)
check(seen == [0, 1])
check(list(selected) == [5])
check(seen == list(range(6)))
check(next(source) == 6)

# The last yield need not finish consuming up to stop.
seen = []
source = tracked(10, seen)
selected = islice(source, 1, 6, 10)
check(next(selected) == 1)
check(seen == [0, 1])
check(list(selected) == [])
check(seen == list(range(6)))
check(next(source) == 6)

for start, stop in [(5, 0), (5, 5)]:
    source = iter(range(10))
    check(list(islice(source, start, stop)) == [])
    check(next(source) == 5)

source = iter(range(3))
check(list(islice(source, 5, 0)) == [])
check(next(source, 'done') == 'done')

values = list(range(10))
check(list(islice(values, 1, 6, 4)) == [1, 5])
check(values == list(range(10)))
check(next(iter(values)) == 0)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Checks lazy fetching, partial consumption, trailing skips after the final yield, two empty ranges, short input exhaustion, and a reusable list control.
- No file, socket, database, concurrent consumer, memory benchmark, or production workload was tested. No recovery or rollback guarantee is implied. This is distinct from the earlier product-input-pools finding, which concerns eager construction of product inputs.

## Sources
- [Python 3.14 itertools](https://docs.python.org/3.14/library/itertools.html): current islice consumption contract and consume recipe.
- [Public question, June 2024](https://stackoverflow.com/questions/78664686/itertools-islice-iterate-over-input-even-when-stop-is-smaller-than-start): concrete empty-output consumption confusion.
- [CPython issue 71571](https://github.com/python/cpython/issues/71571): historical start/stop discussion, closed as not a bug. Not a current regression report.
- [CPython issue 54532](https://github.com/python/cpython/issues/54532): old final-position behavior was changed; historical examples are not current expected output.
- [Python Morsels islice guide](https://www.pythonmorsels.com/islice/): lazy selection and iterator reuse explanation. Its broad stop-point phrasing should be read alongside the primary max(start, stop) rule.
- [Iterator pipelines guide](https://nalar.dev/building-memory-efficient-iterator-pipelines-with-python-itertools/): consuming view and ownership explanation.
