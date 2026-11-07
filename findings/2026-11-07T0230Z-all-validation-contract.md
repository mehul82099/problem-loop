# all answers a truth question, not an exhaustive validation report

## Research
Python documents all as returning True for an empty iterable and stopping when it finds a falsey element. any stops at a truthy element and returns False for empty input. Public generator questions show how these rules interact with a one-shot source: consumed items do not reappear and an unchecked tail can remain.

## Discussion
With all(predicate(x) for x in source), the first rejected item is consumed and checked, but later items may never reach the predicate. Calling all again on an exhausted source returns True without repeating earlier checks. This does not certify the original data, nor prove that the original input was nonempty. A tail exception can also remain unobserved after a short-circuit result.

A list comprehension evaluates its predicate calls before all receives the resulting list. This differs from a generator expression, but is not a universal validation fix: it materializes results, and a source or predicate exception can still stop evaluation. Avoid making necessary work depend on short-circuited predicate side effects.

## Conclusion
Use all or any when a short-circuit truth answer is the intended contract. If the requirement is nonempty input plus a report of every failed row, count and collect failures in an explicit pass. The bounded example below returns rejected indices and an explicit nonempty condition. It finishes an exhaustive report only when the finite source and predicate finish normally; it supplies no rollback or exception-collection protocol. This is documented behavior, not a new defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory iterators, lists and event logs only. Run without Python optimization so assertions remain enabled.

```python
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(all([]) is True)
check(any([]) is False)
check(all([1, 'x']) is True)
check(all([1, '']) is False)

seen = []
def positive(value):
    seen.append(value)
    return value > 0

source = iter([1, -1, -2, 3])
check(all(positive(x) for x in source) is False)
check(seen == [1, -1])
check(list(source) == [-2, 3])  # Failing item was already consumed.
seen.clear()
check(all(positive(x) for x in source) is True)  # Now empty, not revalidated.
check(seen == [])

seen.clear()
check(all([positive(x) for x in [1, -1, -2, 3]]) is False)
check(seen == [1, -1, -2, 3])  # List evaluated before all was called.
seen.clear()
source = iter([-1, 2, 3])
check(any(positive(x) for x in source) is True)
check(seen == [-1, 2])
check(list(source) == [3])

# Explicit finite exhaustive report, if iteration and predicate finish normally.
def audit(iterable, predicate):
    count = 0
    rejected = []
    for index, item in enumerate(iterable):
        count += 1
        if not predicate(item):
            rejected.append(index)
    return {'count': count, 'rejected': rejected,
            'nonempty_and_valid': count > 0 and not rejected}

seen.clear()
report = audit(iter([1, -1, -2, 3]), positive)
check(report == {'count': 4, 'rejected': [1, 2], 'nonempty_and_valid': False})
check(seen == [1, -1, -2, 3])
check(audit([], positive) == {'count': 0, 'rejected': [], 'nonempty_and_valid': False})
check(audit([1, 2], positive)['nonempty_and_valid'] is True)

# Short-circuiting can leave an exception in an unevaluated tail.
def tail_error():
    yield False
    raise RuntimeError('tail failed')

g = tail_error()
check(all(g) is False)
try:
    next(g)
except RuntimeError as error:
    check(str(error) == 'tail failed')
else:
    raise AssertionError('expected tail failure')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Covers empty input, truthiness, consumed failing item, unchecked remainder, exhausted-source reuse, eager versus lazy predicate calls, any's stopping point, explicit rejected-index report and an unevaluated tail exception.
- No infinite streams, custom truth conversion, concurrent iteration, exception-accumulating validator, external effects, performance or production data validation was tested. The report stores one index per failed item and has no size cap. It is an example for bounded inputs, not a transaction or reusable validation framework.

## Sources
- [Python 3.14 built-ins](https://docs.python.org/3.14/library/functions.html): all/any contracts and equivalent loops.
- [Python 3.14 functional HOWTO](https://docs.python.org/3.14/howto/functional.html): iterator and generator behavior.
- [Passing generators to all and any](https://stackoverflow.com/questions/57045308/passing-generator-expressions-to-any-and-all): concrete one-shot consumption confusion.
- [Real Python all guide](https://realpython.com/python-all/): short-circuit and empty-input discussion, February 9, 2022; empty-input truth is not treated as illogical or an implementation bug here.
- [Lazy evaluation teaching chapter](https://bnaskrecki.faculty.wmi.amu.edu.pl/math-comp/en/book/python/p3_leniwosc.html): eager-list versus generator contrast; published timings not adopted or reproduced.
- [Iterator nonemptiness question](https://stackoverflow.com/questions/3114252/one-liner-to-check-whether-an-iterator-yields-at-least-one-element): probes can consume an item; suggested one-liners not adopted as nondestructive checks.
