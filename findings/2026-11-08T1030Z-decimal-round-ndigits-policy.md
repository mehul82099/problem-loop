# Decimal round(d) and round(d, 0) can choose different results

Date: 2026-11-08. Scope: the tested ordinary float and finite Decimal examples, not a business rounding rule.

## Research

Public questions about round() mix two distinct concerns: tie policy and binary representation. The current built-in reference documents ties to even for built-in numeric rounding and warns that round(2.675, 2) gives 2.67 because of the stored float value. The Decimal reference adds another boundary: omitting ndigits, or passing None, rounds to an int using ties to even and ignores the Decimal context's rounding mode. Passing an integer ndigits returns a Decimal and respects that context.

## Discussion

Under a local ROUND_HALF_UP context, round(Decimal('2.5')) is the integer 2, while round(Decimal('2.5'), 0) is Decimal('3'). This is a numeric policy difference, not merely a return-type difference. Under ROUND_DOWN, round(Decimal('2.9')) is 3 while round(Decimal('2.9'), 0) is Decimal('2'). Negative examples are tested too. A wrapper that replaces a missing ndigits argument with zero can silently change both type and result.

Binary representation is separate. Decimal.from_float(2.675) records a value below the exact decimal text Decimal('2.675'). Applying the same two-place decimal rounding to those two inputs can therefore differ. Formatting the float to two places also prints 2.67 in the probe; display formatting does not reconstruct the original decimal intent.

Some historical community text describes ties away from zero while quoting older Python behavior. It is not used as the current Python 3 policy. The independent guide describes ties-to-even and explicit Decimal rounding modes; no general claim that a policy eliminates bias for every dataset is adopted. Earlier decimal findings covered float construction and quantize's exponent contract. This increment focuses on the omitted-versus-zero ndigits boundary, with representation included only to distinguish the two causes of surprise.

## Conclusion

Choose input representation, rounding policy and output type explicitly. For Decimal, preserve the distinction between round(d) and round(d, 0) when designing wrappers or refactoring calls. Use a local context or an explicit quantize rounding argument when that is the intended Decimal contract. No default mode is recommended for measurements, money, law or accounting; those rules must come from the application's own requirements.

## Action

The original MIT-licensed diagnostic passed 24 checks each on CPython 3.13.17 and 3.14.9. It tests float half-ties, return types, one binary approximation, Decimal omitted/None/zero behavior under HALF_UP, DOWN and HALF_EVEN, signed cases and explicit quantize policy. The local context prevents changes leaking into other Decimal work. This is not an exhaustive rounding conformance suite, arbitrary-range helper, benchmark or financial calculation.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from decimal import Decimal, localcontext, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

check([round(x) for x in (0.5, 1.5, 2.5, 3.5)] == [0, 2, 2, 4])
check([round(x) for x in (-0.5, -1.5, -2.5, -3.5)] == [0, -2, -2, -4])
check(type(round(2.5)) is int)
check(type(round(2.5, 0)) is float)
check(round(2.675, 2) == 2.67)
check(Decimal.from_float(2.675) < Decimal('2.675'))
check(format(2.675, '.2f') == '2.67')

with localcontext() as ctx:
    ctx.prec = 28
    ctx.rounding = ROUND_HALF_UP
    d = Decimal('2.5')
    check(round(d) == 2)
    check(type(round(d)) is int)
    check(round(d, None) == 2)
    check(round(d, 0) == Decimal('3'))
    check(type(round(d, 0)) is Decimal)
    check(round(Decimal('-2.5')) == -2)
    check(round(Decimal('-2.5'), 0) == Decimal('-3'))
    check(Decimal('2.675').quantize(Decimal('0.01')) == Decimal('2.68'))
    check(Decimal.from_float(2.675).quantize(Decimal('0.01')) == Decimal('2.67'))
    check(Decimal('2.5').quantize(Decimal('1'), rounding=ROUND_HALF_EVEN) == Decimal('2'))
    check(ctx.rounding == ROUND_HALF_UP)
    ctx.rounding = ROUND_DOWN
    check(round(Decimal('2.9')) == 3)
    check(round(Decimal('2.9'), 0) == Decimal('2'))
    check(round(Decimal('-2.9')) == -3)
    check(round(Decimal('-2.9'), 0) == Decimal('-2'))
    ctx.rounding = ROUND_HALF_EVEN
    check(round(Decimal('2.5'), 0) == Decimal('2'))
    check(round(Decimal('3.5'), 0) == Decimal('4'))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and deterministic probe. Documented behavior, not a new defect or upstream fix. No private data, third-party packages or network calls are needed by the probe. Run without optimization so assertions remain active.

## Sources

Six public sources inspected this cycle:

- Official Python 3.14 round contract; exact HTML section separately inspected after full-page text extraction ended early: https://docs.python.org/3.14/library/functions.html#round
- Official binary floating-point explanation: https://docs.python.org/3.14/tutorial/floatingpoint.html
- Official Decimal round contract, context and quantize modes: https://docs.python.org/3.14/library/decimal.html
- Historical community question about 2.675; old tie-policy quotation is not treated as current: https://stackoverflow.com/questions/14249971/why-is-pythons-round-so-strange
- Community Python 3 half-even question: https://stackoverflow.com/questions/10825926/python-3-x-rounding-behavior
- Independent guide on ties, representation and explicit Decimal modes: https://codeforgeek.com/round-numbers-in-python/
