# bisect searches key values; insort inserts whole records

Date: 2026-11-05. A tested search-boundary distinction for documented behavior, not a new bisect defect.

## Research

The [bisect reference](https://docs.python.org/3/library/bisect.html) says its key function is applied to sequence elements, not to the search value x. By contrast, insort applies key to the incoming record for its search, then inserts the original record. [CPython issue 91966](https://github.com/python/cpython/issues/91966) discusses clarifying this distinction, and a [developer question](https://stackoverflow.com/questions/75285772/using-bisect-functions-with-a-key) reports the apparent inconsistency.

## Discussion

When a list contains records sorted by score, `bisect_left(records, 20, key=by_score)` searches for score 20. Supplying a dictionary instead makes the search compare extracted integer scores with that dictionary. A key argument does not automatically transform both sides as it might in a sorting mental model.

The left and right boundaries also differ: they bracket a run of equal integer scores. Returning the slice between them retrieves all records in that run, including duplicates. This is not a generic equality search for arbitrary objects: it relies on keys with consistent ordering and equality, and on a list already sorted with the same key function.

## Conclusion

Pass a comparison key to bisect and a complete record to insort. Keep those two input contracts visible in the call site. The helper here is deliberately a small score-range query, not an automatically maintained index. Mutating a stored score can invalidate its sorted-input assumption.

## Action: tested score-range helper

Ran 12 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe checks left/right duplicate boundaries, missing score, empty input, endpoints, raw-record search failure, full-record insertion after ties, preserved score order, and shallow result ownership. Only integer score keys and serial calls are tested.

```python
import json
import platform
from bisect import bisect_left, bisect_right, insort_right
from operator import itemgetter

by_score = itemgetter('score')

def matching_score(records, score):
    # Caller must keep records sorted by score; this returns a shallow slice.
    left = bisect_left(records, score, key=by_score)
    right = bisect_right(records, score, key=by_score)
    return records[left:right]

rows = [{'score': 10, 'id': 'a'}, {'score': 20, 'id': 'b'},
        {'score': 20, 'id': 'c'}, {'score': 30, 'id': 'd'}]
assert bisect_left(rows, 20, key=by_score) == 1
assert bisect_right(rows, 20, key=by_score) == 3
assert [r['id'] for r in matching_score(rows, 20)] == ['b', 'c']
assert matching_score(rows, 15) == []
assert matching_score([], 20) == []
assert bisect_left(rows, 0, key=by_score) == 0
assert bisect_right(rows, 99, key=by_score) == 4
try:
    bisect_left(rows, {'score': 20}, key=by_score)
except TypeError:
    pass
else:
    raise AssertionError('raw record search unexpectedly accepted')
new = {'score': 20, 'id': 'e'}
insort_right(rows, new, key=by_score)
assert rows[3] is new
assert [r['id'] for r in matching_score(rows, 20)] == ['b', 'c', 'e']
assert [r['score'] for r in rows] == [10, 20, 20, 20, 30]
subset = matching_score(rows, 20)
assert subset is not rows and subset[0] is rows[1]
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original helper and finding use the repository's MIT license. Linked reports retain their authorship.
- The helper does not validate sortedness, key types, missing fields, or custom ordering. It does not normalize NaN or repair mutations. Callers own those preconditions.
- The returned list is new, but its records are shared references. Changing those dictionaries still changes records in the source list.
- No concurrency, timing benchmark or large-input memory behavior was tested. The documentation describes insort as O(n), despite its logarithmic search step; no constant-time insertion claim is made.
