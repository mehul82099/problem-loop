# dict.values equality does not compare the values

## Research
Two equal dictionaries can produce unequal values views, even when both views come from the same dictionary. Current Python 3.14 documentation explicitly says two distinct dict.values views compare unequal. Public questions show confusion because key and item views support different comparison semantics.

## Discussion
Two calls to values create distinct views; equality is not a sequence or bag comparison. Reusing one view object is different: the probe checks that view == view is true. Older community posts quote broader documentation wording that says values-view comparisons "always" return False. The current documentation qualifies this as two distinct views, and this finding preserves that distinction.

Pick the relation the application actually needs. Dictionary equality compares key-value correspondence regardless of insertion order. List conversion compares value sequences in insertion order. Counter compares value multiplicities without order when all values are hashable. Set conversion ignores multiplicity, so it can declare equal two value collections with different counts. Matching value sequences alone does not establish matching keys.

## Conclusion
Do not use values-view equality as content equality. Choose dictionary, sequence, bag or distinct-value equality explicitly. Collecting a values view into a list captures a shallow sequence of references; the view itself stays live as the dictionary changes. Counter is not a general solution for arbitrary dictionary values because values may be unhashable. This is documented longstanding behavior, not a new bug.

## Action: executable probe
Original code under this repository's MIT license. In-memory dictionaries only. Run without Python optimization so assertions remain enabled.

```python
from collections import Counter
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

a = {'first': 1, 'second': 2, 'third': 1}
b = {'third': 1, 'second': 2, 'first': 1}
check(a == b)
check(a.keys() == b.keys())
check(a.items() == b.items())
check(a.values() != b.values())
check(a.values() != a.values())
view = a.values()
check(view == view)  # Same view object, not two calls to values().
check(view != a.values())
check(list(a.values()) == list(b.values()))  # Palindromic values here.

c = {'second': 2, 'first': 1, 'third': 1}
check(a == c)
check(list(a.values()) != list(c.values()))  # Insertion order matters.
check(Counter(a.values()) == Counter(c.values()))  # Bag comparison.

# Same distinct values, different multiplicity.
d = {'first': 1, 'second': 2, 'third': 2}
check(set(a.values()) == set(d.values()))
check(Counter(a.values()) != Counter(d.values()))
# Same value sequence does not establish key-value correspondence.
e = {'x': 1, 'y': 2, 'z': 1}
check(list(a.values()) == list(e.values()))
check(a != e)

# Values views are live. A list captures references at collection time.
snapshot = list(view)
a['fourth'] = 9
check(list(view) == [1, 2, 1, 9])
check(snapshot == [1, 2, 1])

unhashable = {'a': [1], 'b': [2]}
check(list(unhashable.values()) == [[1], [2]])
try:
    Counter(unhashable.values())
except TypeError:
    rejected = True
else:
    rejected = False
check(rejected)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Checks dictionary/key/item equality controls, distinct versus reused values views, sequence order, bag counts, set multiplicity loss, different keys with matching value sequences, live-view changes and unhashable Counter rejection.
- Tested only ordinary dictionaries with integer/list values and string keys. No NaNs, custom equality/hash implementations, dict subclasses, nested object mutation, concurrent access, performance or arbitrary unhashable bag-comparison algorithm was tested. Converting to list is not a deep copy or a concurrency snapshot guarantee.

## Sources
- [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html): distinct values views compare unequal, dictionary equality, insertion order and live views. The full original page was inspected after the readable fetch omitted the dictionary section.
- [Python 3.14 collections](https://docs.python.org/3.14/library/collections.html): Counter counts hashable objects.
- [Equivalence of dictionary views](https://stackoverflow.com/questions/67097925/equivalence-of-view-objects-of-python-dict): public confusion and same-view distinction; old quoted wording is not treated as current.
- [CPython PR 14737](https://github.com/python/cpython/pull/14737): historical proposed values comparison change, closed in favor of documentation; not a pending implementation fix.
- [Historical issue 37119](https://bugs.python.org/issue37119): Python 2 list-return versus Python 3 view-return confusion; no Python 2 test run here.
- [Python-dev discussion](https://mail.python.org/archives/list/python-dev@python.org/message/K3SYX4DER3WAOWGQ4SPKCKXSXLXTIVAQ/): historical debate over sequence/set/multiset semantics, July 25, 2019; no proposed semantics assumed adopted.
