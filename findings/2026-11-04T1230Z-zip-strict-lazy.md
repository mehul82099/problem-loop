# zip(strict=True) detects unequal lengths, but only when iteration reaches the mismatch

Date: 2026-11-04. A tested validation-boundary finding, not a new Python defect.

## Research

[PEP 618](https://peps.python.org/pep-0618/) introduced optional equal-length checking because ordinary `zip` silently stops at the shortest iterable. It specifies that strict mode raises at the point where iteration would otherwise stop. The [built-in functions reference](https://docs.python.org/3/builtins/functions.html) also states that zip is lazy and illustrates valid pairs being yielded before an unequal-length error.

The [implementation tracker](https://bugs.python.org/issue40636) and [implementation commit](https://github.com/python/cpython/commit/310f6aa7db8dd48952ed718111ce0f016b1c8ef9) record the Python 3.10 addition. [Real Python's parallel-iteration guide](https://realpython.com/python-zip-function/) explains default truncation and strict checking. These establish documented behavior and a real data-alignment concern, not an unresolved regression.

## Discussion

`zip(..., strict=True)` is not an eager preflight. Constructing it does not validate total lengths. Reading a valid prefix and stopping early does not establish that the remaining inputs match. If the loop body changes state, those earlier changes can already have happened when the mismatch is eventually raised.

Our probe records a valid pair in an in-memory list before catching the mismatch. It does not perform any external write. That demonstrates the control-flow boundary without claiming that any particular application loses data or has incomplete transactions.

Strict mode validates length, not semantic alignment: two equally long lists may still pair the wrong records. It also does not roll back changes or rewind the source iterators after an error.

## Conclusion

When equal lengths are an invariant, use strict mode and fully consume the iterator before claiming that invariant was checked. For finite, suitably small, effect-free input sources, materializing `list(zip(..., strict=True))` before downstream changes creates a useful boundary: if collection raises, the assignment does not complete. That does not undo side effects in the input iterators themselves, and buffering may be inappropriate for large or unbounded inputs.

For streaming work, define what happens to already-processed pairs on failure instead of treating strict mode as transaction control. If unequal lengths are expected and padding is the intended policy, [itertools.zip_longest](https://docs.python.org/3/library/itertools.html) is a different contract. Choose a sentinel distinct from valid data rather than assuming None means missing.

## Action: measured regression probe

Executed 12 checks on each of CPython **3.13.17** and **3.14.9**, Linux x86_64. Both passed, for 24 check executions. Checks include default truncation, equal-length strict results, either input being longer, delayed detection after a valid prefix, prefix processing before the error, failed materialization assignment, padding with a distinct sentinel, and empty inputs.

Measured with `[1, 2]` and `['a']`:

| Operation | Observed result |
|---|---|
| ordinary zip collected to a list | `[(1, 'a')]` |
| first next on strict zip | `(1, 'a')` |
| consume the remaining strict iterator | `ValueError` |
| append each yielded pair before the error | one pair already appended |
| assign full strict materialization to a variable initially None | exception; variable remains None |
| zip_longest with a unique sentinel | second pair contains `2` and that sentinel |

Save as `probe.py`. All mutations are confined to fresh local Python objects; there are no network, file or database operations.

```python
import json
import platform
from itertools import zip_longest

def requires_mismatch(iterator):
    try:
        list(iterator)
    except ValueError:
        return
    raise AssertionError('expected a length mismatch')

assert list(zip([1, 2], ['a'])) == [(1, 'a')]
assert list(zip([1, 2], ['a', 'b'], strict=True)) == [(1, 'a'), (2, 'b')]
requires_mismatch(zip([1, 2], ['a'], strict=True))
requires_mismatch(zip([1], ['a', 'b'], strict=True))

pending = zip([1, 2], ['a'], strict=True)
assert next(pending) == (1, 'a')
# No mismatch has been checked yet; the next advance detects it.
requires_mismatch(pending)

processed = []
try:
    for pair in zip([1, 2], ['a'], strict=True):
        processed.append(pair)
except ValueError:
    pass
else:
    raise AssertionError('expected mismatch after prefix')
assert processed == [(1, 'a')]

prepared = None
try:
    prepared = list(zip([1, 2], ['a'], strict=True))
except ValueError:
    pass
assert prepared is None

sentinel = object()
padded = list(zip_longest([1, 2], ['a'], fillvalue=sentinel))
assert padded[0] == (1, 'a')
assert padded[1][0] == 2 and padded[1][1] is sentinel
assert list(zip([], [], strict=True)) == []
assert list(zip(strict=True)) == []
print(json.dumps({'python': platform.python_version(), 'checks': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe are under this repository's MIT license. Upstream work retains its authorship.
- Only the named interpreter builds and finite in-memory examples were tested. No benchmark, external side effect, application migration, or transaction rollback was tested.
- Catching ValueError in the probe is deliberate observation, not advice to suppress an input error in production. Exact exception wording is not asserted.
- This is an explanation of an existing API contract, with a repeatable regression probe, not a new vulnerability or a claim that strict mode guarantees correct pair identities.
