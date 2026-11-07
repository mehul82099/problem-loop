# bisect searches for a key; insort inserts a record

## Research
Public Python questions report surprising positions or TypeError when a complete record is passed to `bisect(..., key=...)`. The historical CPython documentation discussion explains the asymmetry: a lookup often has only a field value, while an insertion necessarily has the complete record. The current Python 3.14 reference is explicit: bisect does not apply key to x; insort applies it during search and inserts the original x.

## Discussion
A key argument does not make these two call shapes interchangeable:

| Operation | Pass as x | What happens |
| --- | --- | --- |
| `bisect_left(rows, 20, key=by_score)` | Comparison key | Finds the first bound for score 20. |
| `insort_left(rows, new_row, key=by_score)` | Complete record | Searches using its score, inserts that record. |
| `bisect_left(rows, new_row, key=by_score)` | Wrong domain for this example | Compares integer keys against a Row and raises TypeError. |

A mismatched domain is not guaranteed to raise: compatible types can yield a plausible but wrong bound, as the public tuple example illustrates. Also, a bound is not proof of membership. It can point at the next greater key or the end. Even a matching score does not establish equality of every field.

This is documented behavior, not a new bug. The list must already be sorted by the same key. Left and right choose opposite sides of an equal-key run; neither decides the application's identity or deduplication policy.

## Conclusion
Give search helpers names that say whether they accept a field value or a record. For an exact score lookup, check both index bounds and the key at that index. If full-record identity matters, inspect the equal-key range with the application's equality rule. Use insort with the record itself and make tie placement explicit. These recommendations assume stable comparable keys and no concurrent mutation; they do not turn bisect into a thread-safe index.

## Action: executable probe
Original code under this repository's MIT license. Run without `-O` so assertions remain enabled. The helper deliberately returns the first matching score, not a full-record match.

```python
from bisect import bisect_left, bisect_right, insort_left, insort_right
from dataclasses import dataclass
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

@dataclass(frozen=True)
class Row:
    score: int
    label: str

rows = [Row(10, 'a'), Row(20, 'b'), Row(20, 'c'), Row(40, 'd')]
seen = []

def by_score(row):
    seen.append(row)
    return row.score

probe = Row(20, 'new')
for search, expected in ((bisect_left, 1), (bisect_right, 3)):
    seen.clear()
    check(search(rows, 20, key=by_score) == expected)
    check(bool(seen) and all(any(r is old for old in rows) for r in seen))
    seen.clear()
    caught = False
    try:
        search(rows, probe, key=by_score)
    except TypeError:
        caught = True
    check(caught)
    check(not any(r is probe for r in seen))

for insert, expected in ((insort_left, 1), (insort_right, 3)):
    copy = rows.copy()
    seen.clear()
    insert(copy, probe, key=by_score)
    check(copy[expected] is probe)
    check(any(r is probe for r in seen))
    check([r.score for r in copy] == [10, 20, 20, 20, 40])
    check([r.label for r in copy if r is not probe] == ['a', 'b', 'c', 'd'])

def first_score(data, target):
    index = bisect_left(data, target, key=lambda r: r.score)
    if index < len(data) and data[index].score == target:
        return data[index]
    return None

check(first_score(rows, 20) is rows[1])
check(first_score(rows, 30) is None)
check(first_score(rows, 99) is None)
check(first_score([], 20) is None)
check(first_score(rows, 0) is None)
check(bisect_left(rows, 30, key=by_score) == 3)
check(rows[3].score == 40)  # A valid bound does not prove a match.
check(probe not in rows)  # Same score is not full-record equality.
check([r.label for r in rows] == ['a', 'b', 'c', 'd'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 25 checks passed on CPython 3.13.17 and 3.14.9, each supervised by a 15-second shell timeout. No external dependencies or network calls in the probe.
- Covers left/right duplicate-key bounds, key calls limited to stored records during search, wrong-domain TypeError with a Row, insertion keying the new record, original-record identity retained after insertion, tie placement, and no mutation of the original list.
- Exact-score checks cover a match, an interior miss, values before/after the data, and empty data. A same-score record with a different label is explicitly not considered full-record equality.
- Does not assert a specific key-call count, benchmark insertion, test custom comparators, NaN, mutable keys, bounded lo/hi searches, concurrent mutation or third-party sorted containers. A search bound is not a validation pass over the whole input.

## Sources
- [Python 3.14 bisect reference](https://docs.python.org/3.14/library/bisect.html): current key-domain, insertion, comparison and concurrency contracts.
- [CPython 3.14 bisect implementation](https://github.com/python/cpython/blob/3.14/Lib/bisect.py): insort passes key(x) for search but inserts x; branch source can change and the module may use its C accelerator at runtime.
- [CPython documentation discussion 91966](https://github.com/python/cpython/issues/91966): historical confusion and explanation, not evidence of a current defect.
- [Public key-domain question](https://stackoverflow.com/questions/75285772/using-bisect-functions-with-a-key): record versus lookup-value asymmetry.
- [Public tuple-position question](https://stackoverflow.com/questions/72101337/how-does-the-key-arg-in-python-bisect-work): wrong-domain input can produce a surprising position instead of an error. That supplied tuple example was not rerun as part of this probe.
- [Independent bisect guide](https://foxipa.com/en/python/learn/bisect/): corroborates key versus record arguments and checking bounds before testing for an exact match.
