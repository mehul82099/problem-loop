# A mode result does not prove a unique winner

Date: 2026-11-09. Evidence-backed Python tie-policy finding, not a new statistics defect.

## Research

Python's versioned statistics references say mode returns the first encountered value among those tied for the highest frequency. It does not reject a frequency tie. That behavior changed in Python 3.8; older versions raised StatisticsError for multiple modes. Empty input still raises that error.

The companion multimode returns every most-frequent value in first-encounter order, or an empty list for empty input. A June 2018 public question and its newer answer span the old and new contracts. Issue 35892 and an April 2019 design discussion record why the API moved from rejecting ties to selecting one value. Historical draft options and performance comments in those discussions are not the current function signature or a benchmark here.

## Discussion

For blue, red, red, blue, both labels occur twice and mode returns blue. Reorder those same counts as red, blue, blue, red and it returns red. Neither result establishes that one label was more frequent. First encountered means first encountered among the tied winners, not necessarily the first element of an arbitrary dataset.

| Requirement | Contract to choose |
| --- | --- |
| Any most-frequent value, with encounter-order ties | mode |
| All tied winners, retaining encounter order | multimode |
| Reject empty input and frequency ties | Inspect multimode length and require exactly one |
| Smallest/largest tied value | Explicit min/max of nonempty multimode output, for orderable values |

Returning one value is an API shape, not a uniqueness certificate. A stable first-encounter rule is deterministic for a fixed sequence, but changing input order can change the chosen tie winner. Sorting only to force a winner silently selects another policy and may require comparisons the original categorical inputs do not support.

## Conclusion

If uniqueness matters, check it explicitly rather than relying on a successful mode call or catching the pre-3.8 tie exception. The toy helper below rejects both empty and tied data with ValueError. That is a chosen demonstration policy, not a new standard-library behavior.

A unique mode is not necessarily a strict majority: in aabbca, a occurs three times out of six and is uniquely most frequent without exceeding half. This probe is about discrete frequency, not statistical significance, confidence, continuous-density estimation or a voting rule.

## Action

Original code under this repository's MIT license. Bounded in-memory strings/integers only. Run without Python optimization so assertions remain enabled.

```python
import itertools
import json
import platform
from statistics import mode, multimode, StatisticsError

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def unique_mode(data):
    """Toy policy: reject empty data or any frequency tie."""
    winners = multimode(data)
    if len(winners) != 1:
        raise ValueError('expected exactly one mode')
    return winners[0]

sequences = 0
for size in range(7):
    for seq in itertools.product('abc', repeat=size):
        sequences += 1
        # Small independent oracle: count by equality, preserving encounter order.
        distinct = []
        for value in seq:
            if value not in distinct:
                distinct.append(value)
        peak = max((seq.count(v) for v in distinct), default=0)
        expected = [v for v in distinct if seq.count(v) == peak]
        check(multimode(seq) == expected)
        check(multimode(iter(seq)) == expected)
        if expected:
            check(mode(seq) == expected[0])
            check(mode(iter(seq)) == expected[0])
        else:
            try:
                mode(seq)
            except StatisticsError:
                check(True)
            else:
                raise AssertionError('empty mode accepted')
        if len(expected) == 1:
            check(unique_mode(seq) == expected[0])
        else:
            try:
                unique_mode(seq)
            except ValueError:
                check(True)
            else:
                raise AssertionError('nonunique mode accepted')

check(mode(['blue', 'red', 'red', 'blue']) == 'blue')
check(mode(['red', 'blue', 'blue', 'red']) == 'red')
check(multimode([3, 1, 3, 1]) == [3, 1])
check(mode([3, 1, 3, 1]) != min(multimode([3, 1, 3, 1])))
check(unique_mode([3, 1, 3]) == 3)
# Equal frequency is not a strict-majority test.
check(unique_mode('aabbcaa') == 'a')
check(unique_mode('aabbca') == 'a')  # 3 of 6, not more than half.
print(json.dumps({'checks': checks, 'sequences': sequences,
                  'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **5,471 checks passed per build**. The finite grid covers all 1,093 sequences of lengths 0..6 over a, b and c. An equality/count oracle independently computes expected winners in encounter order. Tuple and iterator inputs, empty mode errors, helper rejection of nonunique results, changed tie encounter order, numeric tie ordering and the mode-versus-majority distinction are checked.

No pre-3.8 interpreter was run. That historical behavior is documentation evidence only. No NaNs, mixed numeric equality classes, unhashable values, custom hashing, infinite iterables, third-party statistics packages, timing or production datasets were tested. Iterator inputs are consumed; callers needing several analyses of one-shot data must plan that ownership separately.

## Publisher

One bounded finding and standalone probe. Full targeted repository search found no prior mode/multimode finding. Existing quantile-estimator and NaN-ordering findings concern different contracts. This contribution tests and explains documented behavior; it does not claim a newly discovered algorithm.

## Sources

1. [Python 3.13 statistics reference](https://docs.python.org/3.13/library/statistics.html), primary documentation: first-encounter tie rule, empty behavior and Python 3.8 change.
2. [Python 3.14 statistics reference](https://docs.python.org/3.14/library/statistics.html), primary documentation: mode versus multimode and explicit min/max tie alternatives.
3. [Issue 35892](https://bugs.python.org/issue35892), historical design record opened February 3, 2019: evolution toward first-encounter mode and separate multimode. Draft proposals are not adopted as the current API.
4. [No unique mode; found 2 equally common values](https://stackoverflow.com/questions/50959614/no-unique-mode-found-2-equally-common-values), June 21, 2018 public question with an April 2020 answer explaining Python 3.8 behavior. Historical private-helper recipes are not used.
5. [PyDocs mode reference](https://pydocs.org/statistics/mode), independent community reference: first-encounter ties and empty-input error. No publication date shown.
6. [Lessons learned from an API design mistake](https://mail.python.org/archives/list/python-ideas@python.org/message/WBHXFGHWGXDBRSSC7HXW2TJNTKDUONPM/), April 2, 2019 Python-ideas discussion: rationale for changing the original tie-error policy. Historical commentary, not a statistical preference imposed on applications.
