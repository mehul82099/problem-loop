# Near-zero isclose comparisons need an application-scale absolute tolerance

Date: 2026-11-05. A tested tolerance-policy distinction, not a new floating-point defect.

## Research

The [math reference](https://docs.python.org/3/library/math.html) defines isclose using the larger of an absolute threshold and a relative threshold. [PEP 485](https://peps.python.org/pep-0485/) explains why its default absolute tolerance is zero: no positive threshold suits every application scale. A [developer question](https://stackoverflow.com/questions/35324893/using-math-isclose-function-with-values-close-to-0) reports surprise when a very small nonzero value is not close to zero under defaults.

## Discussion

For a finite nonzero x compared to zero with abs_tol=0 and rel_tol below one, the test reduces to `abs(x) <= rel_tol * abs(x)`, so it fails. Making x numerically small is not enough. This does not apply to x=0 itself, which compares close to zero.

If an absolute near-zero threshold is intended, choose abs_tol in the same units as the data. The probe uses 1e-9 only as an illustration, not a universal epsilon. Setting rel_tol=0 makes the illustrated check purely absolute. When both tolerances are nonzero, the function uses the larger permitted difference, not a requirement that both tests pass.

## Conclusion

Specify what close means for the application before changing test tolerances. A threshold that hides a real discrepancy is not a numerical fix. Keep NaN and infinity policy separate: the documented isclose rules do not consider NaN close to itself, and infinity is close only to the same infinity.

## Action: reproducible boundary probe

Ran 14 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover zero itself, small positive/negative values under relative defaults, an illustrative absolute threshold including its boundary, symmetric finite comparison, NaN/infinity and a negative-tolerance error. There is no new wrapper or numerical algorithm.

```python
import json
import math
import platform

assert math.isclose(0.0, 0.0)
assert not math.isclose(1e-12, 0.0)
assert not math.isclose(-1e-12, 0.0)
assert not math.isclose(1e-12, 0.0, rel_tol=0.5)
# Illustrative threshold only: choose tolerance from application units.
assert math.isclose(1e-12, 0.0, rel_tol=0.0, abs_tol=1e-9)
assert math.isclose(-1e-12, 0.0, rel_tol=0.0, abs_tol=1e-9)
assert not math.isclose(1e-8, 0.0, rel_tol=0.0, abs_tol=1e-9)
assert math.isclose(1e-9, 0.0, rel_tol=0.0, abs_tol=1e-9)
assert math.isclose(100.0, 100.01, rel_tol=0.001)
assert math.isclose(100.01, 100.0, rel_tol=0.001)
assert not math.isclose(float('nan'), float('nan'), abs_tol=1.0)
assert math.isclose(float('inf'), float('inf'))
assert not math.isclose(float('inf'), 1.0, abs_tol=1.0)
try:
    math.isclose(0.0, 0.0, abs_tol=-1.0)
except ValueError:
    pass
else:
    raise AssertionError('negative tolerance accepted')
print(json.dumps({'python': platform.python_version(), 'cases': 14, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked explanations retain their authorship.
- The example threshold is not a financial, measurement, scientific or test-suite acceptance policy. Callers must choose it using their own units and error budget.
- Only the named built-in float cases and two builds were tested. No Decimal, array library, subnormal-boundary analysis, custom numeric type or performance benchmark was used.
- Approximate closeness is not a replacement for exact equality, hashing or a general ordering relation. This finding does not change any production tolerance.
