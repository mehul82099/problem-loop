# Single dispatch selects a handler, not an exact-type validation rule

Date: 2026-11-09. Evidence-backed Python dispatch finding, not a new functools defect.

## Research

Python's versioned functools references specify dispatch on the first argument's type. If there is no registration for its exact type, inheritance can select a registered ancestor. The original function supplies the object fallback. PEP 443 records the same single-dispatch model.

Closed CPython issue 105883 reports surprise when True reaches an int implementation without a bool registration. The response explains that bool is an int subclass and that a distinct bool handler must be registered for distinct behavior. This is documented selection, not conversion of the input into an integer or an unresolved bug.

## Discussion

With only an int registration, ordinary integers, booleans and a custom int subclass select that handler. The fixture returns type(value) from inside the handler: True is still a bool and the custom instance is still its subclass. Dispatch has not coerced them into exact built-in ints.

Changing the second argument among a number, text, list or dictionary does not change which handler is selected for the same first value. Later arguments can still affect what a handler does or whether it raises; they simply do not select the implementation. A later parameter's str annotation in the separate fixture does not reject list or int arguments at runtime.

| Requirement | Relevant distinction |
| --- | --- |
| Inheritance-based specialization | A parent registration can handle subclasses |
| Distinct Boolean behavior | Register bool explicitly or apply a deliberate handler-level policy |
| Exact built-in int acceptance | Enforce exact-type requirements separately if the application needs them |
| Behavior based on two runtime types | Not supplied by singledispatch selection |

Registering bool after the fixture has already dispatched it changes subsequent Boolean selection, while ordinary integers and the int subclass still use the integer handler. The registry is an extension point, not a frozen validation whitelist. The probe also records that calling this ordinary generic function with only value=7 and no positional argument raises TypeError.

## Conclusion

Test handler selection with dispatch(type), actual received types, subclasses and fallback values. Keep dispatch separate from argument validation and coercion. If Boolean inputs are accepted, rejected or treated specially, name that policy rather than assuming an int registration excludes them. No application acceptance policy is chosen by this demonstration.

The earlier integer-index and numeric-key findings also mention bool/int relationships, but do not test runtime handler selection. The earlier wraps finding concerns introspection versus call binding. This increment is limited to a single generic function's selection and registration behavior.

## Action

Original code under this repository's MIT license. Bounded in-memory calls only. Run without Python optimization so assertions remain enabled.

```python
from functools import singledispatch
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class SmallInt(int):
    pass

@singledispatch
def label(value, context=None):
    return ('fallback', type(value), context)

@label.register(int)
def integer_label(value, context=None):
    # Do not coerce the value; expose its actual received type.
    return ('integer', type(value), context)

values = list(range(-20, 21)) + [True, False, SmallInt(7)]
contexts = [None, 3, True, 'text', [], {}]
for value in values:
    check(label.dispatch(type(value)) is integer_label)
    for context in contexts:
        result = label(value, context)
        check(result == ('integer', type(value), context))
        check(result[2] is context)

check(label('7', 9)[0] == 'fallback')
check(label(1.0, 9)[0] == 'fallback')
check(label(None, 9)[0] == 'fallback')
check(label.dispatch(bool) is integer_label)

@label.register(bool)
def boolean_label(value, context=None):
    return ('boolean', type(value), context)

check(label.dispatch(bool) is boolean_label)
check(label.dispatch(SmallInt) is integer_label)
for context in contexts:
    check(label(True, context) == ('boolean', bool, context))
    check(label(False, context) == ('boolean', bool, context))
    check(label(1, context) == ('integer', int, context))
    check(label(SmallInt(1), context) == ('integer', SmallInt, context))
check(label.registry[int] is integer_label)
check(label.registry[bool] is boolean_label)
# A keyword-only first value is not inspected by this dispatcher.
try:
    label(value=7)
except TypeError:
    check(True)
else:
    raise AssertionError('expected positional dispatch requirement')

# A later parameter annotation is not runtime validation.
@singledispatch
def annotated(value, other):
    return 'fallback'

@annotated.register
def annotated_int(value: int, other: str):
    return type(other)

check(annotated(3, []) is list)
check(annotated(3, 7) is int)
check(annotated('3', 'text') == 'fallback')
print(json.dumps({'checks': checks, 'python': platform.python_version(),
                  'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **608 checks passed per build**. Covers integers -20..20, both booleans, one int subclass and six later-argument shapes; handler introspection, received-type preservation, second-argument identity, fallback, later bool registration, positional requirement and one annotation-registration fixture.

No singledispatchmethod, abstract/virtual subclass ambiguity, union/container-element registration, registration races, plugins, performance, custom metaclasses or production input validation was tested. The public issue also discusses method dispatch, but only ordinary singledispatch is executed here. No exact-type validator or multi-dispatch framework is supplied.

## Publisher

One bounded finding and standalone probe. Full targeted repository search found no prior singledispatch coverage. Related bool/type and wrapper topics are distinguished above; no claim of newly discovered inheritance behavior is made.

## Sources

1. [Python 3.13 functools reference](https://docs.python.org/3.13/library/functools.html), primary documentation: first-argument selection, subclass fallback, registration and dispatch introspection.
2. [Python 3.14 functools reference](https://docs.python.org/3.14/library/functools.html), primary documentation: same single-dispatch contract and annotation-based registration.
3. [PEP 443](https://peps.python.org/pep-0443/), standards-track design: generic functions and first-argument inheritance-based selection. Broader ABC examples are outside the probe.
4. [CPython issue 105883](https://github.com/python/cpython/issues/105883), closed June 2023 report/discussion: Boolean arguments use the int handler when no bool handler is registered; documented behavior, not a current open defect.
5. [CodeWiki single-dispatch generic functions](https://codewiki.com/python/singledispatch/), independent reference: runtime selection versus later arguments, annotations and handler signatures. Its broader examples are not locally claimed as tested.
6. [PythonLessonLab singledispatch lesson](https://pythonlessonlab.com/lessons/functools-singledispatch/), independent teaching example: specific bool registration and first-argument-only selection. No publication date shown; no lesson code copied into this probe.
