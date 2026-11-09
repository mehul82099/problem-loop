# Sampling without replacement does not make equal values unique

Date: 2026-11-10. Tested Python sampling-contract finding, not a new random defect.

## Research

Python's versioned random references explicitly permit repeated and unhashable population members: each occurrence is eligible. The counts parameter expresses repeated occurrences compactly. A developer question reports both sample and choices returning repeated labels; another question about unique numbers includes a warning about input duplicates. Independent tutorials show sample/counts examples, but their shorthand about "unique items" must be read alongside the official occurrence-level rule.

Older community code that passes a set directly to sample is not a current recipe: automatic set conversion was removed in Python 3.11. This diagnostic uses explicit sequences on the named builds.

## Discussion

Sampling all three occurrences of `['a', 'a', 'b']` necessarily returns two equal labels, regardless of seed or draw order. Without replacement means a selected occurrence is not eligible again. It does not discard other occurrences that compare equal. For unhashable values, two different lists containing 1 can both be selected; the sample contains references to the supplied objects, not deduplicated or cloned values.

`sample(['red', 'blue'], counts=[4, 2], k=5)` models six occurrences, not two unique categories. Counts are multiplicities, not the same contract as reusable relative weights in choices. A zero count makes that category unavailable in this tested nonempty model. The maximum feasible sample size is the total multiplicity. Do not validate k against only the number of displayed labels.

| Required model | Choice | What changes |
| --- | --- | --- |
| Draw occurrences without replacement | sample on occurrence sequence | Equal labels may repeat |
| Compact bounded inventory | sample with counts | Counts are consumable multiplicities |
| Choose distinct categories | Define category identity, deduplicate, then sample a sequence | Removes frequency/inventory information and changes the model |
| Draw with replacement | choices with explicit weights if needed | Does not enforce an inventory cap |

Do not sample occurrences and then discard duplicate labels as a substitute for choosing k categories: the resulting size can shrink, and this is a different sampling process. IDs or input indexes make the selected units explicit. If values are unhashable or domain identity is not ordinary equality, set-based deduplication is not a complete policy.

## Conclusion

State what a sampling unit is before choosing an API. A label can identify a category, a ticket, a stock unit or several different records. Counts preserve multiplicity; deduplication deliberately removes it. Neither is a universal correction.

The earlier combinations-position finding already covers equal values at different positions and shared object references. That overlap is acknowledged. This increment adds random.sample's counts/inventory contract, bounded draw invariants and current sequence-only input checks, not a new claim about positional identity.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Each actual CPython 3.13.17 and 3.14.9 run passed 19,663 checks across 63 nonempty count vectors and 2,808 draw cases, plus selected reference/input cases. Count vectors contain three entries in 0..3; every feasible k and eight local seeds are checked. Each result respects multiplicity and length; full draws recover the entire multiset. Tagged explicit occurrences demonstrate index uniqueness.

The expanded-population path is checked against the same inventory invariants, not equality of same-seed draw order. This is bounded behavioral testing, not a statistical proof, test of uniformity, benchmark or promise of identical samples across Python versions. Local Random objects avoid changing global generator state. Run without optimization so assertions remain active.

```python
from collections import Counter
from itertools import product
from random import Random
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

# Guaranteed duplicate values at full sample, irrespective of order/seed.
population = ['a', 'a', 'b']
check(Counter(Random(7).sample(population, 3)) == Counter(population))
check(population == ['a', 'a', 'b'])
# Equal unhashable objects are permitted; no equality-based deduplication.
objects = [[1], [1]]
sample = Random(7).sample(objects, 2)
check(len(sample) == 2)
check({id(x) for x in sample} == {id(x) for x in objects})

cases = 0
for counts in product(range(4), repeat=3):
    total = sum(counts)
    if total == 0:
        continue
    expanded = [label for label, count in zip('abc', counts) for _ in range(count)]
    before = expanded.copy()
    for k in range(total + 1):
        for seed in range(8):
            result = Random(seed).sample(list('abc'), k, counts=counts)
            observed = Counter(result)
            check(len(result) == k)
            check(all(observed[label] <= count for label, count in zip('abc', counts)))
            check(set(result) <= set(expanded))
            check(k != total or observed == Counter(expanded))
            # Compare invariants, not exact draw order or same-seed identity.
            direct = Random(seed).sample(expanded, k)
            check(len(direct) == k and Counter(direct) <= Counter(expanded))
            tagged = Random(seed).sample(list(enumerate(expanded)), k)
            check(len({i for i, _ in tagged}) == k)
            check(expanded == before)
            cases += 1
for k in (-1, 4):
    try:
        Random(7).sample(population, k)
    except ValueError:
        check(True)
    else:
        raise AssertionError('bad sample size accepted')
try:
    Random(7).sample({'a', 'b'}, 1)
except TypeError:
    check(True)
else:
    raise AssertionError('set population accepted')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'count_vectors': 63, 'draw_cases': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Exact published draft bytes are compared; committed code is extracted and rerun on both named builds.
- Only nonnegative tiny integer counts with a positive total are used. This is not validation for arbitrary counts, exotic equality, concurrent mutation or large inputs.
- No external randomness, user data, files or network. Seeds are test fixtures, not secret values. Python's random module is not for security tokens or other cryptographic use.
- No application fairness, lottery compliance, privacy, or production sampling-frame guarantee is supplied. Deduplication requires a grounded domain identity policy.

## Sources

1. Python 3.13 random reference, occurrences, counts, sequence requirement and reproducibility limits: https://docs.python.org/3.13/library/random.html
2. Python 3.14 random reference, same applicable contracts: https://docs.python.org/3.14/library/random.html
3. Developer question, repeated labels in both sample and choices: https://stackoverflow.com/questions/59763933/what-is-the-difference-between-the-random-choices-and-random-sample-function
4. Community discussion of unique numbers and input duplicates; old direct-set example is not used: https://stackoverflow.com/questions/6494508/how-do-you-pick-x-number-of-unique-numbers-from-a-list-in-python
5. Learn By Example guide, explicit repeats and counts examples: https://www.learnbyexample.org/how-to-select-random-items-from-a-list-in-python/
6. Python Pool independent selection guide; "unique items" shorthand is qualified by the official occurrence rule: https://www.pythonpool.com/randomly-select-from-list-python/
