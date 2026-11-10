# A supplied variance center is trusted, not checked against the sample

Date: 2026-11-10. Tested statistics precondition, not a new variance defect.

## Research

Python's versioned statistics references say variance's optional xbar should be the sample mean and is not verified. They distinguish sample variance's n-1 divisor from pvariance's n divisor. Historical tracker 40855 records a fixed bug where supplied centers were effectively ignored; its old output is not the current contract. Tracker 36099 discusses sample/population mean terminology and is closed as a duplicate. A community API reference and independent tutorial corroborate precomputed-mean usage.

## Discussion

For observations `[1, 3]`, variance is 2 and pvariance is 1. Passing the correct sample mean 2 to variance leaves the result at 2; it does not switch the divisor to n. Passing 0 instead returns 10 on the tested builds, without rejecting the incorrect sample mean.

The explicit center is therefore a precondition, not extra validation. A stale mean from another filter, dataset or time window can silently change the result. If no reliable precomputed mean is available, omit xbar. Do not select a center just because its result looks preferable.

For exact finite rational observations with true sample mean m, supplying m+d changes the tested squared-deviation sum by n*d*d. With variance's n-1 divisor, the result increases by n*d*d/(n-1). The probe verifies that identity with Fraction arithmetic. This explains the local counterexample; it is not a statistical justification for arbitrary recentering.

| Intended calculation | Explicit choice | Boundary |
| --- | --- | --- |
| Sample variance about its sample mean | variance(data) | Needs at least two observations |
| Same calculation with known sample mean | variance(data, xbar=sample_mean) | Caller must ensure it belongs to this dataset |
| Population variance | pvariance(data) | Different divisor; not automatically preferable |

If a genuine population mean is known independently, read pvariance's mu contract and choose the estimator from the study design. Supplying xbar to variance does not signal that different knowledge or change its divisor. This finding does not choose a statistically valid estimator for an unspecified application.

## Conclusion

Retain provenance of precomputed statistics: observations, filters and numeric representation must match. A successful call does not certify those preconditions. The official docs also warn about mixed numeric types; this diagnostic uses homogeneous exact Fractions for the grid rather than extending results to arbitrary numbers.

Earlier median/quantile findings already explain explicit statistical policy, and Fraction/float findings explain representation boundaries. Those overlaps are acknowledged. This increment adds the unchecked precomputed variance center, fixed historical behavior and exact center-shift identity. It does not claim new methodology or an unresolved bug.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 4,688 checks across 360 ordered sequences and 1,080 shifted-center cases, plus selected examples and insufficient-input cases. Lengths 2..5 over -1, 0 and 2 are exhaustive. Centers and sums are exact rational values; iterator input with the correct center is checked separately.

This is a bounded formula/precondition test, not a numerical benchmark, confidence interval, bias study or independent verification of the library's general algorithm. Run without optimization so assertions remain active.

```python
from fractions import Fraction as F
from itertools import product
from statistics import variance, pvariance, mean, StatisticsError
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(variance([1, 3]) == 2)
check(pvariance([1, 3]) == 1)
check(variance([1, 3], xbar=0) == 10)
check(variance([1, 3], xbar=2) == variance([1, 3]))
check(variance([1, 3], xbar=2) != pvariance([1, 3], mu=2))

cases = 0
for size in range(2, 6):
    for raw in product((-1, 0, 2), repeat=size):
        data = list(map(F, raw))
        center = sum(data) / size
        ss = sum((x - center)**2 for x in data)
        check(mean(data) == center)
        check(variance(data) == ss / (size - 1))
        check(variance(iter(data), xbar=center) == variance(data))
        check(pvariance(data) == ss / size)
        for shift in (F(-2), F(1, 2), F(3)):
            supplied = center + shift
            around = sum((x - supplied)**2 for x in data)
            result = variance(data, xbar=supplied)
            check(result == around / (size - 1))
            check(result - variance(data) == F(size, size - 1) * shift**2)
            check(result > variance(data))
            cases += 1
for values in ([], [F(1)]):
    try:
        variance(values)
    except StatisticsError:
        check(True)
    else:
        raise AssertionError('insufficient observations accepted')
check(pvariance([F(7)]) == 0)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'shift_cases': cases, 'sequences': 360, 'status': 'passed'}))
```

## Publisher checks and limits

- Published bytes are compared with the tested draft; committed code is extracted and rerun on both named builds.
- Synthetic in-memory finite data only. No user records, files, network, randomness or process-wide numeric setting changes.
- No NaNs, infinities, mixed numeric types, Decimal contexts, extreme magnitudes, streaming memory bounds or arbitrary-input safety tested. No claim about representativeness, independence or statistical sufficiency.
- Historical issue 40855 is closed/fixed and 36099 closed/duplicate. Their discussions explain a boundary, not pending work or current failures.

## Sources

1. Python 3.13 statistics reference, variance xbar and pvariance: https://docs.python.org/3.13/library/statistics.html
2. Python 3.14 statistics reference, same applicable contracts: https://docs.python.org/3.14/library/statistics.html
3. Historical fixed tracker 40855, supplied centers and unchanged divisor: https://bugs.python.org/issue40855
4. Historical documentation tracker 36099, xbar versus mu terminology: https://bugs.python.org/issue36099
5. Community variance API reference, unchecked xbar: https://pydocs.org/statistics/variance
6. Independent variance guide, precomputed-mean example: https://www.geeksforgeeks.org/python/python-statistics-variance/
