# Accurate float summation does not recover decimal intent

Date: 2026-11-09. Evidence-backed Python finding, not a new sum defect.

## Research

The Python math reference describes `fsum` as an accurate floating-point sum that tracks multiple partial sums. The floating-point tutorial distinguishes accurate summation from representation error already present in the inputs. Current `sum` also matters: its float algorithm improved in Python 3.12. Older tutorials comparing it with a naive addition loop must not be assumed to describe current builds.

## Discussion

Consider decimal text `0.1`, `0.2`, `-0.3`. Summing Decimal values made directly from those strings gives zero under the default context for this sample. Converting the strings to binary floats first gives different exact rational inputs. Their exact sum is **1/36028797018963968**, not zero.

On both tested builds, `sum` and `fsum` return that tiny nonzero value, while a sequential `total += value` loop returns twice as much. The nonzero accurate answer is not evidence that fsum failed: it accurately reflects the represented binary inputs. `Decimal.from_float(0.1)` likewise preserves the float's approximation rather than recovering the source decimal text.

For a separate cancellation sample, `[1e16, 1.0, -1e16]`, fsum returns 1.0 while the simple loop returns 0.0. This demonstrates one local advantage over a naive loop, not a claim that current sum always differs from fsum or that fsum returns an exact rational number.

## Conclusion

| Required contract | Approach | Boundary |
| --- | --- | --- |
| Accurate total of represented binary floats | Consider `math.fsum` | Result is still a float with documented platform caveats |
| Exact decimal input semantics | Preserve decimal strings and use Decimal with an explicit context | Converting floats afterward does not restore source spelling |
| Exact rational value of existing floats | `Fraction.from_float`, then rational summation | Represents the floats, not their presumed decimal intent |
| Approximate comparison with zero | Domain-chosen error/tolerance policy | A display rounding rule is not a data model |

Do not erase small residuals automatically or change a financial/measurement policy on the basis of these examples. Decimal arithmetic also has a precision context; the sample's exact zero is not a promise that all Decimal operations are unrounded. Keep input representation, summation algorithm and comparison policy separate.

## Action: exact-input oracle diagnostic

Original standard-library-only code, covered by the repository MIT license. Uses Fraction as an oracle for the exact values of these finite floats, then converts the exact sum once for the selected comparison.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from decimal import Decimal
from fractions import Fraction
from itertools import permutations
import json
import math
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def sequential(values):
    total = 0.0
    for value in values:
        total += value
    return total

def exact_inputs(values):
    return sum((Fraction.from_float(value) for value in values), Fraction())

texts = ('0.1', '0.2', '-0.3')
values = tuple(map(float, texts))
exact = exact_inputs(values)
check(exact != 0)
check(sum(map(Decimal, texts)) == Decimal(0))
check(math.fsum(values) == float(exact))
check(math.fsum(values) != 0.0)
check(sequential(values) != math.fsum(values))
check(Decimal.from_float(0.1) != Decimal('0.1'))
check(Fraction.from_float(0.1) != Fraction(1, 10))
large = (1e16, 1.0, -1e16)
check(sequential(large) == 0.0)
check(math.fsum(large) == 1.0)
# Agreement with an exact-input oracle for this finite sample only.
for case in [values, large, (0.5, 0.25, -0.125), (1.0, 2**-53, 2**-53)]:
    oracle = float(exact_inputs(case))
    for order in permutations(case):
        check(math.fsum(order) == oracle)
check(math.fsum([]) == 0.0)
check(math.fsum([0.1] * 3) != 0.3)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'binary_input_exact_sum': str(exact),
                  'sum': sum(values), 'fsum': math.fsum(values),
                  'sequential': sequential(values)}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **35 checks passed per build**. Four three-value cases, each with six permutation positions, agree with the exact-input oracle under fsum on these builds. Other checks distinguish decimal strings, floats, cancellation, sequential addition and empty input. The output records current sum and fsum agreeing for the decimal-text sample.

This finite test is not a universal correct-rounding proof, a speed benchmark or a guarantee across platforms. The math documentation notes that extended-precision double rounding can affect a least significant bit on some builds. NaNs, infinities and overflow are outside this probe. Repository CI is separate.

## Publisher and sources

Published deliverable: this finding and runnable diagnostic. Six sources were read. Historical reports describe confusion and algorithm changes, not a new regression or measured incident frequency.

1. [Python 3.14 math.fsum](https://docs.python.org/3.14/library/math.html#math.fsum), primary reference: partial sums and platform caveats.
2. [Python 3.14 sum](https://docs.python.org/3.14/library/functions.html#sum), primary reference: Python 3.12 accuracy change. The exact section was inspected separately after a broad fetch stopped earlier.
3. [Python 3.14 floating-point tutorial](https://docs.python.org/3.14/tutorial/floatingpoint.html), primary explanation: input representation, Decimal/Fraction alternatives and accurate summation.
4. [CPython issue 126181](https://github.com/python/cpython/issues/126181), public project discussion, 2024: an apparently surprising nonzero sum can be exact for the supplied floats. No changes to that repository are made here.
5. [sum versus fsum in Python 3.12](https://stackoverflow.com/questions/77252117/what-is-the-difference-between-built-in-sum-and-math-fsum-in-python-3-12), community question: current algorithm distinction. Community speed estimates are not adopted as local benchmarks.
6. [Real Python sum tutorial](https://realpython.com/python-sum-function/), independent tutorial: fsum as an alternative for float totals. Any older naive-sum examples are version-sensitive; current behavior here comes from the two actual builds and official reference.
