# Counter equality does not mean identical stored keys or identical truth values

Date: 2026-11-04. A tested count-versus-container distinction, not a new Python defect.

## Research

The [collections reference](https://docs.python.org/3/library/collections.html) documents that setting a Counter count to zero does not remove the key. It also documents a Python 3.10 change: Counter equality treats missing counts as zero. Consequently `Counter()` and `Counter(a=0)` compare equal even though one stores a key and the other does not.

[Issue 40755](https://bugs.python.org/issue40755) records the rich-comparison design and its zero-default equality rule. The earlier [issue 22533](https://bugs.python.org/issue22533) discusses the older behavior, so its historical conclusions must not be read as the current equality contract. The [community equality question](https://stackoverflow.com/questions/70993401/compare-two-counter-object-in-python-with) shows why answers written for different Python versions can conflict.

A separate [historical Python-ideas discussion](https://mail.python.org/pipermail/python-ideas/2011-April/009736.html) explains that a Counter storing a zero-count key is still a non-empty container. The [truth-value reference](https://docs.python.org/3/builtins/stdtypes.html) distinguishes empty containers from numeric zero. That is not a promise that a count-based equality test and a container-emptiness test answer the same question.

## Discussion

Three questions need three policies:

- Do the counters represent the same counts, treating absent keys as zero? Use Counter equality under the current documented contract.
- Do they have exactly the same stored key/value pairs? Compare ordinary dictionaries made from them.
- Are any keys stored? Truth testing or length answers that, even when all stored counts are zero.

`elements()` ignores zero and negative counts, so its empty output does not prove the Counter contains no keys. Likewise, unary plus is not a neutral cleanup for signed accounting: it creates a Counter containing only positive counts. It removes negative balances as well as zero entries.

## Conclusion

Name the intended invariant in tests instead of replacing one check with another. If zero entries must be removed while negative balances remain, use an explicit zero-only policy rather than unary plus. If positive multisets are the intended model, unary plus can fit that policy, but preserving the original signed counts may still matter.

For a specific key, `del counter[key]` removes its stored entry; setting its value to zero does not. This finding does not recommend mutating an application's counters automatically. The regression probe uses fresh local objects and deletes only from a copy.

## Action: measured regression probe

Executed 12 assertions on each of CPython **3.13.17** and **3.14.9** on Linux x86_64. All passed, for 24 assertion executions. These are current-build measurements, not a reproduction of pre-3.10 behavior.

| Observation | Result |
|---|---|
| `Counter() == Counter(a=0)` | `True` |
| truth values of those counters | `False`, `True` |
| lengths | `0`, `1` |
| exact dictionary equality | `False` |
| elements from the zero-count counter | `[]` |
| unary plus on `Counter(a=-2, b=0, c=3)` | only `c: 3` remains |
| total before/after unary plus | `1`, `3` |

Save as `probe.py`. There are no file, network or database operations.

```python
import json
import platform
from collections import Counter

empty = Counter()
zero = Counter(a=0)
assert empty == zero
assert bool(empty) is False and bool(zero) is True
assert len(empty) == 0 and len(zero) == 1
assert 'a' not in empty and 'a' in zero
assert empty['a'] == zero['a'] == 0
assert dict(empty) != dict(zero)
assert list(zero.elements()) == []
assert +zero == empty and len(+zero) == 0
signed = Counter(a=-2, b=0, c=3)
assert dict(+signed) == {'c': 3}
assert dict(signed) == {'a': -2, 'b': 0, 'c': 3}
assert signed.total() == 1 and (+signed).total() == 3
copy = zero.copy()
del copy['a']
assert len(copy) == 0 and len(zero) == 1
print(json.dumps({'python': platform.python_version(), 'checks': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe are under the repository's MIT license. Source discussions retain their authorship.
- Only finite integer-count examples on the named interpreter versions were tested. No custom Counter subclass, fractional value, concurrency, performance or production impact is claimed.
- This is documented API behavior. It does not establish a new regression, a data-loss incident or a universal normalization policy.
