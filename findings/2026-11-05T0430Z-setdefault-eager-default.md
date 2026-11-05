# setdefault receives an evaluated default value, not a lazy factory

Date: 2026-11-05. A tested call-boundary distinction for documented dictionary behavior, not a new defect or speed benchmark.

## Research

A [public comparison of setdefault and defaultdict](https://softwareengineering.stackexchange.com/questions/355960/what-is-the-difference-between-the-solution-that-uses-defaultdict-and-the-one-th) explains that the default argument is evaluated before setdefault is called. The [collections reference](https://docs.python.org/3/library/collections.html) specifies a different interface: defaultdict calls its no-argument factory on missing subscription, inserts the result and returns it. An [independent defaultdict guide](https://realpython.com/python-defaultdict/) also notes that get() does not invoke that factory.

## Discussion

In `d.setdefault(key, build())`, build() runs even when key already exists. The method can return the existing value without using the new object, but it cannot undo the argument evaluation. This matters if constructing a default does more than allocate a small empty list. The probe counts calls rather than claiming a measured speed advantage.

A defaultdict stores a callable, not its result: use `defaultdict(build)`, not `defaultdict(build())`. Its missing-key factory belongs to subscription, such as dd[key]. It does not run for dd.get(key). Passing build() as an explicit get default is still an ordinary eager argument evaluation, even on a defaultdict hit.

## Conclusion

Choose the intended missing-key behavior, not just shorter syntax. For uniform no-argument factory behavior on missing subscription, defaultdict can avoid unnecessary explicit construction. For read-only lookup, get does not insert or call the factory. Neither choice means every dictionary operation is lazy or every factory result is independent; the factory must create the ownership behavior you want.

## Action: tested factory-call boundaries

Ran 17 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe verifies eager defaults on setdefault hits/misses, retained object identity, get bypassing the factory without inserting, one factory call on missing subscription, reuse on hits, distinct lists for different keys and eager explicit get defaults.

```python
import json
import platform
from collections import defaultdict

calls = []
def build():
    calls.append('build')
    return []

d = {'present': [1]}
original = d['present']
assert d.setdefault('present', build()) is original
assert len(calls) == 1
assert d['present'] == [1]
missing = d.setdefault('missing', build())
assert len(calls) == 2
assert d['missing'] is missing
assert d.setdefault('missing', build()) is missing
assert len(calls) == 3
calls.clear()
dd = defaultdict(build)
assert dd.get('x') is None
assert 'x' not in dd
assert calls == []
x = dd['x']
assert len(calls) == 1
assert dd['x'] is x
assert len(calls) == 1
assert dd['y'] is not x
assert len(calls) == 2
calls.clear()
assert dd.get('x', build()) is x
assert len(calls) == 1
print(json.dumps({'python': platform.python_version(), 'cases': 17, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked explanations retain their authorship.
- Only local call logging and list allocation were used. No files, sockets, network requests, external side effects or user data were involved.
- No timing, memory, concurrency, atomicity, reentrant factory or failure-recovery behavior was tested. This is not a recommendation to hide I/O inside a default factory.
- The separate factory-call and object-identity assertions apply to this build() function. A factory returning the same global object would still share that object between keys.
