# itertools.product yields output lazily but pools finite inputs first

Date: 2026-11-06. A documented input-consumption boundary, not a new Python defect.

## Research

The [Python 3.14 itertools reference](https://docs.python.org/3.14/library/itertools.html) says product completely consumes its input iterables and keeps pools of values in memory; it is useful only with finite inputs. Lazy output does not imply lazy input consumption. [Documentation issue 40806](https://bugs.python.org/issue40806) and its [2020 documentation commit](https://github.com/python/cpython/commit/cfc6ce4d40f2f01314b7e283fb972a7bb3ed3faa) record the clarification.

A [2012 memory question](https://stackoverflow.com/questions/8695422/why-do-i-get-a-memoryerror-with-itertools-product) and a [2022 file-iteration question](https://stackoverflow.com/questions/72722268/python-itertools-dont-load-files-into-memory) show the practical confusion. A [2019 initialization question](https://stackoverflow.com/questions/58262861/why-does-itertools-product-run-through-all-elements-at-initialization) includes an explanation framed around the first next call and a Python generator recipe. That timing is not what the built-in product does on the two CPython builds tested here: source events already exist immediately after construction, before any next call. A roughly equivalent generator recipe is not an exact timing specification.

## Discussion

Product needs to revisit input values to emit combinations, so its output iterator holds input pools rather than rerunning arbitrary one-shot sources. In this probe, construction consumes both small generators. Reading the first result does not trigger more input generation because those sources are already exhausted.

Wrapping product in islice limits returned output, not the work already performed to pool its inputs. A source exception can therefore surface while constructing product, before an output iterator is assigned or any output next call runs. Catch errors around construction as well as iteration when the input can fail.

## Conclusion

Check input size and finiteness separately from output size. If a smaller Cartesian product is actually intended, select a bounded input prefix before calling product. That changes the result set and is not a transparent optimization. If full streaming semantics are required, choose a design with explicit replay/reopening rules rather than replacing arbitrary iterators with naive nested loops.

No infinite input or large allocation is run here. No memory amount, throughput, production failure or universal streaming replacement is claimed. The Cartesian output itself can still be large, even with small finite input pools.

## Action

Original MIT-licensed probe. All inputs contain at most four local values. It checks construction-time input events, output order, the difference between input and output limits, and one controlled source exception.

```python
import json
import platform
from itertools import islice, product

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def tracked(label, values, events):
    for value in values:
        events.append((label, value))
        yield value

events = []
left = tracked('L', [1, 2], events)
right = tracked('R', ['a', 'b'], events)
check(events == [])
pairs = product(left, right)
check(events == [('L', 1), ('L', 2), ('R', 'a'), ('R', 'b')])
check(list(left) == [])
check(list(right) == [])
check(next(pairs) == (1, 'a'))
check(list(pairs) == [(1, 'b'), (2, 'a'), (2, 'b')])
check(len(events) == 4)

# Limiting product output does not limit its input pooling.
events = []
prefix = islice(product(tracked('L', range(4), events), ['x']), 1)
check(events == [('L', 0), ('L', 1), ('L', 2), ('L', 3)])
check(list(prefix) == [(0, 'x')])
check(len(events) == 4)

# A source failure can occur in product construction, before any next call.
events = []
def failing_source():
    events.append('yielded')
    yield 7
    events.append('raised')
    raise ValueError('controlled source failure')

raised = False
try:
    product(failing_source(), ['x'])
except ValueError as error:
    raised = str(error) == 'controlled source failure'
check(raised)
check(events == ['yielded', 'raised'])

# Bound a chosen source prefix before constructing the product, if that
# smaller Cartesian product is the intended application contract.
events = []
pairs = product(islice(tracked('L', range(4), events), 2), ['x'])
check(events == [('L', 0), ('L', 1)])
check(list(pairs) == [(0, 'x'), (1, 'x')])

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 14 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Tests do not measure memory, consume infinite streams, open files, or establish the internals of every Python implementation. Repeat, zero-input and empty-pool corner cases are outside this probe. Repository CI is separate.

## Publisher

One evidence-backed finding with a bounded executable probe. No runtime patch, package installation or application migration.
