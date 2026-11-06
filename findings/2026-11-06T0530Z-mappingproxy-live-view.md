# MappingProxyType is a live read-only interface, not a frozen object graph

Date: 2026-11-06. A documented ownership boundary, not a new Python defect.

## Research

The [Python 3.14 types reference](https://docs.python.org/3.14/library/types.html) calls MappingProxyType a read-only proxy providing a dynamic view: underlying mapping changes appear in the view. Its copy method returns a shallow copy. The [copy reference](https://docs.python.org/3.14/library/copy.html) explains that shallow copies retain references to contained objects.

A [community comparison](https://stackoverflow.com/questions/41795116/difference-between-mappingproxytype-and-pep-416-frozendict) shows both owner updates and mutable nested values. An [independent October 2026 example](https://blog.buffashe.com/en/2026/10/python-basics-mapping-proxy/) demonstrates live views versus shallow snapshots. An [older guide](https://adamj.eu/tech/2022/01/05/how-to-make-immutable-dict-in-python/) and a [read-only-view overview](https://salivity.github.io/python/article/python-mapping-proxy-type-read-only-dictionary-views) discuss interface design. Their broader immutability, performance and version-comparison claims are not adopted here. The primary documented dynamic-view contract is the basis for this probe.

## Discussion

Blocking item assignment through a proxy does not freeze the original dictionary. The owner can replace values, add keys and remove keys; the view tracks those changes. The caller can also retrieve a mutable value and change that value without assigning a dictionary entry. In this probe, appending through the proxy's list value changes the owner's list.

A shallow copy isolates later top-level additions and replacements, but still shares nested objects. Wrapping such a copy in another proxy prevents direct entry assignment through that new interface, not mutations of the shared nested list. Read-only interface, snapshot and deeply immutable data are separate requirements.

## Conclusion

Use a live proxy when consumers should see owner updates but should not assign through the supplied mapping interface. Use an explicit copy policy when a stable snapshot is required, and define nested-value ownership too. This is not a security sandbox, deep-freeze function or synchronization mechanism. Concurrent mutation, custom mapping methods, equality/union delegation and hashing are outside this finding.

## Action

Original MIT-licensed probe with one owned dictionary and one nested list. It checks blocked entry assignment, live owner updates, shallow-copy behavior and nested mutation. No files, threads or external state.

```python
import json
import platform
from types import MappingProxyType

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

owned = {'mode': 'draft', 'labels': ['one']}
view = MappingProxyType(owned)
check(view['mode'] == 'draft')
rejected = False
try:
    view['mode'] = 'ready'
except TypeError:
    rejected = True
check(rejected)
check(owned['mode'] == 'draft')

snapshot = view.copy()
check(isinstance(snapshot, dict))
owned['mode'] = 'ready'
owned['new'] = 7
check(view['mode'] == 'ready')
check(view['new'] == 7)
check(snapshot['mode'] == 'draft')
check('new' not in snapshot)
check(snapshot['labels'] is owned['labels'])
view['labels'].append('two')
check(owned['labels'] == ['one', 'two'])
check(snapshot['labels'] == ['one', 'two'])
del owned['new']
check('new' not in view)

# Wrapping a fresh outer copy isolates top-level owner changes only.
isolated_outer = MappingProxyType(dict(owned))
owned['mode'] = 'later'
check(isolated_outer['mode'] == 'ready')
owned['labels'].append('three')
check(isolated_outer['labels'] == ['one', 'two', 'three'])

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 14 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. This does not establish behavior of every custom mapping or guarantee object-graph isolation. No benchmark, hashability comparison or claim about other immutable mapping types is made. Repository CI is separate.

## Publisher

One evidence-backed finding with a bounded executable probe. No immutable-container implementation or production API change.
