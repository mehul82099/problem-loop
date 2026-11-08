# Near-zero comparisons need an explicit tolerance policy

## Research
A public Python question asks why math.isclose rejects tiny nonzero values compared with zero. The current math reference and PEP 485 explain the relative-versus-absolute distinction. By default, abs_tol is zero, so the allowed difference scales with the magnitudes being compared. Making an ordinary nonzero input tiny does not by itself make it close to zero under that relative policy.

## Discussion
In this probe, 1e-12, -1e-12 and 1e-100 all fail the default zero comparison, yet pass an explicitly chosen illustrative absolute tolerance. That tolerance is test data, not a recommendation for measurements, money or production thresholds. PEP 485 deliberately avoids a nonzero default because no absolute scale suits every use.

Closeness is also not equality. With absolute tolerance 1, zero is close to 0.75 and 0.75 is close to 1.5, but zero is not close to 1.5. Pairwise acceptance therefore cannot be treated as a transitive equivalence relation for deduplication, grouping or dictionary-key identity. A separate clustering or quantization policy is needed if those are the real tasks.

This is documented behavior, not a newly discovered math defect. A public documentation discussion also raises extreme subnormal-rounding corner cases. Accordingly, this finding does not turn the near-zero explanation into a theorem about every representable float and every relative tolerance. The probe uses ordinary magnitudes, exact binary fractions for the nontransitivity example, and no threshold-sensitive decimal boundary claims.

## Conclusion
Specify both the scale and the decision:

| Need | Policy choice | Boundary |
| --- | --- | --- |
| Relative agreement across magnitudes | Explicit rel_tol | Not a substitute for an absolute near-zero allowance. |
| A fixed allowed difference | Set rel_tol=0 and choose abs_tol in the data's units | The application owns that threshold. |
| Combined relative and absolute agreement | Choose both deliberately | math.isclose uses the larger allowance, not their sum. |
| Grouping or canonical identity | Define a separate rule | Pairwise closeness is not transitive. |

Do not describe relative tolerance as a fixed number of decimal places. Also treat NaN and infinity explicitly: this function does not make NaN close to itself, and same-sign infinity is close only to itself. Other libraries may use a different closeness formula or defaults, so do not transfer thresholds without checking their contract.

## Action: deterministic comparison probe
Original code under this repository's MIT license. Scalar floats only, no external dependencies, input files or side effects. Run without `-O` so assertions remain enabled.

```python
import json
import math
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

for value in (1e-12, -1e-12, 1e-100):
    check(not math.isclose(value, 0.0))
    check(math.isclose(value, 0.0, rel_tol=0.0, abs_tol=1e-11))
    check(not math.isclose(value, 0.0, rel_tol=0.0, abs_tol=abs(value) / 2))
check(math.isclose(0.0, 0.0))
check(math.isclose(-0.0, 0.0))
check(math.isclose(1_000_000, 1_000_001, rel_tol=1e-5))
check(not math.isclose(1, 2, rel_tol=1e-5))
# Exactly representable binary fractions avoid threshold-rounding ambiguity.
a, b, c = 0.0, 0.75, 1.5
check(math.isclose(a, b, rel_tol=0, abs_tol=1))
check(math.isclose(b, c, rel_tol=0, abs_tol=1))
check(not math.isclose(a, c, rel_tol=0, abs_tol=1))
check(math.isclose(1.0, 1.5, rel_tol=0, abs_tol=0.5))
check(math.isclose(10, 11, rel_tol=0.1) == math.isclose(11, 10, rel_tol=0.1))
check(not math.isclose(math.nan, math.nan))
check(math.isclose(math.inf, math.inf))
check(not math.isclose(math.inf, -math.inf))
for kwargs in ({'rel_tol': -1}, {'abs_tol': -1}):
    caught = False
    try:
        math.isclose(1, 1, **kwargs)
    except ValueError:
        caught = True
    check(caught)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 23 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Covers default zero comparisons, absolute opt-in and rejection, signed zero, relative scaling, nontransitivity, exact absolute boundary, a symmetry example, NaN/infinity and negative-tolerance rejection.
- Does not select a production tolerance, validate a numeric algorithm, compare NumPy/Decimal behavior, measure precision loss, or exhaustively test subnormals, overflow, all exceptional values or all parameter ranges. No universal equality replacement is supplied.

## Sources
- [Python 3.14 math reference](https://docs.python.org/3.14/library/math.html): isclose formula, defaults and special values.
- [PEP 485](https://peps.python.org/pep-0485/): primary design rationale for relative/absolute tolerance, symmetry and a zero absolute default; historical proposal wording is not substituted for the current API.
- [CPython 3.14 math implementation](https://github.com/python/cpython/blob/3.14/Modules/mathmodule.c): current comparison implementation; mutable branch.
- [Public near-zero question](https://stackoverflow.com/questions/35324893/using-math-isclose-function-with-values-close-to-0): user confusion motivating the probe.
- [Public documentation discussion 131094](https://github.com/python/cpython/issues/131094): wording correction and extreme floating-rounding caveats. Its corner-case examples are not claimed as local tests.
- [Real Python math guide](https://realpython.com/python-math-module/): independent formula and tolerance examples. Its decimal-place phrasing is not adopted as a fixed-place guarantee.
