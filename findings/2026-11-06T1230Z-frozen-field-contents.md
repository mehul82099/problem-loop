# Frozen dataclasses do not freeze their field contents

## Research
Public Python questions ask what frozen means and why a dataclass with a generated hash can still be unhashable. Python documents frozen=True as emulating read-only instances by adding assignment/deletion guards. It does not recursively transform field values.

## Discussion
A frozen dataclass can still hold a mutable list. Appending through the field or through an alias changes that list without rebinding the field. With default equality and frozen=True, a hash method is generated, but hashing an instance whose included field is a list raises TypeError. Generating a method is different from making every input value hashable. unsafe_hash=True does not make a list hashable.

This is documented behavior, not a new defect. A tuple of known strings is a useful value representation for the narrow example here, but a tuple containing a list is still shallow and unhashable. An annotation alone does not coerce an incoming list into a tuple. Do not assume a frozen flag or a tuple annotation validates an arbitrary object graph.

## Conclusion
Decide which fields are part of value equality and hashing, then normalize and validate their values at an explicit boundary. The probe converts a known list of strings into a tuple to detach that sequence from later list edits. It does not offer a general recursive-freezing function, input validator or security boundary. Keep all equality/hash-relevant values stable for as long as an object is used as a dictionary key or set member.

## Action: executable probe
Original code under this repository's MIT license. Small in-memory values only. Run without Python optimization so assertions remain enabled.

```python
from dataclasses import dataclass, FrozenInstanceError
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def raises(kind, operation):
    try:
        operation()
    except kind:
        return True
    return False

@dataclass(frozen=True)
class Basket:
    items: list[str]

original = ['a']
basket = Basket(original)
check(basket.items is original)
check(raises(FrozenInstanceError, lambda: setattr(basket, 'items', [])))
check(raises(FrozenInstanceError, lambda: delattr(basket, 'items')))
basket.items.append('b')
check(original == ['a', 'b'])
original.append('c')
check(basket.items == ['a', 'b', 'c'])
check(callable(Basket.__hash__))
check(raises(TypeError, lambda: hash(basket)))
check(raises(TypeError, lambda: {basket}))

@dataclass(frozen=True, unsafe_hash=True)
class Forced:
    items: list[str]

check(raises(TypeError, lambda: hash(Forced(['a']))))

@dataclass(frozen=True)
class Key:
    items: tuple[str, ...]

# Normalize known string input at this boundary, not an arbitrary object graph.
key = Key(tuple(original))
check(key.items == ('a', 'b', 'c'))
original.append('d')
check(key.items == ('a', 'b', 'c'))
check(hash(key) == hash(Key(('a', 'b', 'c'))))
check({key: 'ok'}[Key(('a', 'b', 'c'))] == 'ok')
# Type annotations do not coerce or enforce tuple input at runtime.
wrong = Key(original)
check(wrong.items is original)
check(raises(TypeError, lambda: hash(wrong)))
# A tuple can still contain mutable/unhashable objects.
nested = (['a'],)
nested[0].append('b')
check(nested[0] == ['a', 'b'])
check(raises(TypeError, lambda: hash(nested)))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 17 checks passed on CPython 3.13.17 and 3.14.9.
- Covers assignment/deletion guards, list mutation and aliasing, generated hash failure, unsafe_hash list failure, detached tuple-of-strings key lookup, annotation non-enforcement, and nested mutable tuple contents.
- No custom equality/hash implementation, inheritance, slots, concurrent mutation, recursive graph conversion, persistence or performance test. No claim of protection against deliberate attribute machinery manipulation.
- This concerns field-value immutability, not the earlier asdict copying or replace reconstruction findings.

## Sources
- [Python 3.14 dataclasses](https://docs.python.org/3.14/library/dataclasses.html): frozen guards and hash-generation rules.
- [PEP 557](https://peps.python.org/pep-0557/): original design; current reference wins over older exception details.
- [What does frozen mean?](https://stackoverflow.com/questions/66194804/what-does-frozen-mean-for-dataclasses): community explanation of shallow contents and recursive hash requirements.
- [Why dataclass is unhashable?](https://discuss.python.org/t/why-dataclass-is-unhashable/16258): public hash-generation confusion.
- [Python-Dev, February 2018](https://mail.python.org/pipermail/python-dev/2018-February/152115.html): historical distinction between immutability and hashability.
- [Frozen dataclasses guide](https://www.application-architect.com/posts/python-frozen-dataclasses-immutable-data-objects/): independent list-content example. Broad claims of true immutability are not adopted.
