# Insertion order is not last-update or last-access order

Date: 2026-11-08. Scope: ordinary Python dict and collections.OrderedDict with simple string keys.

## Research

A public question asks how to make update() move an existing entry to the end. The current reference states that dict preserves insertion order, updating a key does not affect that order, and keys added after deletion go at the end. OrderedDict also leaves an overwritten key in place unless an explicit reordering operation is used.

## Discussion

The probe updates the oldest dict key and confirms it stays first. Updating another existing key and adding a new one changes values in place and appends only the new key. Reading an entry does not make it most recently used. A plain dict therefore does not become a last-updated or last-accessed cache just because its iteration is ordered.

For a deliberate move to the right endpoint, the collections reference documents d[k] = d.pop(k) as an emulation. This removes and reinserts the key; it is not a concurrent or exception-safe cache transaction. OrderedDict.move_to_end() expresses explicit reordering and can also move a key to the left endpoint. A real cache still needs its own access/update policy, eviction rules and synchronization.

Equality is another boundary: two dicts can compare equal while iterating in different orders. Comparing list(d.items()) tests order as well as contents for the simple-key examples here. Two OrderedDicts compare with order sensitivity, but OrderedDict-to-dict equality ignores order. The probe demonstrates two differently ordered OrderedDicts both equal to the same plain dict while unequal to one another; do not mix these comparisons as a universal order-sensitive equivalence test.

Historical material needs its date. PEP 372 described ordinary dicts as unordered when proposing OrderedDict in 2008. The current documentation guarantees dict insertion order from Python 3.7. The PEP is used for original overwrite semantics, not as a description of current dict guarantees. No disagreement remains once those versions are separated.

## Conclusion

Specify which order the application needs: initial insertion, last write, last access, a sorted order or an explicit workflow order. Ordinary assignment supplies the first of those, not all of them. Use explicit reordering when recency is intended and explicit ordered-content comparison when order is part of correctness. This complements the earlier shallow-union finding by testing recency and equality, not nested-copy or merge policy.

## Action

Original MIT-licensed diagnostic code below passed 25 checks each on CPython 3.13.17 and 3.14.9. It covers update/read position, deletion and reinsertion, duplicate constructor keys, reverse iteration, endpoint moves, pop behavior and mixed equality. It is not a cache implementation, concurrency test, benchmark or guarantee about custom Mapping subclasses.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
from collections import OrderedDict
import json
import platform

checks = 0

def check(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

d = {'a': 1, 'b': 2, 'c': 3}
d['a'] = 10
check(list(d), ['a', 'b', 'c'])
check(d['a'], 10)
d.update(b=20, d=4)
check(list(d), ['a', 'b', 'c', 'd'])
check(d['b'], 20)
check(d['b'], 20)  # A read does not update recency.
check(list(d), ['a', 'b', 'c', 'd'])
d['a'] = d.pop('a')
check(list(d), ['b', 'c', 'd', 'a'])
check(d['a'], 10)
check(d.popitem(), ('a', 10))
check(list(d), ['b', 'c', 'd'])

a = dict([('x', 1), ('y', 2), ('x', 3)])
check(list(a.items()), [('x', 3), ('y', 2)])
b = {'y': 2, 'x': 3}
check(a == b, True)
check(list(a.items()) == list(b.items()), False)
check(list(reversed(a)), ['y', 'x'])

od = OrderedDict(a)
od['x'] = 30
check(list(od), ['x', 'y'])
od.move_to_end('x')
check(list(od), ['y', 'x'])
check(od['x'], 30)
od.move_to_end('x', last=False)
check(list(od), ['x', 'y'])
check(od.popitem(last=False), ('x', 30))
check(list(od), ['y'])

left = OrderedDict([('x', 1), ('y', 2)])
right = OrderedDict([('y', 2), ('x', 1)])
plain = {'x': 1, 'y': 2}
check(left == right, False)
check(left == plain, True)
check(right == plain, True)  # Mixed comparisons ignore order.
try:
    left.move_to_end('missing')
except KeyError:
    checks += 1
else:
    raise AssertionError('missing key should fail')
check(list(left), ['x', 'y'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and reproducible probe. Documented behavior, not a new defect or an upstream change. No private data, external packages or network calls are needed by the probe.

## Sources

Six public sources inspected during this cycle:

- Python 3.14 mapping reference, current insertion-order guarantee and update/delete behavior. The full-page text extraction ended before the mapping section, so the exact HTML section was also retrieved and inspected: https://docs.python.org/3.14/library/stdtypes.html
- Python 3.14 collections reference, endpoint moves, plain-dict emulation and mixed equality: https://docs.python.org/3.14/library/collections.html
- PEP 372, historical design and overwrite semantics, not current ordinary-dict order guarantees: https://peps.python.org/pep-0372/
- Independent explanation of update, reinsertion and reordering: https://realpython.com/python-ordereddict/
- Public question asking for last-update ordering: https://stackoverflow.com/questions/39681839/how-to-ensure-update-adds-to-end-of-dictionary
- Public replacement/reinsertion question: https://stackoverflow.com/questions/33405759/replacing-an-element-in-an-ordereddict
