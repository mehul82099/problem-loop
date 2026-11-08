# Equal numeric keys do not preserve separate type domains

Date: 2026-11-08. Scope: ordinary Python dictionaries and sets with built-in bool, int and float examples.

## Research

A public question shows True, 1 and 1.0 sharing a dictionary entry. The current data model explicitly says equal numeric keys can index the same entry; bool is a subtype of int. The hash reference says equal numeric values have equal hashes even across types. Thus {True: 'boolean', 1: 'integer', 1.0: 'float'} contains one entry whose final value is 'float', not three typed IDs.

## Discussion

False, 0 and 0.0 behave similarly. The probe checks lookup through each of the three equal positive keys, and shows set deduplication also coalescing these values. The string '1' remains distinct from the number 1. A dictionary cannot enforce an application's intended distinction between numeric type domains merely by receiving different built-in numeric types.

This is not failure to handle hash collisions. The historical tracker discussion explicitly corrects that misconception: unequal keys can share a hash and remain separate. The probe uses -1 and -2 to demonstrate same-hash, unequal integer keys coexisting. The independent article likewise separates equality from collision, but its exploratory custom classes are not copied or offered as valid key-design patterns here.

Input validation is a separate choice. isinstance(True, int) is true, so an int-subclass check does not exclude booleans. If a particular ID contract requires exact built-in integers, type(value) is int expresses that narrower rule, also rejecting all int subclasses. Another possible contract is a tagged key such as (type(value), value), which separates the three built-in domains tested here. Neither is a universal normalization rule: choose whether subclasses, equivalent numeric representations and external serialization should preserve or erase type distinctions.

## Conclusion

Decide identity before inserting values into mappings or deduplicating them. Validate a single allowed domain or use an explicit tag when multiple type domains must coexist. Do not change hash values to try to separate objects that remain equal; that breaks the equal-objects/equal-hash contract. The stored representative key's display is not a record of every input type that contributed an update.

## Action

The original MIT-licensed diagnostic below passed 26 checks each on CPython 3.13.17 and 3.14.9. It covers numeric equality and hash consistency, overwrite/lookup, the observed CPython representative, set deduplication, same-hash unequal keys, exact-type rejection and an example tagged domain. This is not an exhaustive numeric-type validator, custom-key recipe, wire format or production schema library.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

check(True == 1 == 1.0, True)
check(hash(True) == hash(1) == hash(1.0), True)
d = {True: 'boolean', 1: 'integer', 1.0: 'float'}
check(len(d), 1)
for key in (True, 1, 1.0):
    check(d[key], 'float')
check(next(iter(d)) is True, True)  # Observed CPython representative.
z = {False: 'boolean', 0: 'integer', 0.0: 'float'}
check(len(z), 1)
check(z[False], 'float')
check(len({True, 1, 1.0}), 1)
check(len({False, 0, 0.0}), 1)
check(len({'1': 'text', 1: 'number'}), 2)
check(isinstance(True, int), True)
check(type(True) is int, False)

# Same hash alone does not mean same entry (ordinary unequal ints).
check(hash(-1) == hash(-2), True)
check(-1 == -2, False)
check(len({-1: 'minus one', -2: 'minus two'}), 2)

# Example contract: exact built-in int only, excluding bool and subclasses.
def exact_integer_id(value):
    if type(value) is not int:
        raise TypeError('expected an exact built-in int ID')
    return value

check(exact_integer_id(1), 1)
for value in (True, False, 1.0, '1'):
    try:
        exact_integer_id(value)
    except TypeError:
        checks += 1
    else:
        raise AssertionError('wrong ID type accepted')

# Alternative example contract: retain these three exact type domains.
typed = {(type(k), k): label for k, label in
         [(True, 'boolean'), (1, 'integer'), (1.0, 'float')]}
check(len(typed), 3)
check(typed[(bool, True)], 'boolean')
check(typed[(int, 1)], 'integer')
check(typed[(float, 1.0)], 'float')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and reproducible probe. This is documented longstanding behavior, not a new dict defect or a hash-collision vulnerability. No private data, external packages or network calls are needed by the probe.

## Sources

All six public pages fetched and inspected in this cycle:

- Python 3.14 data model, boolean subtype and interchangeable equal numeric keys: https://docs.python.org/3.14/reference/datamodel.html
- Python 3.14 built-in hash and isinstance contracts: https://docs.python.org/3.14/library/functions.html#hash
- Historical tracker, expected behavior and same-hash unequal-key counterexample: https://bugs.python.org/issue26614
- CPython documentation discussion, equal mixed-type keys and sets: https://github.com/python/cpython/issues/77753
- Community question showing True, 1 and 1.0 overwrite: https://stackoverflow.com/questions/52402133/true-and-1-and-1-0-evaluated-to-be-same-in-python-dictionaries
- Independent explanation, equality versus collision and CPython key representative: https://dbader.org/blog/python-mystery-dict-expression
