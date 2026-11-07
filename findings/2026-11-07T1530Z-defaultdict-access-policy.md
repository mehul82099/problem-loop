# defaultdict subscription creates missing entries; get does not

## Research
Python documents defaultdict.__missing__ as the missing-key path used by dict.__getitem__. If a factory is configured, it is called without arguments and its result is inserted for the key before returning. get and membership tests do not invoke that missing-key path. Public questions show both sides of the surprise: get does not create a default, but after subscription creates one, get can retrieve it normally.

## Discussion
The probe counts factory calls and observes dictionary size. A missing get returns None or its explicit fallback without insertion. A missing subscription creates a list and stores it. Repeated access returns that same list; a different missing key gets a fresh list from this particular factory. This is not a guarantee that every custom factory returns fresh objects.

Existing None is a value, not a missing-key signal: subscription returns it without calling the factory. setdefault follows its own supplied-default policy rather than using default_factory. Setting default_factory=None changes future missing subscriptions to KeyError while existing entries remain available. A synthetic factory failure is propagated unchanged and does not insert the requested key in this example; that is not a rollback guarantee for arbitrary factory side effects.

## Conclusion
Choose non-mutating get/membership for optional reads and subscription when creating a missing entry is intended. Do not mechanically replace one with the other: doing so changes both the returned value and dictionary contents. In sparse data or reporting code, a read-looking subscription can accumulate entries. This is documented behavior, not a new defect, memory benchmark or general concurrency guarantee.

## Action: executable probe
Original code under this repository's MIT license. In-memory mappings and synthetic factory calls only. Run without Python optimization so assertions remain enabled.

```python
from collections import defaultdict
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

calls = []
def factory():
    calls.append('called')
    return []

d = defaultdict(factory)
check(d.get('absent') is None)
sentinel = object()
check(d.get('absent', sentinel) is sentinel)
check('absent' not in d)
check(len(d) == 0 and calls == [])
first = d['absent']
check(first == [] and calls == ['called'])
check('absent' in d and len(d) == 1)
check(d.get('absent') is first)
check(d['absent'] is first and len(calls) == 1)
second = d['other']
check(second == [] and second is not first)
check(len(calls) == 2)
first.append('owned')
check(d['absent'] == ['owned'] and d['other'] == [])

d['explicit_none'] = None
check(d['explicit_none'] is None)
check(len(calls) == 2)
# setdefault uses its supplied default, not this mapping's factory.
check(d.setdefault('via_setdefault', None) is None)
check('via_setdefault' in d and len(calls) == 2)

d.default_factory = None
check(d['absent'] is first)  # Existing entries are unaffected.
try:
    d['new']
except KeyError as exc:
    missing = exc.args == ('new',)
else:
    missing = False
check(missing and 'new' not in d)

failure = RuntimeError('synthetic factory failure')
def fail():
    raise failure

broken = defaultdict(fail)
try:
    broken['x']
except RuntimeError as exc:
    same_error = exc is failure
else:
    same_error = False
check(same_error)
check('x' not in broken and len(broken) == 0)
check(broken.get('x', 'fallback') == 'fallback')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Covers missing get/default/membership without insertion, factory call counts, inserted and reused values, independent lists from this factory, existing None, setdefault's own policy, factory removal, missing KeyError and unchanged propagated factory exception without insertion.
- No concurrent access, reentrant factories, custom hash/equality, mapping subclasses, shared-return factories, filesystem or network work, arbitrary factory rollback, performance or memory-size claim was tested. This is distinct from the earlier setdefault eager-default finding; the focus here is which lookup operations create missing entries.

## Sources
- [Python 3.14 collections](https://docs.python.org/3.14/library/collections.html): defaultdict factory, insertion, missing path, get exception and writable default_factory.
- [Python 3.14 standard types](https://docs.python.org/3.14/library/stdtypes.html): dict get, membership and setdefault policies.
- [Default value unless key referenced first](https://stackoverflow.com/questions/29109036/pythons-collections-defaultdict-returns-default-value-correctly-unless-the-key): community get/subscription/membership question; custom mapping recipes not adopted.
- [get changes after subscription](https://stackoverflow.com/questions/79367821/defaultdict-get-returns-item-and-not-none-after-calling-after-operator): January 18, 2025 question about retrieving a previously created entry.
- [Real Python defaultdict guide](https://realpython.com/python-defaultdict/): independent explanation; broad 'access' wording is narrowed here to the documented missing subscription path.
- [defaultdict as sparse array](https://pzel.name/til/2023/12/10/Python-defaultdict-as-sparse-array-use-with-caution.html): December 10, 2023 independent caution about read-like insertions. Its scale/performance results were not reproduced or claimed here.
