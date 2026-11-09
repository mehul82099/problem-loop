# Integer coercion is not an exact count contract

Date: 2026-11-09. Evidence-backed Python finding, not a new numeric defect.

## Research

Python separates int conversion from the integer index protocol. int can parse text and truncate floats toward zero, while operator.index requires an integer-like object implementing the index protocol. A public question expecting operator.index(1.0) to accept an integral-valued float illustrates why "numeric value looks whole" and "integer type protocol" are different requirements.

## Discussion

| Input | Tested int behavior | Tested index behavior |
| --- | --- | --- |
| 3.9 | 3 | TypeError |
| -3.9 | -3 | TypeError |
| '3' | 3 | TypeError |
| 3.0 | 3 | TypeError |
| Object with only __int__ returning 3 | 3 | TypeError |
| Object with __index__ returning 3 | 3 via fallback | 3 |
| True | 1 | 1 |

Replacing a count check with int(value) can therefore silently change the input: a fractional request becomes an integer, and a text value is parsed even when the API was meant to accept integer-like objects only. That coercion can be intentional, but it needs its own stated rounding and text grammar. The index protocol is not a configurable rounding operation.

The two hooks are not identical. The controlled Both class below returns 2 from __int__ and 4 from __index__; the two operations give different results on both tested builds. An independent tutorial calls the methods identical, but that claim is not used here. Versioned documentation and the primary PEP distinguish their purpose.

The index protocol accepts booleans because bool is an int subclass. It also does not enforce nonnegativity or a small count limit: index(10**100) succeeds in this probe. A reporting/API count rule can still reject bool and require a bounded range after conversion. Those restrictions are application policy, not guarantees supplied by operator.index.

## Conclusion

Choose the input contract before choosing the conversion. If text and fractional values are allowed, define their parsing/rounding separately. If integer-like objects are wanted, use operator.index and then apply the domain's sign and range rules. If only built-in integers are allowed, an exact-type policy is narrower still.

The toy helper accepts index-protocol values, rejects direct bool inputs, and requires 0 through 100 inclusive. That bound is only a demonstration, not a recommended resource limit. Calling __index__ can run custom Python code; this is not a safe deserialization boundary or a way to validate arbitrary untrusted objects without executing their methods. It does not infer units, permissions or resource availability from a valid integer result.

## Action: bounded index-protocol diagnostic

Original standard-library-only code under the repository MIT license. In-memory literal values and controlled classes only; no files, network or allocation based on a huge count. Run without -O so assertions remain enabled.

```python
# Original pure input-contract diagnostic, MIT license (repository LICENSE).
from operator import index
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def raises(kind, fn):
    try:
        fn()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

def bounded_count(value):
    # Toy policy: exact index protocol, no bool, inclusive range 0..100.
    if isinstance(value, bool):
        raise TypeError('boolean is not a count in this contract')
    result = index(value)
    if not 0 <= result <= 100:
        raise ValueError('count outside 0..100')
    return result

class ExactCount:
    def __init__(self, value):
        self.value = value
    def __index__(self):
        return self.value

class Coercible:
    def __int__(self):
        return 3

class Both:
    def __int__(self):
        return 2
    def __index__(self):
        return 4

check(int(3.9) == 3)
check(int(-3.9) == -3)
check(int('3') == 3)
for value in (3., 3.9, -3.9, '3', Coercible()):
    raises(TypeError, lambda: index(value))
    raises(TypeError, lambda: bounded_count(value))
check(int(Coercible()) == 3)
check(int(Both()) == 2)
check(index(Both()) == 4)
check(bounded_count(Both()) == 4)
check(index(True) == 1 and index(False) == 0)
for value in (True, False):
    raises(TypeError, lambda: bounded_count(value))
check(list(range(ExactCount(3))) == [0, 1, 2])
check('abcde'[ExactCount(2)] == 'c')
raises(TypeError, lambda: range(3.))
float_index = 1.0
raises(TypeError, lambda: 'abc'[float_index])
raises(TypeError, lambda: bounded_count(ExactCount(2.5)))
for value in range(-2, 103):
    if 0 <= value <= 100:
        check(bounded_count(value) == value)
        check(bounded_count(ExactCount(value)) == value)
        check(type(bounded_count(ExactCount(value))) is int)
    else:
        raises(ValueError, lambda: bounded_count(value))
        raises(ValueError, lambda: bounded_count(ExactCount(value)))
check(index(10**100) == 10**100)  # Index protocol itself does not impose this cap.
raises(ValueError, lambda: bounded_count(10**100))
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

338 checks passed separately on CPython 3.13.17 and 3.14.9. Includes int truncation/text coercion versus index rejection, controlled hook differences, boolean policy, range/index use, invalid hook return type, all toy inputs -2 through 102, exact-int results and a huge index value rejected by the helper. These are input-contract checks, not a guarantee about third-party classes or every index-consuming API's size limits.

## Sources

1. [Python 3.13 operator reference](https://docs.python.org/3.13/library/operator.html): operator.index and exact-int result since 3.10.
2. [Python 3.14 operator reference](https://docs.python.org/3.14/library/operator.html): corroborating versioned contract.
3. [Python 3.14 data model](https://docs.python.org/3.14/reference/datamodel.html#object.__index__): integer-like index protocol and conversion fallback. Exact section inspected after the broad page fetch stopped early.
4. [Python 3.14 built-ins](https://docs.python.org/3.14/library/functions.html): int conversion/truncation and bool subclass relationship; exact int/bool sections inspected.
5. [PEP 357](https://peps.python.org/pep-0357/): primary rationale for distinguishing integer identity from coercion. Historical Python 2 details are not treated as current signatures.
6. [Public operator.index question](https://stackoverflow.com/questions/54381866/could-someone-give-an-example-for-operator-index), 2019-01-26: independent user evidence for the integral-float expectation, not a test of NumPy here.
7. [Programiz int tutorial](https://www.programiz.com/python-programming/methods/built-in/int): independent truncation example; its claim that __int__ and __index__ are identical is explicitly not adopted.

The contribution is an original bounded count probe, not a new integer protocol. Earlier integer-quotient and text-integer-grammar findings concern different division/parsing contracts; this increment distinguishes object protocols and domain range policy.
