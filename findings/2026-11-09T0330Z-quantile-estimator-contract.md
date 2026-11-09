# Quantile cut points need an estimator label, not just a percentile name

Date: 2026-11-09. Evidence-backed Python finding, not a new statistics defect.

## Research

Public questions report different quartiles from statistics.quantiles and other tools. The Python reference makes the estimator an explicit method parameter: exclusive is the default, inclusive is another supported choice. The result has n-1 cut points, where n is the number of intervals, not the number of input observations or desired returned values.

## Discussion

For the same literal observations [10, 20, 30, 40, 50], the tested default/exclusive quartiles are [15, 30, 45], while inclusive gives [20, 30, 40]. Neither difference proves arithmetic corruption. The methods assign different probability positions to observations. Python documents exclusive in terms of samples that can omit population extremes, and inclusive for population data or samples known to include those extremes. That description is not a universal rule that one estimator is statistically best for every report.

| Explicit call | Tested cut points | Boundary |
| --- | --- | --- |
| quantiles([10,20,30,40,50], method='exclusive') | [15,30,45] | Default estimator, not the same quartiles as inclusive |
| quantiles([10,20,30,40,50], method='inclusive') | [20,30,40] | Different stated estimator, not a bug fix |
| quantiles([0,100], method='exclusive') | [-25,50,125] | Tiny-sample cut points can extend beyond observations |
| quantiles([0,100], method='inclusive') | [25,50,75] | Staying within endpoints does not prove a reliable estimate |
| quantiles([7]) | [7,7,7] | Accepted on the tested 3.13/3.14 builds, not evidence of adequate sampling |

The version boundary matters: Python documents singleton acceptance as a 3.13 change. An independent tutorial still illustrates a Python 3.10 singleton rejection. That older traceback is not the current input-size contract. Empty input still fails in this probe. Acceptance of a singleton is separate from the reference's advice that meaningful results should use more observations than n.

NumPy currently documents its own default as method='linear' and offers multiple estimators. Match probability levels, estimator definitions, input treatment and library version before comparing tools. This probe does not execute NumPy or certify cross-library equivalence; a shared percentile name alone is insufficient.

## Conclusion

A reproducible report should retain the estimator and sample size with the cut points. Choose the estimator from the reporting requirement before looking at which output seems preferable. State missing-value and small-sample policy instead of silently removing measurements or relying on a version-dependent exception. Percentiles with n=100 produce 99 cuts; the 90th cut is at zero-based index 89, not index 90.

The toy helper below requires an explicit method, at least five observations for quartiles, built-in int/float inputs, finite numeric checks and finite outputs. Five is this demonstration's policy, not a statistical sufficiency threshold. It rejects booleans, unsupported types and extreme values outside its numeric checks rather than promising general arbitrary-precision statistics. It does not choose an estimator, infer representativeness or provide confidence intervals. The earlier NaN ordering finding addresses missing-value ordering; this increment addresses quantile estimator identity and sample-size acceptance.

## Action: bounded diagnostic and labeled report helper

Original standard-library-only code under the repository MIT license. Literal in-memory samples, no files or external services. Run without -O so assertions remain enabled. This is not a streaming or weighted quantile estimator.

