# dict.fromkeys reuses one value object; a shallow copy can still share nested state

Date: 2026-11-04. A tested object-sharing finding, not a new Python defect.

## Research

The [dictionary reference](https://docs.python.org/3/library/stdtypes.html) explicitly says that all values created by `dict.fromkeys(iterable, value)` refer to a single instance, and recommends a dictionary comprehension when distinct mutable values are wanted. [Issue 36715](https://bugs.python.org/issue36715) led to a documentation note in 2019. The older [issue 6730](https://bugs.python.org/issue6730) closed as "wont fix": implicit per-key copying was not the intended contract.

The [community example](https://stackoverflow.com/questions/8174723/dictionary-creation-with-fromkeys-and-mutable-objects-a-surprise) shows the resulting surprise when appending to a list through one key changes what is visible through another. The [copy reference](https://docs.python.org/3/library/copy.html) supplies the next distinction: a shallow copy makes a new outer container but retains references to its contained objects. Finally, the [collections reference](https://docs.python.org/3/library/collections.html) documents `defaultdict(list)` for on-demand list creation.

## Discussion

`dict.fromkeys(['a', 'b'], [])` evaluates one list value and installs references to it under both keys. Mutating that list through either key is visible through both. Rebinding one key to a new list is different: it changes only that dictionary entry and does not empty or replace the list still referenced by the other key.

A comprehension `{key: [] for key in keys}` evaluates a fresh list expression for each key. But `{key: template.copy() for key in keys}` is only shallow. If the template contains a nested list, the outer lists differ while the nested list remains shared. Fixing the first layer is not evidence that an entire nested object graph is independent.

## Conclusion

Choose the data-construction policy deliberately:

- If all predefined keys need independent empty lists, create the list inside the comprehension.
- If keys should appear only when first accessed, `defaultdict(list)` is a different contract. A missing-key indexed read creates an entry, so this is not equivalent to prepopulating every key.
- If values start from nested templates, define which parts must be independent. Do not call a shallow copy "fully isolated". Deep copying has its own behavior and costs; this finding does not recommend it as a universal fix.

Shared values are not always wrong: `fromkeys` can be suitable when the same value instance is intended. The defect would be an application assumption that its mutable values are independent, not the dictionary API itself.

## Action: measured regression probe

Executed 12 assertions on each of CPython **3.13.17** and **3.14.9**, Linux x86_64. Both passed, for 24 assertion executions. Tests cover shared identity, mutation visibility, rebinding, independent list construction, shallow nested sharing, and lazy creation with defaultdict.

| Construction or operation | Observed result |
|---|---|
| fromkeys with one empty list | both keys refer to the same list |
| append through key a | key b sees the appended item |
| rebind key a to a new list | key b still sees its original list |
| comprehension with a fresh empty list | values are distinct objects |
| per-key shallow copies of a nested template | outer lists differ, inner list is shared |
| defaultdict before a missing-key indexed access | that key is absent |
| defaultdict after that access | a new independent list is stored |

Save as `probe.py`. The probe mutates only freshly created local objects; no files, network or databases are accessed.

```python
import json
import platform
from collections import defaultdict

keys = ['a', 'b']
shared = dict.fromkeys(keys, [])
assert shared['a'] is shared['b']
shared['a'].append(1)
assert shared['b'] == [1]
shared['a'] = []
assert shared['a'] is not shared['b']
assert shared['b'] == [1]

independent = {key: [] for key in keys}
assert independent['a'] is not independent['b']
independent['a'].append(1)
assert independent['b'] == []

template = [[]]
shallow = {key: template.copy() for key in keys}
assert shallow['a'] is not shallow['b']
assert shallow['a'][0] is shallow['b'][0]
shallow['a'][0].append(2)
assert shallow['b'] == [[2]]

lazy = defaultdict(list)
assert len(lazy) == 0
lazy['a'].append(1)
assert 'b' not in lazy
assert lazy['a'] is not lazy['b'] and lazy['b'] == []
print(json.dumps({'python': platform.python_version(), 'checks': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe are under the repository's MIT license. Linked reports retain their authorship.
- Only finite list-valued examples and built-in copying behavior were tested. No custom copy protocol, thread safety, performance, persistence or production impact is claimed.
- This is longstanding documented behavior with an executable check, not a new regression or a claim that every mutable value requires copying.
