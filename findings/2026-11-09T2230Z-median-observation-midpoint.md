# A median can be an interpolated number rather than an observed item

Date: 2026-11-10. Tested Python statistics policy, not a new arithmetic defect.

## Research

The versioned statistics references define median as the middle value for odd counts and the mean of the two middle values for even counts. median_low and median_high instead choose observed values. PEP 450 records these separate APIs. A January 2019 tracker discussion about integer-versus-float return types was closed as not a bug; it documents a real expectation mismatch, not a current regression. PyMOTW and a community API reference corroborate the separate low/high policies.

## Discussion

For `[1, 3, 5, 7]`, median returns 4.0, which is not one of the observations. Low median returns 3 and high median returns 5. Choosing one merely to avoid a float silently changes the statistic. Even `[1, 1]` returns a float on these builds, whereas the singleton `[1]` returns the original integer value.

Precision is a separate boundary. The integer `2**53 + 1` is exact, and the odd singleton median preserves it. For two equal copies, the tested even median rounds through float and is no longer equal to that integer. Converting the integer observations to Fraction before taking median preserves the exact rational value for this sample. It does not restore precision already lost in float inputs.

| Required meaning | Deliberate API/data choice | Boundary |
| --- | --- | --- |
| Conventional middle-two average | median | Even integer inputs can produce float |
| Lower observed center | median_low | Different statistic when middle values differ |
| Upper observed center | median_high | Different statistic when middle values differ |
| Exact rational midpoint of exact integer observations | Fraction inputs before median | More arithmetic/storage cost; not a universal data model |

Do not convert a rounded float median to int and call that a repair. Rounding, truncating and choosing an observed order statistic are separate policies. Numeric-looking identifiers also do not automatically make arithmetic interpolation meaningful.

## Conclusion

State whether the result may lie between observations and which numeric representation is required. Keep missing-value and population-selection policies explicit. The official reference warns that mixed numeric types are undefined/implementation-dependent and that NaNs disrupt sort/count-based functions. This probe uses homogeneous finite integers or Fractions only.

The earlier NaN ordering finding already calls median after cleaning one sample; the quantile finding addresses estimator identity and small samples; recent Fraction and float findings cover representation loss. Those overlaps are acknowledged. This increment tests median versus observed low/high centers and odd/even numeric type/precision changes. It does not claim a new float limitation or replace a statistical methodology review.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 8,747 checks across 1,092 ordered input sequences plus selected precision/type/empty cases. Sequence lengths 1..6 over integers -2, 0 and 3 are exhaustive. Sorted central indexes provide the low/high oracle; exact Fraction midpoints verify average results. Reverse-order and iterator variants are checked.

The tiny grid's integer/half-integer averages are exactly representable as floats. The separate large-integer sample intentionally crosses that precision boundary. No claim that all integer medians are exact, all Fraction inputs are cheap, or all numeric extensions behave alike. Run without optimization so assertions remain active.

```python
from fractions import Fraction
from itertools import product
from statistics import median, median_low, median_high, StatisticsError
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(median([1, 3, 5, 7]) == 4.0)
check(median([1, 3, 5, 7]) not in [1, 3, 5, 7])
check(type(median([1])) is int)
check(type(median([1, 1])) is float)
# Same exact integer input, even length introduces float rounding.
large = 2**53 + 1
check(median([large]) == large)
check(median([large, large]) != large)
check(median_low([large, large]) == median_high([large, large]) == large)
check(median([Fraction(large), Fraction(large)]) == Fraction(large))

cases = 0
for length in range(1, 7):
    for values in product((-2, 0, 3), repeat=length):
        ordered = sorted(values)
        low = ordered[(length - 1) // 2]
        high = ordered[length // 2]
        expected = Fraction(low + high, 2)
        check(median_low(values) == low)
        check(median_high(values) == high)
        check(median_low(values) in values and median_high(values) in values)
        check(median(values) == expected)  # tiny exactly representable half-integers
        exact = [Fraction(x) for x in values]
        check(median(exact) == expected)
        check(median(iter(exact)) == expected)
        check(median(list(reversed(values))) == expected)
        check(low <= expected <= high)
        cases += 1
for function in (median, median_low, median_high):
    try:
        function([])
    except StatisticsError:
        check(True)
    else:
        raise AssertionError('empty input accepted')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'sequences': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Exact published draft bytes are compared and committed code is extracted and rerun on both named builds.
- Synthetic in-memory data only; no user records, files or network. No timing, arbitrary-input resource bound or production statistics guarantee.
- No NaNs, infinities, mixed types, Decimal contexts, grouped medians, custom comparisons or sampling uncertainty tested. An accepted input is not evidence that observations are representative.
- Tracker 35698's first report contains an odd/even wording error; the finding uses the official definition and observed behavior, not that typo. The historical issue is closed, not presented as outstanding work.

## Sources

1. Python 3.13 statistics reference, median/low/high and type caveats: https://docs.python.org/3.13/library/statistics.html
2. Python 3.14 statistics reference, same applicable contract: https://docs.python.org/3.14/library/statistics.html
3. PEP 450 primary API rationale: https://peps.python.org/pep-0450/
4. Historical tracker 35698 (January 2019), return-type discussion, closed not a bug: https://bugs.python.org/issue35698
5. PyMOTW independent statistics guide, median variants: https://pymotw.com/3/statistics/
6. Community median_low API reference and examples: https://pydocs.org/statistics/median_low
