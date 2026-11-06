# wraps preserves metadata, not the wrapper's call binding

## Research
Public decorator questions conflate the signature shown by inspect.signature with the arguments a wrapper receives. functools.wraps updates metadata and sets `__wrapped__`. inspect.signature follows that attribute by default. A wrapper defined with *args and **kwargs still receives arguments according to its own definition.

## Discussion
An invalid call can enter a permissive wrapper, run its logging or other work, and only then fail when forwarded to the wrapped function. Default parameter values are not automatically injected into the wrapper's kwargs. The advertised signature is useful introspection metadata, not an argument-validation gate in front of the wrapper body.

This is documented behavior, not a new defect. For a known callable whose signature the decorator promises to preserve, Signature.bind can check argument shape before other wrapper work, and apply_defaults can populate a bound argument mapping. This does not validate types, values or the wrapped function's business rules. It also does not repair a decorator that intentionally changes its calling convention.

## Conclusion
Separate the interface advertised by introspection, the wrapper's runtime binding and the target's validation. If invalid argument shape must be rejected before wrapper side effects, explicitly bind before those effects or use a correctly defined wrapper interface. The probe uses a simple Python function with a positional-only input and keyword-only default; it is not a universal decorator factory.

## Action: executable probe
Original code under this repository's MIT license. In-memory functions and event lists only. Run without Python optimization so assertions remain enabled.

```python
from functools import wraps
from inspect import signature
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def target(x, /, *, scale=2):
    """Multiply x."""
    return x * scale

events = []
@wraps(target)
def wrapper(*args, **kwargs):
    events.append((args, kwargs.copy()))
    return target(*args, **kwargs)

check(wrapper.__name__ == target.__name__)
check(wrapper.__doc__ == target.__doc__)
check(wrapper.__wrapped__ is target)
check(str(signature(wrapper)) == '(x, /, *, scale=2)')
check(str(signature(wrapper, follow_wrapped=False)) == '(*args, **kwargs)')
check(wrapper(3) == 6)
check(events == [((3,), {})])  # Default was not injected into kwargs.

for args, kwargs in [((), {}), ((), {'x': 3}), ((3, 4), {})]:
    events.clear()
    rejected = False
    try:
        wrapper(*args, **kwargs)
    except TypeError:
        rejected = True
    check(rejected)
    check(len(events) == 1)  # Wrapper work happened before target rejection.

sig = signature(target)
@wraps(target)
def checked(*args, **kwargs):
    bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    events.append(dict(bound.arguments))
    return target(*bound.args, **bound.kwargs)

events.clear()
check(checked(3) == 6)
check(events == [{'x': 3, 'scale': 2}])
events.clear()
rejected = False
try:
    checked(x=3)
except TypeError:
    rejected = True
check(rejected)
check(events == [])
check(checked(3, scale=4) == 12)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 18 checks passed on CPython 3.13.17 and 3.14.9.
- Tests copied metadata, wrapped reference, default versus follow_wrapped=False introspection, absent kwargs defaults, wrapper execution before three invalid target calls, explicit bind/default application and early rejection before the demonstration event.
- No custom signature attribute, callable class, built-in/extension function, descriptor, static type checker, stacked decorator, async function, performance or production side effect was tested. Introspection can have limits or be customized; this sample does not handle arbitrary callables.

## Sources
- [Python 3.14 functools](https://docs.python.org/3.14/library/functools.html): update_wrapper/wraps metadata contract.
- [Python 3.14 inspect](https://docs.python.org/3.14/library/inspect.html): signature unwrapping, bind and apply_defaults.
- [What does wraps do?](https://stackoverflow.com/questions/308999/what-does-functools-wraps-do): community distinction between displayed and runtime signature; old attribute lists are not treated as exhaustive today.
- [Please Fix Your Decorators](https://hynek.me/articles/decorators/): historical introspection discussion. Its older API/version limitations are not current claims here.
- [Python discussion on argument signatures](https://discuss.python.org/t/taking-the-argument-signature-from-a-different-function/42618): different wrapper versus wrapped signatures; static-tool claims not tested.
- [Stacked decorator/defaults question](https://stackoverflow.com/questions/59863010/preserve-exact-function-signature-in-chain-of-decorators-using-functools-wraps): concrete missing-default confusion; proposed validation snippets not adopted.
