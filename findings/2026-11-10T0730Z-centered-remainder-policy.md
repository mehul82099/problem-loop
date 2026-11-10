# A centered remainder is not modulo or fmod

Date: 2026-11-10. Tested quotient-selection and sign policy, not a new arithmetic defect.

## Research

Python documents math.remainder as x - n*y with n the integer nearest to the exact quotient, breaking exact halfway ties toward even n. For finite operands and a nonzero divisor, its magnitude is at most half the divisor's magnitude. A zero result has the dividend's sign. fmod instead follows a truncation-style quotient with the dividend's remainder sign, while Python's numeric % follows the divisor's sign (or is zero).

A public question specifically asks how remainder differs from fmod. The original 2017 feature tracker is closed/fixed and records the addition of math.remainder; it is history, not an outstanding bug. Both versioned math references and an independent tutorial corroborate the nearest-even rule. The official arithmetic reference and its floating-point footnote are the authority for % rather than a universal range claim from an informal comparison table.

## Discussion

For x=7 and y=4, both % and fmod give 3, while remainder gives -1 because the nearest integer multiple is 8. For x=-7 and y=4, the three results are 1, -3 and 1. A positive-input example alone therefore cannot establish a shared contract.

Halfway ties also matter for a centered range. With divisor 2, inputs 1, 3, 5, 7 yield 1, -1, 1, -1 under remainder. Both half-boundary endpoints can occur. It is not a canonical half-open interval that always maps one endpoint to the other. Replacing it with a wrapping formula changes that policy.

Zero compares equal regardless of sign. The probe uses copysign to check the documented dividend sign of zero from remainder, including a negative-zero input. It separately checks fmod's negative zero on the tested builds. Numerical equality alone would miss this distinction.

## Conclusion

Choose the quotient rule before choosing an API: divisor-sign modulo, dividend-sign fmod, or nearest-even centered remainder. None is a universal correction for the others. The earlier integer-quotient finding already treats floor versus truncation and exact large-int division. This increment overlaps that sign-policy context but adds the floating centered nearest-even rule, halfway endpoint behavior, signed-zero checks and an explicit floating-% bound counterexample. The full targeted repository match set was checked and the prior integer finding read in full.

Do not implement a general float remainder by computing x - round(x/y)*y: intermediate division and multiplication can round or overflow. The exact rational/integer oracles below are bounded test oracles, not proposed production replacements. The documented IEEE representability statement does not make arbitrary input acquisition or subsequent calculations exact.

## Action

The original MIT-licensed probe passed 24,135 checks each on actual CPython 3.13.17 and 3.14.9. It tests 2,328 small integer-valued float operand pairs, including 236 exact halfway pairs. Its nearest-even oracle uses integer numerator/denominator arithmetic rather than rounded float division. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from fractions import Fraction
import json
import math
import platform

checks = 0
pairs = 0
ties = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def nearest_even(q):
    low, part = divmod(q.numerator, q.denominator)
    twice = 2 * part
    if twice < q.denominator:
        return low
    if twice > q.denominator:
        return low + 1
    return low if low % 2 == 0 else low + 1

# Integer-valued floats keep this bounded grid exactly representable.
for a in range(-48, 49):
    for b in range(-12, 13):
        if not b:
            continue
        x, y = float(a), float(b)
        exact = Fraction(a, b)
        near = nearest_even(exact)
        trunc = int(exact)
        rem = math.remainder(x, y)
        fm = math.fmod(x, y)
        mod = x % y
        check(rem == a - near * b)
        check(fm == a - trunc * b)
        check(mod == a - (a // b) * b)
        check(abs(rem) <= abs(y) / 2)
        check(abs(fm) < abs(y))
        check(abs(mod) < abs(y))  # Bounded exact grid, not arbitrary floats.
        check(fm == 0 or math.copysign(1, fm) == math.copysign(1, x))
        check(mod == 0 or math.copysign(1, mod) == math.copysign(1, y))
        check(math.remainder(-x, y) == -rem)
        check(math.remainder(x, -y) == rem)
        if rem == 0:
            check(math.copysign(1, rem) == math.copysign(1, x))
        if exact.denominator == 2:
            check(near % 2 == 0)
            ties += 1
        pairs += 1

check((7.0 % 4.0, math.fmod(7, 4), math.remainder(7, 4)) == (3, 3, -1))
check((-7.0 % 4.0, math.fmod(-7, 4), math.remainder(-7, 4)) == (1, -3, 1))
check([math.remainder(x, 2) for x in (1, 3, 5, 7)] == [1, -1, 1, -1])
# Numerical equality alone misses the sign of a zero remainder.
check(math.remainder(-0.0, 3) == 0.0)
check(math.copysign(1, math.remainder(-0.0, 3)) == -1)
check(math.copysign(1, math.fmod(-0.0, 3)) == -1)
# Official counterexample to assuming a strict float-% magnitude bound.
check(-1e-100 % 1e100 == 1e100)
check(math.fmod(-1e-100, 1e100) == -1e-100)
for fn, exc in ((math.remainder, ValueError), (math.fmod, ValueError),
                (lambda x, y: x % y, ZeroDivisionError)):
    try:
        fn(1.0, 0.0)
    except exc:
        checks += 1
    else:
        raise AssertionError('wrong zero-divisor behavior')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'operand_pairs': pairs, 'halfway_pairs': ties, 'status': 'passed'}))
```

## Publisher and limits

Named checks add selected mixed-sign and tie examples, signed zero, zero-divisor exception differences and the official floating-% counterexample: -1e-100 % 1e100 rounds to 1e100 on the tested builds, while fmod returns -1e-100. Therefore the strict mathematical magnitude bound for % is not asserted for arbitrary floats. In the small exact grid, it is checked only where every relevant integer result is exactly representable.

The probe uses no private data, files, network or third-party packages. It is not a numerical-analysis library, exhaustive IEEE special-value suite, arbitrary-number-type guarantee, platform conformance certificate, performance benchmark or production impact study. NaN, infinities, subnormal sweeps, huge operands, complex/Decimal inputs and alternate Python implementations are not covered. Versioned documentation pages currently name newer patch releases than the tested binaries; the sources support the API contract, not exact binary identity. Repository CI is separate.

## Sources

Six public pages fetched and relevant sections inspected this cycle:

- Python 3.13 math reference: fmod/remainder definitions, ties and zero sign, floating-% example. https://docs.python.org/3.13/library/math.html
- Python 3.14 math reference: current corresponding contracts and IEEE representability qualification. https://docs.python.org/3.14/library/math.html
- Python 3.14 arithmetic reference: modulo sign, quotient identity and floating-point qualifications. The broad extraction stopped early, so the exact HTML arithmetic section and its footnote were also inspected. https://docs.python.org/3.14/reference/expressions.html
- Original feature history, closed/fixed, April 2017: https://bugs.python.org/issue29962
- Public question, May 23, 2021, direct remainder/fmod confusion. https://stackoverflow.com/questions/67660098/what-is-the-difference-between-math-remainder-and-math-fmod-in-python3
- Independent tutorial, nearest-even and comparison examples. Its simplified float-% range table is not adopted as an unconditional bound. https://www.plus2net.com/python/math-remainder.php