```python
# Original diagnostic, MIT license (repository LICENSE).
import json
import math
import platform
from statistics import quantiles, StatisticsError

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def raises(kind, fn):
    try:
        fn()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

def quartile_report(values, *, method):
    # Toy reporting contract, not a statistical adequacy test.
    if method not in ('inclusive', 'exclusive'):
        raise ValueError('choose inclusive or exclusive')
    data = tuple(values)
    if len(data) < 5:
        raise ValueError('this report requires at least five observations')
    if any(type(x) not in (int, float) for x in data):
        raise TypeError('this report accepts only built-in ints and floats')
    try:
        finite = all(math.isfinite(x) for x in data)
    except OverflowError as exc:
        raise ValueError('observation outside this report numeric range') from exc
    if not finite:
        raise ValueError('finite observations required')
    cuts = quantiles(data, n=4, method=method)
    if not all(math.isfinite(x) for x in cuts):
        raise ValueError('cut point outside this report numeric range')
    return {'sample_size': len(data), 'method': method, 'cuts': cuts}

sample = [10, 20, 30, 40, 50]
original = sample.copy()
check(quantiles(sample) == [15.0, 30.0, 45.0])
check(quantiles(sample, method='inclusive') == [20.0, 30.0, 40.0])
check(sample == original)
for method, expected in [('exclusive', [15., 30., 45.]),
                         ('inclusive', [20., 30., 40.])]:
    report = quartile_report(iter(sample), method=method)
    check(report == {'sample_size': 5, 'method': method, 'cuts': expected})
    check(quantiles(reversed(sample), method=method) == expected)
    for n in (1, 2, 4, 10, 100):
        cuts = quantiles(sample, n=n, method=method)
        check(len(cuts) == n-1)
        check(cuts == sorted(cuts))
    check(quantiles([7], method=method) == [7, 7, 7])
    check(quantiles([7, 7, 7, 7, 7], method=method) == [7, 7, 7])
    raises(StatisticsError, lambda: quantiles([], method=method))
    raises(StatisticsError, lambda: quantiles(sample, n=0, method=method))
    for short in ([], [7], [1, 2], [1, 2, 3, 4]):
        raises(ValueError, lambda: quartile_report(short, method=method))
    for bad in (float('nan'), float('inf'), -float('inf')):
        raises(ValueError, lambda: quartile_report([1, 2, 3, 4, bad], method=method))
    for bad in (True, '5', None):
        raises(TypeError, lambda: quartile_report([1, 2, 3, 4, bad], method=method))
raises(ValueError, lambda: quartile_report([1, 2, 3, 4, 10**1000], method='inclusive'))
raises(ValueError, lambda: quartile_report([1e308]*5, method='inclusive'))
raises(TypeError, lambda: quartile_report(sample))  # No hidden estimator default.
raises(ValueError, lambda: quartile_report(sample, method='other'))
# At extreme cut points, exclusive can extrapolate outside a tiny sample.
check(quantiles([0, 100], n=4, method='exclusive') == [-25., 50., 125.])
check(quantiles([0, 100], n=4, method='inclusive') == [25., 50., 75.])
check(len(quantiles(sample, n=100)) == 99)
check(quantiles(sample, n=100, method='inclusive')[89] == 46.)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

63 checks passed separately on CPython 3.13.17 and 3.14.9. Cases cover both estimators, unsorted/reversed input, unchanged source values, output cardinality for n=1/2/4/10/100, singleton and empty inputs, a two-point extrapolation example, invalid n, explicitly required method, toy minimum size, rejected types, nonfinite values, oversized integers and nonfinite cut-point arithmetic. Checks use exactly representable expected values in these cases; they are not a general numeric-accuracy benchmark.

## Sources

1. [Python 3.13 statistics reference](https://docs.python.org/3.13/library/statistics.html): quantiles definitions, n-1 output, size advice and singleton version change.
2. [Python 3.14 statistics reference](https://docs.python.org/3.14/library/statistics.html): corroborating current versioned contract.
3. [NumPy quantile reference](https://numpy.org/doc/stable/reference/generated/numpy.quantile.html): documented linear default and alternative estimators; not a local NumPy execution result.
4. [Rick Wicklin, comparison of quantile definitions](https://blogs.sas.com/content/iml/2021/07/26/compare-quantiles-sas-r-python.html), SAS technical blog, 2021-07-26: explanation of estimator-driven differences across statistical software.
5. [Public comparison question](https://stackoverflow.com/questions/61135376/numpy-quantile-and-statistics-quantiles-are-calculating-different-which-one-is), 2020-04-10: user evidence for mismatched-tool confusion, not authority for current API semantics.
6. [TutorialsPoint quantiles tutorial](https://www.tutorialspoint.com/python/python_statistics_quantiles_function.htm): older singleton rejection example explicitly runs Python 3.10; its general two-observation statement is not used as the 3.13/3.14 contract.

The contribution is the original boundary probe and explicit reporting contract. These are documented estimator choices, not a newly discovered algorithm or a claim that other tools are wrong.
