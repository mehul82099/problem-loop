# A descending stable sort is not a reversed ascending sort

## Research
Python guarantees sort stability: records with equal keys retain their input order. The sorting HOWTO explicitly says reverse=True keeps that guarantee. Reversing an already ascending-sorted list instead reverses the order within every equal-key group too. A public Python tracker report treated unchanged all-equal records as an ignored reverse flag; the response explains why preserving them is intentional.

## Discussion
The probe tags records with distinct labels so equal scores remain observable. A descending sort keeps their original encounter order inside each score group. Reversing the ascending output puts each tie group in the opposite order. Both outputs have descending scores, so checking only score order would miss this difference. With all keys equal, reverse=True leaves encounter order unchanged.

Stability also supports mixed-direction multi-pass sorting. The probe first sorts by ascending age, then by descending score. The second pass preserves the age order within each score group, including original order for complete ties. A numeric tuple-key expression gives the same result for these integer fixtures, but negating keys is not a generic technique for arbitrary sortable objects. The documented double-reversal construction is checked separately.

## Conclusion
Use reverse=True for descending key order while preserving ties. Use a final reversal only when reversing ties is also intended. For multiple criteria, sort least-significant criteria first or define an appropriate composite key. Stability preserves encounter order, not a global deterministic identity: if the input tie order changes, the stable output can change too. This is documented behavior, not a new sorting defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory tagged tuples and fresh lists only. Run without Python optimization so assertions remain enabled.

```python
from operator import itemgetter
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

# (identity label, primary score, secondary age)
rows = [('a', 2, 30), ('b', 1, 20), ('c', 2, 10),
        ('d', 1, 10), ('e', 2, 10)]
original = rows.copy()
score = itemgetter(1)
labels = lambda items: [r[0] for r in items]
ascending = sorted(rows, key=score)
descending = sorted(rows, key=score, reverse=True)
flipped = list(reversed(ascending))
check(labels(ascending) == ['b', 'd', 'a', 'c', 'e'])
check(labels(descending) == ['a', 'c', 'e', 'b', 'd'])
check(labels(flipped) == ['e', 'c', 'a', 'd', 'b'])
check(descending != flipped)
check([r[1] for r in descending] == [2, 2, 2, 1, 1])
check([r[0] for r in descending if r[1] == 2] == ['a', 'c', 'e'])
check(list(reversed(sorted(reversed(rows), key=score))) == descending)
check(rows == original)
check(descending is not rows)
check(descending[0] is rows[0])

all_ties = [('first', 1), ('second', 1), ('third', 1)]
check(sorted(all_ties, key=score, reverse=True) == all_ties)
check(list(reversed(sorted(all_ties, key=score))) != all_ties)
check(sorted([], key=score, reverse=True) == [])
check(sorted([('only', 1)], key=score, reverse=True) == [('only', 1)])

# Least significant criterion first; stable primary pass preserves it.
by_age = sorted(rows, key=itemgetter(2))
multi = sorted(by_age, key=score, reverse=True)
check(labels(multi) == ['c', 'e', 'a', 'd', 'b'])
check(multi == sorted(rows, key=lambda r: (-r[1], r[2])))
check([r[0] for r in multi if (r[1], r[2]) == (2, 10)] == ['c', 'e'])

calls = []
def observed_key(row):
    calls.append(row[0])
    return row[1]

check(sorted(rows, key=observed_key, reverse=True) == descending)
check(len(calls) == len(rows) and set(calls) == set(labels(rows)))
copy = rows.copy()
result = copy.sort(key=score, reverse=True)
check(result is None)
check(copy == descending)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 21 checks passed on CPython 3.13.17 and 3.14.9.
- Covers ascending/descending tie order, final reversal difference, all-equal keys, empty/singleton inputs, double reversal, mixed-direction multi-pass/composite equivalence, original complete ties, one key evaluation per item, unchanged source, shallow element identity and in-place sort's None return.
- No NaNs, inconsistent/custom comparisons, key exceptions, concurrent mutation, external sorting, database ordering, cross-process deterministic ordering or timing benchmark was tested. The tuple-key negation comparison is restricted to the small integer scores shown.

## Sources
- [Python 3.14 sorting HOWTO](https://docs.python.org/3.14/howto/sorting.html): stable reverse sorting, key evaluation, multi-pass sorts and double reversal.
- [Python 3.14 built-in functions](https://docs.python.org/3.14/library/functions.html): sorted contract and return representation.
- [Python tracker issue 29754](https://bugs.python.org/issue29754): March 8, 2017 report about all-equal keys and clarification that reverse sorting preserves ties.
- [Reversed output versus reverse sorting](https://stackoverflow.com/questions/9969698/python-difference-between-reversedlist-and-list-sortreverse-true): community examples of different equal-key ordering.
- [Real Python sorting guide](https://realpython.com/python-sort/): independent sorting/stability explanation. Its informal 'reverse the order' wording is interpreted here as descending key order, not reversal of ties.
- [Python-ideas multiple-level sorting discussion](https://mail.python.org/pipermail/python-ideas/2016-October/043126.html): October 2016 discussion distinguishing reversed comparisons from reversing a list. No external sorter implementation was executed.
