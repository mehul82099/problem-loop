# dataclasses.asdict is recursive conversion, not a shallow field view

Date: 2026-11-06. A documented copy boundary, not a new dataclasses defect.

## Research

The [Python 3.14 dataclasses reference](https://docs.python.org/3.14/library/dataclasses.html) says asdict recursively converts dataclasses and supported containers, and deep-copies other objects. It supplies a fields/getattr comprehension when a shallow mapping is wanted. The [copy reference](https://docs.python.org/3.14/library/copy.html) documents custom deepcopy hooks and distinguishes shallow from deep copying.

[Issue 43905](https://bugs.python.org/issue43905) records identity-sensitive lookup failures and led to a [2021 documentation change](https://github.com/python/cpython/commit/c1f93f0d378958dfae4f24aad0c0088e3e04e403). A [separate report](https://github.com/python/cpython/issues/89298) demonstrates a leaf copy hook raising during asdict. A [2023 community performance discussion](https://discuss.python.org/t/dataclasses-make-asdict-astuple-faster-by-skipping-deepcopy-for-objects-where-deepcopy-obj-is-obj/24662) distinguishes copy behavior from optimizations for atomic values. This finding does not claim every scalar gets a fresh object or every field invokes a hook.

## Discussion

An asdict result can look like a simple field-name mapping while its values have already been recursively transformed. A nested dataclass becomes a dictionary. A list in that nested record becomes a separate list in this probe. An object used as an identity-sensitive token is copied, so it no longer matches the original token's lookup entry.

A custom leaf can also reject copying through its deepcopy hook. Supplying a custom dict_factory does not make the operation shallow: the controlled failure below happens while converting the leaf, before constructing the outer mapping.

## Conclusion

Choose whether the caller needs recursive conversion or a shallow field mapping. The fields/getattr approach preserves the original field objects, including identity tokens, but also shares their mutable state. It is not an isolated snapshot and does not recursively serialize nested dataclasses. Neither operation alone supplies an application's wire format or guarantees JSON compatibility. Do not switch between them silently.

## Action

Original MIT-licensed probe using owned local records, lists and a controlled copy hook. It checks structural conversion, mutable-list independence, token identity, shallow sharing and a copy failure. No files or external objects are read.

```python
import json
import platform
from dataclasses import asdict, dataclass, fields

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

@dataclass
class Child:
    numbers: list

@dataclass
class Record:
    child: Child
    token: object

original = Record(Child([1]), object())
converted = asdict(original)
check(isinstance(converted['child'], dict))
check(converted['child']['numbers'] == [1])
check(converted['child']['numbers'] is not original.child.numbers)
converted['child']['numbers'].append(2)
check(original.child.numbers == [1])
check(converted['token'] is not original.token)
lookup = {original.token: 'owned value'}
check(converted['token'] not in lookup)

shallow = {field.name: getattr(original, field.name) for field in fields(original)}
check(shallow['child'] is original.child)
check(shallow['token'] is original.token)
check(lookup[shallow['token']] == 'owned value')
shallow['child'].numbers.append(3)
check(original.child.numbers == [1, 3])

# A controlled custom leaf: even a custom dict factory does not disable
# the recursive conversion and leaf-copy step that precede it.
events = []
class RefusesCopy:
    def __deepcopy__(self, memo):
        events.append('copy attempted')
        raise ValueError('controlled copy refusal')

@dataclass
class Holder:
    value: object

raised = False
try:
    asdict(Holder(RefusesCopy()), dict_factory=lambda items: dict(items))
except ValueError as error:
    raised = str(error) == 'controlled copy refusal'
check(raised)
check(events == ['copy attempted'])

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 12 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. The identity example uses object(), not immutable scalar values. Custom container subclasses, cycles, alias preservation across fields, performance and serialization are not tested. Repository CI is separate.

## Publisher

One evidence-backed finding and bounded executable probe. No universal serializer, dataclasses replacement or production data conversion.
