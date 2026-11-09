# Counter augmented arithmetic is not a signed update

Date: 2026-11-09. Evidence-backed Python finding, not a new collections defect.

## Research

Python's versioned collections references distinguish signed count storage from multiset operations. Counter can hold zero and negative values, and update/subtract preserve them. Counter-level addition and subtraction instead emit only positive results. The 3.14 implementation shows the augmented operators also remove nonpositive counts after updating: `counter += other` is not the same contract as `counter.update(other)`.

A June 2021 public question reports negative differences disappearing and then a second surprise: assigning the result of subtract gives None because that method mutates its receiver. A March 2010 design discussion explains the deliberate multiset policy. That historical message predates the subsequently added subtract method and is not evidence that signed subtraction is unavailable today.

## Discussion

| Operation on fresh Counter copies | Signed result policy | Mutation/return policy |
| --- | --- | --- |
| left + right or left - right | Retain positive results only | New Counter |
| left += right or left -= right | Retain positive results only | Mutate existing Counter |
| left.update(right) | Preserve signed sums, including zero | Mutate; returns None |
| left.subtract(right) | Preserve signed differences, including zero | Mutate; returns None |
| left[key] += delta | Arithmetic on the selected value | Not the Counter-level multiset operator |

The augmented operators can remove a pre-existing negative entry even when the right operand is empty. In-place does not mean sign-preserving. If another variable aliases the Counter, it sees this mutation too.

Clipping also changes algebra over signed inputs. For one key with counts 1, -2 and 2, `(a + b) + c` produces 2 but `a + (b + c)` produces 1. The intermediate negative was discarded in the first grouping. Accumulating the same signed deltas with update preserves -1 after the first two inputs and ends at 1. Do not regroup signed Counter additions assuming ordinary integer associativity.

## Conclusion

Choose between positive multiset operations and signed accumulation explicitly. For a new signed difference without changing the source, copy it and call subtract on the copy; do not assign that method's None return as the result. Use update for signed accumulation only when its mutation policy is intended. This is an API distinction, not a recommendation for a financial ledger or a claim about a production incident.

The repository's earlier Counter finding covered missing-zero equality, stored keys, truth testing and unary-plus filtering. This increment acknowledges that shared positive-count policy but tests binary/augmented arithmetic versus update/subtract, including mutation identity, empty-RHS clipping and grouping-sensitive signed inputs. It is not a new discovery of unary-plus filtering.

## Action

Original code under this repository's MIT license. Bounded in-memory integer Counters only. Run without Python optimization so assertions remain enabled.

```python
from collections import Counter
import itertools
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

for a, b in itertools.product(range(-5, 6), repeat=2):
    left = Counter(x=a, left=-2, zero=0)
    right = Counter(x=b, right=-3, zero=0)
    keys = set(left) | set(right)
    sums = {k: left[k] + right[k] for k in keys}
    diffs = {k: left[k] - right[k] for k in keys}
    positive_sum = {k: v for k, v in sums.items() if v > 0}
    positive_diff = {k: v for k, v in diffs.items() if v > 0}
    check(dict(left + right) == positive_sum)
    check(dict(left - right) == positive_diff)
    add = left.copy()
    alias = add
    add += right
    check(add is alias)
    check(dict(add) == positive_sum)
    sub = left.copy()
    alias = sub
    sub -= right
    check(sub is alias)
    check(dict(sub) == positive_diff)
    update = left.copy()
    check(update.update(right) is None)
    check(dict(update) == sums)
    subtract = left.copy()
    check(subtract.subtract(right) is None)
    check(dict(subtract) == diffs)
    check(dict(left) == {'x': a, 'left': -2, 'zero': 0})
    check(dict(right) == {'x': b, 'right': -3, 'zero': 0})

# Clipping intermediate negatives means signed addition need not associate.
a, b, c = Counter(x=1), Counter(x=-2), Counter(x=2)
check(dict((a + b) + c) == {'x': 2})
check(dict(a + (b + c)) == {'x': 1})
check((a + b) + c != a + (b + c))
# Signed update preserves the intermediate -1 instead.
signed = a.copy()
signed.update(b)
check(dict(signed) == {'x': -1})
signed.update(c)
check(dict(signed) == {'x': 1})
# Even empty RHS augmented assignment clips pre-existing nonpositive counts.
original = Counter(debt=-2, zero=0, stock=3)
for operation in ('add', 'subtract'):
    local = original.copy()
    if operation == 'add':
        local += Counter()
    else:
        local -= Counter()
    check(dict(local) == {'stock': 3})
    local = original.copy()
    if operation == 'add':
        local.update(Counter())
    else:
        local.subtract(Counter())
    check(dict(local) == dict(original))
# Single-key arithmetic is not the Counter-level augmented operator.
one = Counter(x=-2)
one['x'] += 1
check(dict(one) == {'x': -1})
print(json.dumps({'checks': checks, 'pairs': 121,
                  'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **1,462 checks passed per build**. The 121 operand pairs cover x counts -5..5 plus left-only negative, right-only negative and zero keys. Exact dictionaries are compared so missing keys cannot be confused with stored zero entries. Checks cover binary/augmented results, augmented mutation identity, update/subtract returns and signed values, unchanged operands, one non-associativity fixture, empty RHS and single-key arithmetic.

No Counter subclasses, custom numeric types, floating-point values, threads, performance, aliasing of the left operand with the right operand, arbitrary mappings or external systems were tested. This is not a general ledger, transaction or input-validation implementation.

## Publisher

One bounded increment. Existing overlap is named above rather than presented as a new finding. All source claims are separated from locally executed tests.

## Sources

1. [Python 3.13 collections reference](https://docs.python.org/3.13/library/collections.html), primary documentation: signed update/subtract versus positive multiset arithmetic.
2. [Python 3.14 collections reference](https://docs.python.org/3.14/library/collections.html), primary documentation: same policies and in-place multiset operations.
3. [CPython 3.14 collections implementation](https://github.com/python/cpython/blob/3.14/Lib/collections/__init__.py), primary implementation reference: augmented arithmetic invokes positive-count filtering. The branch is context, not a claim of exact build-source identity.
4. [Subtraction with negative values included](https://stackoverflow.com/questions/67883082/subtraction-of-counter-objects-with-negative-values-included-in-result), June 8, 2021 community question: operator filtering versus mutating subtract's None return.
5. [negative counts in collections.Counter](https://mail.python.org/pipermail/python-list/2010-March/721032.html), March 8, 2010 historical design discussion: deliberate multiset operators; predates current subtract support.
6. [ZetCode collections tutorial](https://zetcode.com/python/collections/), independent tutorial, October 29, 2026, labelled Python 3.15: arithmetic versus signed update/subtract. Its newer-version symmetric-difference example is outside this probe and is not assumed available on the tested builds.
