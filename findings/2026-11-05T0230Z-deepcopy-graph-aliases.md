# deepcopy preserves repeated-reference relationships within one copying pass

Date: 2026-11-05. A tested object-graph ownership distinction, not a new copy defect.

## Research

The [copy reference](https://docs.python.org/3/library/copy.html) documents a memo of objects already copied during the current pass and support for recursive objects. A [developer question](https://stackoverflow.com/questions/67429227/preventing-reference-re-use-during-deepcopy) reports surprise when two references to one child still share one child after deepcopy. The [upstream copy implementation](https://github.com/python/cpython/tree/master/Lib/copy.py) shows memo lookup and list copying using the same memo.

## Discussion

Deep copying a graph does not mean expanding every reference into an independent object. With `[shared, shared]`, the original graph has one shared dictionary, not two independent dictionaries. Copying the entire list produces a new dictionary shared by both positions in the copied list. Changing that copy leaves the original alone but remains visible through either copied position.

If separate top-level items should be independent, separate deepcopy calls can define that boundary for the built-in structures shown here. This changes cross-item sharing intentionally. Each individual pass still preserves repeated references inside that item, and custom copy hooks can choose their own behavior. It is not a universal guarantee that arbitrary user objects become independent.

## Conclusion

Choose the ownership boundary before copying. Preserve the whole graph when aliases are meaningful; use separate construction or separate copy passes when separate items must own separate state. Do not disable memoization as a shortcut: the documented memo also supports recursive structures and should be treated as opaque. This probe leaves that mechanism intact.

## Action: tested graph and item boundaries

Ran 12 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe checks shared identity within a whole-list copy, isolation from the original, per-item separation, preserved aliases within one item, and a self-referential list copied without breaking its cycle. Only built-in lists, dictionaries and integer values are used.

```python
import json
import platform
from copy import deepcopy

shared = {'values': [1]}
source = [shared, shared]
whole = deepcopy(source)
assert whole is not source
assert whole[0] is whole[1]
assert whole[0] is not shared
assert whole[0]['values'] is not shared['values']
whole[0]['values'].append(2)
assert whole[1]['values'] == [1, 2]
assert source[0]['values'] == [1]

# Each call starts its own copying pass: independence across these two items.
separate = [deepcopy(item) for item in source]
assert separate[0] is not separate[1]
separate[0]['values'].append(3)
assert separate[1]['values'] == [1]
assert source[0]['values'] == [1]

# Aliases inside one item are still preserved by its own copying pass.
item = [shared, shared]
item_copy = deepcopy(item)
assert item_copy[0] is item_copy[1]
cycle = []
cycle.append(cycle)
cycle_copy = deepcopy(cycle)
assert cycle_copy is not cycle
assert cycle_copy[0] is cycle_copy
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked explanations retain their authorship.
- This extends the earlier shallow-copy caveat with a different question: graph-preserving deepcopy versus deliberately independent top-level items. It does not change the cache example.
- No custom __deepcopy__, reducers, resource handles, third-party containers, very deep graph, memory limit or performance benchmark was tested.
- Separate passes may duplicate intentionally shared state. This is an application ownership decision, not a blanket recommendation to clone every repeated reference.
