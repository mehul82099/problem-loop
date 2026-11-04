# Decimal(float) preserves the float, not the original decimal spelling

Date: 2026-11-05. A tested input-boundary finding for documented behavior, not a new arithmetic defect.

## Research

The [decimal reference](https://docs.python.org/3/library/decimal.html) says a float input is converted losslessly to its exact decimal equivalent. It also says constructor storage is not limited by context precision. A [developer question](https://stackoverflow.com/questions/32189748/strange-decimal-behavior-while-constructing-from-float-literal) reports the resulting surprise. [CPython issue 125557](https://github.com/python/cpython/issues/125557) discusses a related limit: trapping FloatOperation does not prohibit mixed equality comparisons.

## Discussion

`Decimal(0.1)` cannot recover the text a user originally entered. The argument is already a binary float; converting it exactly preserves that value. If the application owns decimal text, parse that text directly. Converting an already-rounded float to a string is a different policy, not a general recovery of lost input.

Context precision controls arithmetic rounding, not how many digits the ordinary constructor stores. Use an explicit arithmetic or context conversion step when rounding is intended, with a precision and rounding rule chosen for the application. A three-digit demonstration is not a currency policy.

## Conclusion

Keep decimal text until the decimal boundary when that text is the source of truth. FloatOperation can catch accidental float construction and ordering, but it is not a universal float ban: equality is still permitted and explicit `from_float()` conversion remains available. Do not describe a documented comparison result as an incorrect computation.

## Action: reproducible boundary probe

Ran 13 cases on each of CPython **3.13.17** and **3.14.9**, Linux x86_64. They verify the float's exact ratio survives conversion, constructor digits exceed a precision of three, explicit rounding works, two trapped operations raise, equality sets a sticky flag without raising, and explicit float conversion does not set that flag. The context changes are confined to `localcontext()`.

```python
import json
import platform
from decimal import Decimal, FloatOperation, localcontext

with localcontext() as ctx:
    ctx.prec = 3
    ctx.traps[FloatOperation] = False
    exact = Decimal('0.1')
    converted = Decimal(0.1)
    assert converted != exact
    assert converted == Decimal.from_float(0.1)
    assert converted.as_integer_ratio() == (0.1).as_integer_ratio()
    assert len(converted.as_tuple().digits) > ctx.prec
    assert Decimal('1.23456') == Decimal('1.234560')
    assert str(+Decimal('1.23456')) == '1.23'
    assert str(ctx.create_decimal('1.23456')) == '1.23'
    ctx.traps[FloatOperation] = True
    try:
        Decimal(0.1)
    except FloatOperation:
        pass
    else:
        raise AssertionError('implicit float construction was accepted')
    try:
        exact < 0.1
    except FloatOperation:
        pass
    else:
        raise AssertionError('mixed ordering was accepted')
    ctx.clear_flags()
    assert (exact == 0.1) is False
    assert ctx.flags[FloatOperation] is True
    ctx.clear_flags()
    assert Decimal.from_float(0.1) == converted
    assert ctx.flags[FloatOperation] is False
print(json.dumps({'python': platform.python_version(), 'result': 'passed', 'cases': 13}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked reports retain their authorship.
- This probe does not implement a financial parser, scale checks, finite-number validation, quantization policy, or protection against large input. Numeric strings still need application validation.
- Only these finite inputs and two CPython builds were tested. No production data, third-party decimal implementation or timing benchmark was used.
- Flags are sticky: the probe clears them before attributing a flag to a particular operation. A trap alone is not evidence that every mixed use was blocked.
