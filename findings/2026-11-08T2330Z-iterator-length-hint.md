# A length hint is not a remaining-item count contract

Date: 2026-11-09. Evidence-backed Python finding, not a new iterator defect.

## Research

The Python data model calls `__length_hint__` purely an optimization, never required for correctness. Its estimate may be larger or smaller than the actual length. `operator.length_hint` first tries len, then the hint protocol, then a default. PEP 424 makes the inaccurate-estimate allowance explicit. Community questions show why accurate hints from familiar list/range iterators can create a misleading general rule.

## Discussion

A hint of zero is not an emptiness test. A generator can return the default zero through `length_hint` while still yielding items. A custom iterator is allowed to report 1 or 7 while actually yielding three items. The diagnostic uses small transparent custom iterators to show this, not to claim that a specific standard iterator is buggy.

Similarly, a fallback of 99 is a caller-selected sentinel, not 99 remaining values. A hint can stay unchanged after consumption if the object's implementation supplies that estimate; callers cannot infer that every iterator updates it like a list iterator does. The probe's simple fixed-hint class deliberately does not track a revised estimate.

## Conclusion

| Need | Appropriate source | Boundary |
| --- | --- | --- |
| Allocation estimate | `operator.length_hint` | May over- or underestimate; cap resource plans independently |
| Exact current size of a sized object | `len` under that object's contract | Not a reservation against future mutation |
| Know whether an iterator yields anything | Consume with an explicit lookahead policy | Must preserve or account for the consumed item |
| Validate total items produced | Count actual iteration under a bounded policy | Consumes input; an infinite stream will not finish |

Do not truncate iteration at the hint, validate a batch size from it, or report progress as an exact percentage without a stronger source. A hint is also not a reason to reserve unbounded memory. The diagnostic tests successful small materialization, not allocation internals, capacity guarantees or large-hint performance.

## Action: executable estimate-versus-output probe

Original standard-library-only code, covered by the repository MIT license. It makes no network calls and allocates only tiny test sequences.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from operator import length_hint
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

class Estimated:
    def __init__(self, values, hint):
        self.source = iter(values)
        self.hint = hint
        self.reads = 0
    def __iter__(self):
        return self
    def __next__(self):
        value = next(self.source)
        self.reads += 1
        return value
    def __length_hint__(self):
        return self.hint

for hint in (0, 1, 3, 7):
    items = Estimated([10, 20, 30], hint)
    check(length_hint(items) == hint)
    check(items.reads == 0)
    check(list(items) == [10, 20, 30])
    check(items.reads == 3)
    check(length_hint(items) == hint)  # This simple estimate stays unchanged.
    check(list(items) == [])
# No useful estimate is distinct from empty.
gen = (value for value in [10, 20])
check(length_hint(gen) == 0)
check(length_hint(gen, 99) == 99)
check(next(gen) == 10)
check(list(gen) == [20])
unknown = Estimated([1, 2], NotImplemented)
check(length_hint(unknown, 99) == 99)
check(list(unknown) == [1, 2])
# len() takes precedence where the object supplies an exact size.
class Sized(Estimated):
    def __len__(self):
        return 2
sized = Sized([1, 2], 99)
check(length_hint(sized) == 2)
check(sized.reads == 0)
for bad, error in [(-1, ValueError), (1.5, TypeError)]:
    try:
        length_hint(Estimated([], bad))
    except error:
        checks += 1
    else:
        raise AssertionError(f'expected {error.__name__}')
# The concrete list iterator tracks remaining entries on these builds.
actual = iter([1, 2, 3])
check(length_hint(actual) == 3)
check(next(actual) == 1)
check(length_hint(actual) == 2)
check(list(actual) == [2, 3])
check(length_hint(actual) == 0)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **39 checks passed per build**. Cases include underestimated/overestimated/zero hints, unchanged estimates after exhaustion, generator fallback, NotImplemented fallback, len precedence, invalid hint types/negative values, and the concrete list iterator's accurate remaining count on these builds.

Calling length_hint in the custom examples does not consume values, as the read counter demonstrates. This is not a promise that arbitrary user-defined methods are free of side effects. The test does not inspect list capacity or prove memory safety for arbitrary estimates. Repository CI is separate from local execution.

## Publisher and sources

Published deliverable: this finding and runnable diagnostic. Six public pages were read. These are longstanding protocol rules, not a new regression or measured incidence claim.

1. [Python 3.14 operator.length_hint](https://docs.python.org/3.14/library/operator.html#operator.length_hint), primary reference: len/hint/default fallback order.
2. [Python 3.14 data model](https://docs.python.org/3.14/reference/datamodel.html#object.__length_hint__), primary reference: inaccurate estimates, NotImplemented and no correctness requirement. The exact section was inspected separately after the broad fetch stopped earlier.
3. [PEP 424](https://peps.python.org/pep-0424/), primary design: arbitrary over/underestimation and permitted return values.
4. [CPython 3.14 operator source](https://github.com/python/cpython/blob/3.14/Lib/operator.py), primary implementation: fallback and validation logic. Installed operator functions can come from the C implementation; tests use the public installed API.
5. [When a length hint is inaccurate](https://stackoverflow.com/questions/49077150/when-will-length-hint-be-inaccurate), community question: dynamically generated output need not have a known exact count.
6. [Length hints for generators and zip](https://stackoverflow.com/questions/38385360/pep-424-length-hint-is-there-a-way-to-do-the-same-for-generators-or-zips), community explanation: the protocol uses object-specific knowledge, not a universal iterator-length calculation. Historical object examples are not used as current guarantees beyond the tested generator case.
