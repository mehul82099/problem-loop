# cached_property does not track dependencies or invalidate itself

## Research
functools.cached_property computes on an attribute lookup only when that attribute is absent from the instance, then stores the result as a normal attribute. Changing another field does not tell it that its answer is stale. Current documentation recommends it for expensive computed properties on effectively immutable instances and explicitly allows assignment and deletion of the cached attribute.

## Discussion
The probe changes a source field after reading the cached result: the old answer remains. Assigning directly to the cached attribute shadows the getter. Deleting it makes the next read recompute. Plain deletion before the cache exists can raise AttributeError; for an ordinary instance dictionary, removing the known cache key with pop and a default avoids that absent-key failure without evaluating the getter.

A public reset discussion shows a subtle trap: hasattr is an attribute lookup, not a passive test of instance dictionary contents. It can compute the very cached property that the caller only wanted to clear. The probe verifies this separately. Direct dictionary invalidation here is scoped to the ordinary class shown, not arbitrary descriptors or custom attribute machinery.

## Conclusion
Choose an immutable input model or explicitly invalidate this cache on every relevant mutation path. A local reset helper does not discover dependencies, intercept mutations inside nested objects or provide concurrency safety. Current docs say concurrent first reads can execute the getter more than once; no exactly-once claim is made. A slots-only instance without a mutable instance dictionary cannot use this decorator as shown. This is documented behavior, not a new defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory ordinary instances only. Run without Python optimization so assertions remain enabled.

```python
from functools import cached_property
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class Meter:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    @cached_property
    def doubled(self):
        self.calls += 1
        return self.value * 2

    def invalidate(self):
        self.__dict__.pop('doubled', None)

m = Meter(3)
check('doubled' not in m.__dict__)
m.invalidate()
check(m.calls == 0)
check(m.doubled == 6)
check(m.doubled == 6 and m.calls == 1)
check(m.__dict__['doubled'] == 6)
m.value = 5
check(m.doubled == 6 and m.calls == 1)  # Dependency not tracked.
m.doubled = 99
check(m.doubled == 99 and m.calls == 1)  # Assignment shadows getter.
del m.doubled
check('doubled' not in m.__dict__)
check(m.doubled == 10 and m.calls == 2)
m.invalidate()
m.invalidate()
check(m.calls == 2)
check(m.doubled == 10 and m.calls == 3)
other = Meter(7)
check(other.doubled == 14 and other.calls == 1)
check(m.calls == 3)

# hasattr performs a lookup, so it can populate this cache.
fresh = Meter(4)
check(hasattr(fresh, 'doubled'))
check(fresh.calls == 1 and fresh.__dict__['doubled'] == 8)
del fresh.doubled
try:
    del fresh.doubled
except AttributeError:
    absent_delete_failed = True
else:
    absent_delete_failed = False
check(absent_delete_failed)
check(fresh.calls == 1)

class SlotsOnly:
    __slots__ = ()

    @cached_property
    def answer(self):
        return 42

try:
    SlotsOnly().answer
except TypeError:
    no_dict_failed = True
else:
    no_dict_failed = False
check(no_dict_failed)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 18 checks passed on CPython 3.13.17 and 3.14.9.
- Covers first/repeated reads, stored instance value, stale dependency, assignment override, deletion/recomputation, idempotent reset without lookup, per-instance state, hasattr evaluation, absent deletion and slots-only rejection.
- No threads, async calls, custom __getattribute__/__setattr__, nested mutable inputs, getter exceptions, inheritance, memory benchmark, production invalidation framework or automatic dependency tracking was tested. The calls counter demonstrates sequential evaluations only.

## Sources
- [Python 3.14 functools](https://docs.python.org/3.14/library/functools.html): cached_property lookup/write/delete semantics, dictionary requirement and concurrent-read caveat.
- [CPython functools, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/functools.py): descriptor implementation context, not identity of the tested builds.
- [Python reset discussion](https://discuss.python.org/t/best-practice-for-reseting-functools-cached-property/76667): absent-delete and hasattr lookup issue, January 10, 2025.
- [Updating a cached property after nested change](https://stackoverflow.com/questions/74748675/python-update-cached-property-when-field-of-attribute-changes): public dependency-invalidation question; alternative caching helpers not adopted.
- [Clearing cached_property](https://stackoverflow.com/questions/62662564/how-do-i-clear-the-cache-from-cached-property-decorator): historical/current deletion discussion; older claims that deletion is undocumented are not current claims here.
- [PythonLessonLab invalidation guide](https://pythonlessonlab.com/lessons/cached-property-and-invalidation/): independent explanation of instance storage and controlled invalidation; broad safety language is limited by the caveats above.
