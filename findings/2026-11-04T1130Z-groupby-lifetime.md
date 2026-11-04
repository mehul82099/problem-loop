# itertools.groupby: keeping the outer list does not keep the groups

Date: 2026-11-04. A tested iterator-lifetime and grouping-contract finding, not a new Python defect.

## Research

The [itertools reference](https://docs.python.org/3/library/itertools.html) states two contracts that are easy to overlook: `groupby` forms consecutive runs, not SQL-style aggregation, and each returned group iterator shares the source with the outer iterator. Advancing the outer iterator makes the previous group unavailable. If values are needed later, materialize each group while it is current.

Public examples show both forms of confusion: [converting the outer iterator to a list](https://stackoverflow.com/questions/48475888/list-around-groupby-results-in-empty-groups), [consuming the same group more than once](https://stackoverflow.com/questions/25895395/strange-behavior-of-sorted-itertools-groupby), and [unpacking groups with zip before consuming them](https://stackoverflow.com/questions/66320285/using-zip-on-the-results-of-itertools-groupby-unexpectedly-gives-empty-lists). These are developer questions, not evidence of a new runtime regression.

## Discussion

There are two separate hazards. First, `list(groupby(data))` saves keys and group-iterator objects, not the values in each group. It exhausts the outer iterator before later code reads those groups. Second, even correctly materialized *runs* can repeat keys. Turning `[('a', first_run), ('b', second_run), ('a', third_run)]` into a dictionary overwrites the earlier `a` run. Materializing at the right time fixes the lifetime problem but does not fix the grouping policy.

For input `[('a', 1), ('b', 2), ('a', 3)]`, immediate materialization produces three runs. Converting those runs to a dictionary retains only two of the three input records. That record loss is in the constructed dictionary; it does not mutate the input list.

## Conclusion

Choose the intended contract before changing code:

- For adjacent runs, keep input order and consume or materialize a group before advancing the outer iterator. Do not turn repeated run keys into dictionary keys unless overwriting is intentional.
- For all records grouped by key, sort with the same key function before `groupby`, if reordering is acceptable, or accumulate into list-valued buckets. The [sorting guide](https://docs.python.org/3/howto/sorting.html) explains stable key-based sorting, and the [collections reference](https://docs.python.org/3/library/collections.html) documents `defaultdict(list)` grouping.

Sorting is not a universal fix: it changes run boundaries and key order, requires comparable sort keys, and materializes data. Buckets require hashable keys and retain the collected values. Neither approach should replace streaming run processing without considering memory and order requirements.

## Action: measured regression probe

Ran 12 assertions on each of CPython **3.13.17** and **3.14.9** on Linux x86_64. All passed, for 24 assertion executions across two interpreters. Checks cover repeated run keys, dictionary overwriting, sorted aggregation, source sharing, repeated consumption, late group consumption, and bucket-based aggregation.

Measured examples:

| Construction | Observed result |
|---|---|
| Run keys from the unsorted three-row input | `['a', 'b', 'a']` |
| Number of records left after `dict(runs)` | `2` |
| Number of records after same-key sorting and immediate group materialization | `3` |
| Read first group after advancing outer iterator to second group | `[]` |
| Read second group immediately | `['b', 'b']` |
| Read that second group again | `[]` |
| Read groups only after `list(groupby('aabb'))` | `[('a', []), ('b', [])]` |

Save as `probe.py` and run on supported interpreters. No files, network or external databases are accessed.

```python
import json
import platform
from itertools import groupby
from collections import defaultdict

rows = [('a', 1), ('b', 2), ('a', 3)]
key = lambda row: row[0]
runs = [(k, list(g)) for k, g in groupby(rows, key)]
assert [k for k, _ in runs] == ['a', 'b', 'a']
assert dict(runs) == {'a': [('a', 3)], 'b': [('b', 2)]}
assert sum(len(g) for g in dict(runs).values()) == 2
materialized = [(k, list(g)) for k, g in groupby(sorted(rows, key=key), key)]
assert materialized == [('a', [('a', 1), ('a', 3)]), ('b', [('b', 2)])]
assert sum(len(g) for _, g in materialized) == len(rows)

outer = groupby('aabb')
_, first = next(outer)
_, second = next(outer)
assert list(first) == []
assert list(second) == ['b', 'b']
assert list(second) == []

late = list(groupby('aabb'))
assert [(k, list(g)) for k, g in late] == [('a', []), ('b', [])]

buckets = defaultdict(list)
for row in rows:
    buckets[key(row)].append(row)
assert dict(buckets) == dict(materialized)
assert [k for k, _ in runs] != list(buckets)
assert sum(len(g) for g in buckets.values()) == len(rows)
print(json.dumps({'python': platform.python_version(), 'checks': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe are under this repository's MIT license. Source questions retain their authorship.
- Tests use finite in-memory lists and strings with deterministic keys. No claim about infinite iterables, changing keys, exceptions in key functions, performance, application impact or other grouping libraries.
- The probe checks only two named Python versions. It is a repeatable teaching/regression example, not a newly discovered defect or an exhaustive compatibility guarantee.
