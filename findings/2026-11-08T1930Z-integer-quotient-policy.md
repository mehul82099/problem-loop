# Integer quotient policy: floor is not truncation, and float is not exact

Date: 2026-11-09. Evidence-backed Python finding, not a new arithmetic defect.

## Research

The Python arithmetic reference specifies that integer `/` returns a float while integer `//` returns a floored integer quotient. `divmod(a, b)` pairs that floor quotient with `a % b`. Public questions show two distinct mistakes: assuming floor means truncation toward zero for negative values, and converting a large integer quotient through float before calling int.

## Discussion

For -7 divided by 3, floor division gives -3 with remainder 2. A truncation-toward-zero contract instead gives -2 with remainder -1. Both reconstruct the dividend as quotient times divisor plus remainder; that identity alone cannot identify the required rounding policy. The remainder sign and quotient rule must be named too.

`int(a / b)` is not a general exact integer truncation implementation. `/` introduces a floating-point result before int sees it. On the tested builds, `int((2**60 + 1) / 1)` loses the final unit, while integer division preserves it. Applying int afterward cannot recover information already rounded away.

## Conclusion

| Desired result | Appropriate policy | Boundary |
| --- | --- | --- |
| Floor quotient and matching remainder | Integer `divmod(a, b)` | Remainder has divisor's sign or is zero |
| Truncation-toward-zero quotient | Integer-only magnitude division plus sign | Remainder has dividend's sign or is zero |
| Exact fractional quotient | A rational representation such as Fraction | Different output type and cost |
| Approximate real-valued quotient | `/` | Floating-point precision and range apply |

Do not replace one policy with another just because positive examples agree. This helper accepts plain built-in ints, excludes bool and custom numeric classes, preserves zero-divisor errors, and defines no fixed-width overflow or float/Decimal behavior. It is an option only when truncation toward zero is the intended contract, not a correction to Python's floor semantics.

## Action: exact truncating quotient/remainder helper

Original code is covered by the repository MIT license. Standard-library only. The implementation uses no float; the test oracle uses exact Fraction conversion to int.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from fractions import Fraction
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def trunc_divmod(a, b):
    """Plain ints only; quotient toward zero, remainder sign of dividend."""
    if type(a) is not int or type(b) is not int:
        raise TypeError('plain integer operands required')
    q = abs(a) // abs(b)  # Preserves ZeroDivisionError for zero divisor.
    if (a < 0) != (b < 0):
        q = -q
    return q, a - q * b

check(divmod(-7, 3) == (-3, 2))
check(trunc_divmod(-7, 3) == (-2, -1))
check(divmod(7, -3) == (-3, -2))
check(trunc_divmod(7, -3) == (-2, 1))
check(trunc_divmod(-7, -3) == (2, -1))
check(trunc_divmod(0, -3) == (0, 0))
large = 2**60 + 1
check(large // 1 == large)
check(int(large / 1) != large)
check(trunc_divmod(-large, 1) == (-large, 0))
for a in range(-20, 21):
    for b in range(-9, 10):
        if b == 0:
            continue
        q, r = trunc_divmod(a, b)
        check(q == int(Fraction(a, b)))  # Exact rational oracle, no float.
        check(a == q * b + r)
        check(abs(r) < abs(b))
        check(r == 0 or (r > 0) == (a > 0))
        fq, fr = divmod(a, b)
        check(a == fq * b + fr)
        check(fr == 0 or (fr > 0) == (b > 0))
for a, b, exc in [(1, 0, ZeroDivisionError), (True, 2, TypeError),
                  (1, 2.0, TypeError), ('1', 2, TypeError)]:
    try:
        trunc_divmod(a, b)
    except exc:
        checks += 1
    else:
        raise AssertionError(f'expected {exc.__name__}')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **4,441 checks passed per build**. The finite grid covers dividends -20 through 20 and nonzero divisors -9 through 9, totaling 738 operand pairs. Six checks per pair cover the exact rational oracle, reconstruction identity, remainder magnitude, and the different remainder-sign policies. Selected sign examples, a large-integer float counterexample and error/type cases complete the probe.

This grid and selected cases are not a proof for arbitrary numeric classes or a performance benchmark. Repository CI is separate from the local runs.

## Publisher and sources

Published deliverable: this finding and runnable helper/probe. Six public pages were read; longstanding documented behavior is not evidence of a new regression or production incident rate.

1. [Python 3.14 arithmetic reference](https://docs.python.org/3.14/reference/expressions.html#binary-arithmetic-operations), primary documentation: integer division types, floor semantics, modulo sign and identity. The exact section was inspected after the broad fetch stopped before it.
2. [Python 3.14 divmod reference](https://docs.python.org/3.14/library/functions.html#divmod), primary documentation: integer quotient/remainder pair.
3. [PEP 238](https://peps.python.org/pep-0238/), primary design: separating true division from floor division. Historical migration details are not presented as current behavior.
4. [Dividing large integers](https://discuss.python.org/t/dividing-large-integers/105649), community discussion, 2026: converting a large quotient through float can change it; current reference remains the authority.
5. [Real Python modulo tutorial](https://realpython.com/python-modulo-operator/), independent explanation, 2020: floor versus truncation and remainder-sign conventions. This probe is limited to built-in ints rather than all numeric types.
6. [Large-int math.floor question](https://stackoverflow.com/questions/17076401/python-math-floor-not-producing-correct-values-with-large-ints), community evidence: intermediate floating-point precision loss. Older-version example details are not copied as a current specification.
