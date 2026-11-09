# combinations selects positions, not distinct values

Date: 2026-11-09. Evidence-backed Python finding, not a new itertools defect.

## Research

The Python itertools reference says combinations treats elements as unique by position, not by value. Community questions about duplicate results show why "without replacement" is easy to misread: it means one input position is not selected twice in the same result, not that equal-valued positions disappear. A Python forum explanation and independent tutorial corroborate that distinction.

## Discussion

For `['A', 'A', 'B']`, two-position combinations are `('A', 'A')`, `('A', 'B')`, `('A', 'B')`. There are three positional choices even though only two distinct value tuples appear. The pair of As is valid because it uses two different positions.

Deduplicating before and after the operation answers different questions. Removing duplicate input values first leaves only A and B, so the AA result is impossible. Deduplicating output tuples retains AA once, along with AB once. Neither is a universal correction to the raw combinations result.

The input order controls tuple order. With an unsorted input, AB and BA may be different value tuples even if the application thinks of them as the same unordered multiset. Output deduplication by tuple equality does not supply that further canonicalization policy.

## Conclusion

| Required model | Candidate policy | Boundary |
| --- | --- | --- |
| Choose distinct occurrences or records | Raw `combinations` | Equal values can yield repeated-looking tuples |
| Choose from distinct categories at most once | Deduplicate input, then combine | Discards original multiplicity |
| Keep feasible value tuples once | Deduplicate output under stated equality | Still generates positional results first; tuple order matters |
| Unique unordered multisets | Define a canonical key or dedicated algorithm | Different from merely hashing raw tuples |

Retain IDs or input indexes when individual occurrences matter. Do not use displayed labels as identity by accident. The examples use dictionary keys for stable first-seen deduplication only where all values are hashable. They are a semantic demonstration, not a scalable distinct-combination generator.

## Action: executable policy diagnostic

Original standard-library-only code, covered by the repository MIT license. It also shows that selected objects are shared references and can be unhashable; position selection does not clone values.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from itertools import combinations, product
from math import comb
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

values = ['A', 'A', 'B']
raw = list(combinations(values, 2))
check(raw == [('A', 'A'), ('A', 'B'), ('A', 'B')])
check(len(raw) == comb(3, 2))
# Distinct value tuples while retaining the available multiplicity.
after = list(dict.fromkeys(raw))
check(after == [('A', 'A'), ('A', 'B')])
# Distinct input values: a different problem, no second A remains.
before = list(combinations(dict.fromkeys(values), 2))
check(before == [('A', 'B')])
check(before != after)
check(list(combinations(['B', 'A', 'A'], 2)) ==
      [('B', 'A'), ('B', 'A'), ('A', 'A')])
# Equal unhashable objects are still separate positions and shared references.
a, b = [1], [1]
chosen = list(combinations([a, b], 2))
check(len(chosen) == 1)
check(chosen[0][0] is a and chosen[0][1] is b)
a.append(2)
check(chosen[0] == ([1, 2], [1]))
try:
    list(dict.fromkeys(chosen))
except TypeError:
    checks += 1
else:
    raise AssertionError('unhashable tuple accepted as dict key')
# Position-based count and mapping oracle across every short binary input.
for length in range(5):
    for data in product(('A', 'B'), repeat=length):
        for r in range(length + 2):
            rows = list(combinations(data, r))
            indexes = list(combinations(range(length), r))
            check(len(rows) == comb(length, r))
            check(rows == [tuple(data[i] for i in ix) for ix in indexes])
            check(all(len(set(ix)) == r for ix in indexes))
check(list(combinations([], 0)) == [()])
check(list(combinations([], 1)) == [])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **492 checks passed per build**. These cover duplicate positions, before/after deduplication, input order, unhashable shared references, empty/r=0 cases, and all 31 binary-valued input sequences of lengths zero through four with r from zero through length+1. Counts match math.comb, and results map from increasing index selections.

The index-mapping check uses combinations on distinct indexes, not an independent implementation of its entire algorithm. The finite count checks and explicit examples are bounded evidence, not a proof for all inputs or a performance test. Generating then deduplicating can still incur the full combinatorial output cost. Repository CI is separate.

## Publisher and sources

Published deliverable: this finding and runnable diagnostic. Six public pages were read. No production incidence or new regression is claimed.

1. [Python 3.14 combinations reference](https://docs.python.org/3.14/library/itertools.html#itertools.combinations), primary documentation: positional identity, input-relative ordering and count formula.
2. [Python 3.14 math.comb](https://docs.python.org/3.14/library/math.html#math.comb), primary documentation: number of unordered selections without repetition, zero when r exceeds n.
3. [What combinations guarantees](https://stackoverflow.com/questions/53112861/what-is-the-guarantee-made-by-itertools-combinations), community question: positional uniqueness. Advice to deduplicate inputs is conditional, not interchangeable with preserving multiplicity.
4. [Combinations without repetitions](https://stackoverflow.com/questions/36429507/python-combinations-without-repetitions), community examples: repeated values and output deduplication. Third-party implementations mentioned there are not installed or benchmarked here.
5. [Python forum discussion of combinations/permutations wording](https://discuss.python.org/t/the-confusion-in-docs-of-itertools-combinations-and-itertools-permutations/106244), community explanation, 2026: equal-valued positions remain selectable.
6. [Teclado combinations and permutations tutorial](https://blog.teclado.com/python-itertools-part-2-combinations-permutations/), independent guide, 2019: duplicates and input-position examples. Its broad wording about unique combinations is read with the explicit duplicate examples and current official contract.
