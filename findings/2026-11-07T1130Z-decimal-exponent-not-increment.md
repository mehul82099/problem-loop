# Decimal.quantize aligns exponents, not arbitrary increments

## Research
Python documents quantize as rounding to the exponent of its second operand. Decimal('0.05') therefore requests two fractional decimal places, not membership in a grid of multiples of 0.05. Public questions about rounding to 0.05 show why those operations are easy to confuse. Using decimal strings avoids an initial binary-float conversion, but it does not change this method's contract.

## Discussion
The probe quantizes 1.03 with 0.01, 0.05 and 0.99: all have the same exponent and leave that value unchanged. Quantizing 1.037 with 0.05 under ROUND_HALF_UP gives 1.04, still not a multiple of 0.05. The coefficient is not an increment instruction. Operand representation also matters: 0.050 requests exponent -3, and 5 requests exponent 0 rather than multiples of five.

A separate illustrative calculation divides by a fixed 0.05 step, rounds the unit count with an explicit policy and multiplies back. The small exact fixtures include positive/negative ties and already-aligned values. HALF_UP and HALF_EVEN produce different answers for the same midpoint. Neither policy is selected here as a legal, financial or application requirement.

## Conclusion
Keep decimal-place formatting, increment membership and tie policy separate. Use quantize for an exponent contract; implement and test the actual grid contract when increments are required. Scaling arithmetic still obeys Decimal context precision, so a generic divide-round-multiply recipe needs range and precision analysis before use on arbitrary inputs or steps. This is documented behavior, not a new defect or a general-purpose rounding library.

## Action: executable probe
Original code under this repository's MIT license. In-memory Decimal values only. Run without Python optimization so assertions remain enabled.

```python
from decimal import Decimal as D, InvalidOperation, ROUND_HALF_EVEN, ROUND_HALF_UP, localcontext
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

with localcontext() as ctx:
    ctx.prec = 28  # Enough for these small fixtures, not arbitrary input.
    ctx.rounding = ROUND_HALF_EVEN
    ctx.traps[InvalidOperation] = True
    x = D('1.03')
    check(x.quantize(D('0.05')) == x)
    check(x.quantize(D('0.01')) == x.quantize(D('0.05')))
    check(x.quantize(D('0.99')) == x)
    check(x.quantize(D('0.05')) % D('0.05') != 0)
    check(D('1.037').quantize(D('0.05'), rounding=ROUND_HALF_UP) == D('1.04'))
    check(D('1.03').quantize(D('5')) == D('1'))
    check(D('17').quantize(D('1E1')) == D('2E1'))
    check(D('1.2').quantize(D('0.050')).as_tuple().exponent == -3)

    # Fixed zero-origin 0.05 grid; explicit illustrative tie policy.
    # This is not an arbitrary-increment or unlimited-precision routine.
    step = D('0.05')
    fixtures = [('1.02', '1.00'), ('1.03', '1.05'),
                ('1.025', '1.05'), ('-1.025', '-1.05'),
                ('1.05', '1.05'), ('0', '0.00')]
    for raw, expected in fixtures:
        units = (D(raw) / step).to_integral_value(rounding=ROUND_HALF_UP)
        result = units * step
        check(result == D(expected))
        check(result % step == 0)
    tie = D('1.025') / step
    check(tie.to_integral_value(rounding=ROUND_HALF_EVEN) * step == D('1.00'))
    check(tie.to_integral_value(rounding=ROUND_HALF_UP) * step == D('1.05'))

    # Exact string construction does not remove arithmetic precision limits.
    ctx.prec = 2
    try:
        D('123.45').quantize(D('0.01'))
    except InvalidOperation:
        too_wide = True
    else:
        too_wide = False
    check(too_wide)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 23 checks passed on CPython 3.13.17 and 3.14.9.
- Covers equal-exponent quantums, off-grid results, coefficient/exponent distinction, retained trailing-zero exponent, fixed-grid examples, positive/negative ties, HALF_EVEN versus HALF_UP and a controlled precision failure.
- Only finite small exact string fixtures, one positive fixed step and a zero-origin grid were tested. No arbitrary increment helper, parser validation, NaN/infinity handling, nonzero grid origin, changing tick bands, jurisdictional rule, payment, trade or performance claim. Low precision can signal InvalidOperation; the probe explicitly enables that trap.

## Sources
- [Python 3.14 decimal](https://docs.python.org/3.14/library/decimal.html): quantize exponent contract, precision failure and rounding mode definitions.
- [CPython _pydecimal.py, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/_pydecimal.py): reference implementation context; not a claim that this pure-Python implementation ran in the tested builds.
- [Round Python Decimal to nearest 0.05](https://stackoverflow.com/questions/37825909/round-python-decimal-to-nearest-0-05): June 15, 2016 public increment-rounding question. Broad generic recipes are limited here to the tested fixed step/range.
- [Decimal rounding to a whole unit](https://stackoverflow.com/questions/3935661/python-decimals-rounding-to-nearest-whole-dollar-no-cents-with-round-half): community explanation of exponent selection and separate display precision.
- [Decimal precision versus tick size](https://algoway.trade/blog/python-decimal-order-price-precision.html): independent October 24, 2026 explanation of exponent versus grid and precision/origin caveats. No external trading rules or service claims are used here.
- [Python ROUND_05UP discussion](https://stackoverflow.com/questions/13106953/python-round-05up): community distinction among rounding policies and increment requirements. A rounding mode's name alone does not define a 0.05 grid.
