# bisect searches with a key value; insort inserts a record

Date: 2026-11-08. Evidence-backed Python finding, not a new runtime defect.

## Research

A public Python issue and community questions document confusion about the `key=` argument: `bisect_left` and `bisect_right` apply it to stored records, but not to the search probe. `insort_left` and `insort_right` apply it to the incoming record for searching, then insert that original record. The Python 3.14 documentation states both contracts explicitly.

## Discussion

Suppose jobs are sorted by their integer `due` field. Searching takes the integer cutoff: `bisect_left(jobs, 20, key=by_due)`. Inserting takes a job: `insort_left(jobs, new_job, key=by_due)`. Passing the same argument shape to both APIs is a mistake.

The failure is not always a TypeError. With `[1, 3, 5]` and a key that multiplies by ten, searching for raw `3` returns index 0 because it compares 3 against keys 10, 30, 50. If the intent was to find the position of record 3, the search probe must be 30. A plausible in-range integer result cannot verify that intent. Conversely, applying a key before `insort` can apply the transformation twice or insert the wrong object.

An insertion point is also not an exact-match result. Guard the end boundary and compare the candidate key when exact membership is required. Left and right select opposite sides of equal keys; neither supplies a secondary ordering policy.

## Conclusion

| Task | Input to API | Required caller policy |
| --- | --- | --- |
| Locate cutoff or key range | Key value to `bisect_*` | List sorted under the same key; choose left/right boundary |
| Insert a record | Whole record to `insort_*` | Preserve sortedness; choose tie placement |
| Check exact key membership | Key value, then inspect candidate | Handle index equal to list length and compare key |
| Change a stored ordering field | Explicit remove/reinsert or re-sort | Existing position does not update itself |

Assumptions: single-threaded access, comparable integer keys, no concurrent mutation. This is not a generic validation wrapper. Some domains use the same type for records and keys, so runtime type checks alone cannot infer the intended units. `insort` still has an O(n) list insertion cost despite its O(log n) search.

## Action: executable diagnostic

Standard-library-only probe, no network or external dependencies. Original code is covered by the repository MIT license.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from bisect import bisect_left, bisect_right, insort_left, insort_right
from operator import itemgetter
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def raises_typeerror(action):
    global checks
    try:
        action()
    except TypeError:
        checks += 1
    else:
        raise AssertionError('expected TypeError')

by_due = itemgetter('due')
jobs = [{'id': 'a', 'due': 10}, {'id': 'b', 'due': 30},
        {'id': 'c', 'due': 30}, {'id': 'd', 'due': 50}]
original = list(jobs)
check(bisect_left(jobs, 30, key=by_due) == 1)
check(bisect_right(jobs, 30, key=by_due) == 3)
check(bisect_left(jobs, 20, key=by_due) == 1)
check(bisect_left(jobs, 0, key=by_due) == 0)
check(bisect_right(jobs, 99, key=by_due) == len(jobs))
check(jobs == original)  # Search does not insert.
raises_typeerror(lambda: bisect_left(jobs, {'due': 20}, key=by_due))
new = {'id': 'new', 'due': 30}
left = list(jobs)
right = list(jobs)
insort_left(left, new, key=by_due)
insort_right(right, new, key=by_due)
check([j['id'] for j in left] == ['a', 'new', 'b', 'c', 'd'])
check([j['id'] for j in right] == ['a', 'b', 'c', 'new', 'd'])
check(left[1] is new)
check(right[3] is new)
raises_typeerror(lambda: insort_left(list(jobs), 20, key=by_due))
# Comparable wrong-domain probes can return plausible but unintended slots.
scale = lambda value: value * 10
check(bisect_left([1, 3, 5], 3, key=scale) == 0)
check(bisect_left([1, 3, 5], scale(3), key=scale) == 1)
# An insertion point is not proof of an exact match.
i = bisect_left(jobs, 20, key=by_due)
check(i < len(jobs))
check(by_due(jobs[i]) != 20)
# Mutating an ordering field breaks the caller's sortedness invariant.
mutated = [dict(j) for j in jobs]
mutated[0]['due'] = 100
check([by_due(j) for j in mutated] != sorted(map(by_due, mutated)))
mutated.sort(key=by_due)
check([by_due(j) for j in mutated] == [30, 30, 50, 100])
check(bisect_left(mutated, 100, key=by_due) == 3)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **19 checks passed on each build**. Checks cover key-domain probes, both duplicate boundaries, empty-side boundaries, non-mutating searches, record identity on insertion, wrong-shape errors, comparable wrong-domain values, absent exact matches, and repair after ordering-field mutation. The mutation example verifies the invariant and re-sort, not any guaranteed result from searching unsorted input.

This is a bounded semantic probe, not a benchmark, concurrency test, or production integration test. Repository CI is separate from the local checks.

## Publisher and sources

Published deliverable: this finding and its runnable diagnostic. No automatic repair or library change is proposed. All six source pages were read; longstanding documented behavior is not evidence of a current regression or incident rate.

1. [Python 3.14 bisect documentation](https://docs.python.org/3.14/library/bisect.html), primary reference: key handling, sortedness assumption, boundaries, exact-lookup recipes, and insertion cost.
2. [CPython issue 91966](https://github.com/python/cpython/issues/91966), public maintainer discussion from 2022: the API confusion and documentation clarification.
3. [CPython 3.14 Lib/bisect.py](https://github.com/python/cpython/blob/3.14/Lib/bisect.py), primary source: readable algorithm shows `key(x)` for insort and insertion of original `x`. This file can be replaced at import by the C implementation; local tests exercise the installed public API, not this file in isolation.
4. [Using bisect functions with a key](https://stackoverflow.com/questions/75285772/using-bisect-functions-with-a-key), community question: search/insert asymmetry. Community explanations are corroboration, not the API authority.
5. [Using bisect in a list of tuples](https://stackoverflow.com/questions/20908047/using-bisect-in-a-list-of-tuples), community examples: field-key searching. Older answers predate `key=` and are not used as current guidance.
6. [PyMOTW bisect](https://pymotw.com/3/bisect/index.html), independent tutorial: insertion positions and duplicate-side choice. Its examples do not establish the modern `key=` contract; the current Python reference does.
