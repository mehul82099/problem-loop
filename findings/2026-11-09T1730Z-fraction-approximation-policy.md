# Fraction denominator limits approximate; they do not recover input intent

Date: 2026-11-10. Evidence-backed Python numeric-contract finding, not a new arithmetic defect.

## Research

The versioned fractions references distinguish exact conversion of a supplied float from parsing decimal text. They define `limit_denominator(M)` as the closest rational with denominator at most M. A March 2016 developer question asks why `Fraction(2.6)` differs from `Fraction('2.6')`; a July 2013 mailing-list exchange discusses the same conversion surprise. An independent tutorial demonstrates approximation with several denominator bounds. These are longstanding documented behaviors, not evidence of a current regression.

## Discussion

`Fraction(1.1)` exactly preserves the already-rounded binary float. `Fraction('1.1')` and `Fraction(Decimal('1.1'))` instead represent 11/10. Choosing a denominator bound of 10 happens to map that float to 11/10, but that does not authenticate the original spelling or intent.

In particular, both 49/100 and 51/100 become 1/2 with bound 2. Distinct exact inputs collapse to the same approximation. An exact rational such as 1/7 also changes when limited to denominator 3. The method is not merely reducing a fraction to lowest terms: Fraction construction already normalizes the representation.

| Required meaning | Explicit choice | Limit |
| --- | --- | --- |
| Preserve existing finite float value exactly | `Fraction(value)` or its integer ratio | Does not restore decimal intent |
| Preserve owned decimal input text | Parse that text directly | Validate application grammar and size separately |
| Find a nearby bounded-denominator rational | `limit_denominator(M)` | Domain must select M and acceptable error |

The earlier Decimal/float boundary and float-summation findings already explain representation loss, and the summation probe already uses Fraction as an oracle. That overlap is intentional and acknowledged. This increment tests a different contract: bounded rational approximation, its many-to-one behavior, and nearest-distance checks. It does not claim a new discovery about binary floats.

## Conclusion

Keep exact conversion and approximation separate. A smaller denominator can be useful for a measurement or display, but the chosen bound is a policy, not proof of the original rational. If exact source text matters, preserve it before float conversion. Do not silently apply a guessed bound to financial or measurement data.

## Action

Original standard-library-only diagnostic code under this repository's MIT license. On actual CPython 3.13.17 and 3.14.9, each run passed 10,411 checks: 401 decimal inputs, 2,400 rational/bound oracle cases and selected counterexamples/error cases.

The independent oracle enumerates each denominator from 1 through the bound and the two adjacent integer numerators. For fixed positive q, no other integer numerator can be closer to x*q. All distances are exact Fraction values, so the oracle does not introduce float rounding. It verifies minimum distance without claiming a particular answer when equal-distance ties exist. Duplicate reduced candidates are harmless. Run without optimization so assertions remain active.

```python
from fractions import Fraction
from decimal import Decimal
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

# Constructor preserves the supplied value, not a guessed original spelling.
check(Fraction(1.1) == Fraction(*(1.1).as_integer_ratio()))
check(Fraction(1.1) != Fraction(11, 10))
check(Fraction('1.1') == Fraction(Decimal('1.1')) == Fraction(11, 10))
check(Fraction(1.1).limit_denominator(10) == Fraction(11, 10))
# Different exact inputs collapse to the same limited result.
check(Fraction(49, 100).limit_denominator(2) == Fraction(51, 100).limit_denominator(2) == Fraction(1, 2))
check(Fraction(1, 7).limit_denominator(3) != Fraction(1, 7))
check(Fraction(1, 7).limit_denominator(7) == Fraction(1, 7))

# Exact decimal text versus already-rounded float for 401 hundredths.
for n in range(-200, 201):
    text = str(Decimal(n) / Decimal(100))
    check(Fraction(text) == Fraction(n, 100))
    value = float(text)
    check(Fraction(value) == Fraction(*value.as_integer_ratio()))

# Independent bounded nearest-distance oracle: for each denominator q,
# the closest numerator must be floor(x*q) or its successor.
# Compare distance, deliberately making no public tie-breaking promise.
cases = 0
for n in range(-12, 13):
    for d in range(1, 13):
        x = Fraction(n, d)
        for bound in range(1, 9):
            candidates = []
            for q in range(1, bound + 1):
                p = (x.numerator * q) // x.denominator
                candidates.extend((Fraction(p, q), Fraction(p + 1, q)))
            result = x.limit_denominator(bound)
            check(1 <= result.denominator <= bound)
            check(abs(result - x) == min(abs(c - x) for c in candidates))
            check(result.limit_denominator(bound) == result)
            check(x.denominator > bound or result == x)
            cases += 1
for bad in (0, -1):
    try:
        Fraction(1, 3).limit_denominator(bad)
    except ValueError:
        check(True)
    else:
        raise AssertionError('nonpositive bound accepted')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'oracle_cases': cases, 'decimal_inputs': 401, 'status': 'passed'}))
```

## Publisher checks and limits

- Versioned official references, public question, mailing-list thread, independent tutorial and floating-point background inspected. The independent tutorial's informal warnings do not override the official closest-rational contract.
- Published probe checks exact draft bytes and is rerun after readback. Only the named builds and bounded finite samples were tested, not every rational, implementation or numeric extension.
- No benchmark, financial parser, arbitrary-input service, or resource-exhaustion protection is supplied. The small oracle is a test, not the library algorithm or a production replacement. Large numerators/denominators may cost substantial time and memory.
- No original decimal spelling or error tolerance can be inferred from a float alone. No external data, network access, files or mutable decimal context in the probe.

## Sources

1. Python 3.13 fractions reference, exact constructors and closest bounded denominator: https://docs.python.org/3.13/library/fractions.html
2. Python 3.14 fractions reference, same applicable contracts: https://docs.python.org/3.14/library/fractions.html
3. Python floating-point tutorial, multiple decimal spellings share one float: https://docs.python.org/3/tutorial/floatingpoint.html
4. Stack Overflow developer question (March 27, 2016), string versus float input: https://stackoverflow.com/questions/36249335/why-is-there-a-difference-in-result-for-numeric-stringfloat-and-float-instance
5. Python-list discussion (July 2013), exact Fraction conversion and approximation: https://mail.python.org/pipermail/python-list/2013-July/803410.html
6. Real Python tutorial (October 11, 2021), denominator-bound examples: https://realpython.com/python-fractions/
