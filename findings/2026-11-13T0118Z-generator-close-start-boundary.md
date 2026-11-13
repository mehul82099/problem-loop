# Closing an unstarted generator does not enter its cleanup block

Date: 2026-11-13. A generator execution and ownership finding, not a new Python defect.

## Research

Historical Python issue 23227 reports a generator wrapping an already-open resource: close before the first iteration did not run its finally block. The issue is closed as not a bug. The language reference describes deferred generator execution and close raising GeneratorExit at the suspension point; PEP 342 gives the original close/throw model. The finally clause cannot clean up through a try block the generator never entered.

A later public question asks the same unstarted-generator question. Neither report establishes current production impact. This probe uses a fake resource recording events, not actual open files or connections.

## Discussion

Calling a generator function creates its iterator without running the function body. In the tested build, closing that created iterator moves it directly to GEN_CLOSED without entering the body. If the caller acquired a resource before passing it into the generator, that resource can still need cleanup even though the generator body never started.

For the comparison generator, acquisition is inside the body. With zero iterations, neither acquisition nor cleanup happens. Once execution has entered the resource context and reached yield, explicit close runs its cleanup. Normal exhaustion also cleans up. These are different ownership contracts, not two equivalent wrappers.

The earlier StopIteration forwarding report concerns exhaustion escaping a generator body. It explicitly excludes close semantics; this finding instead measures created, suspended and exhausted lifetime boundaries.

## Conclusion

Keep cleanup responsibility with the code that owns acquisition. A caller-owned context can manage an already-acquired resource independently of whether a consumer starts iterating. Alternatively, acquiring inside the generator can align acquisition with entered generator cleanup, provided the driver explicitly ends its lifetime when it stops early. contextlib.closing calls close on context exit; it does not force an unstarted generator body to run. Do not prime a generator just to trigger cleanup: priming also executes application work and may consume a value.

This is not a generic resource wrapper, a guarantee about garbage-collection timing or permission to suppress cleanup errors. Choose one cleanup owner; the fake resource is diagnostic only.

## Action

Original code under this repository's MIT license. Run without optimization so assertions stay enabled. Only local objects, event lists and synchronous generators are used. No file, network, thread or external resource is acquired.

```python
import inspect
import json
import platform
from contextlib import closing

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

class Resource:
    def __init__(self, events):
        self.events = events
        self.closed = False
        events.append('acquire')
    def close(self):
        self.closed = True
        self.events.append('release')

# This wrapper accepts an already-acquired resource.
def borrowed(resource, events):
    try:
        events.append('enter')
        yield 1
        yield 2
    finally:
        resource.close()

# Here acquisition belongs inside the generator's execution lifetime.
def owned(events):
    with closing(Resource(events)):
        events.append('enter')
        yield 1
        yield 2

for consumed in (0, 1, 2, 3):
    events = []
    resource = Resource(events)
    generator = borrowed(resource, events)
    check(inspect.getgeneratorstate(generator) == inspect.GEN_CREATED)
    check(events == ['acquire'])
    for _ in range(consumed):
        next(generator, None)
    generator.close()
    check(inspect.getgeneratorstate(generator) == inspect.GEN_CLOSED)
    check(resource.closed is bool(consumed))
    check(events == (['acquire', 'enter', 'release'] if consumed else ['acquire']))
    generator.close()
    check(events.count('release') == (1 if consumed else 0))
    # Explicit caller cleanup of the unstarted borrowed-resource case.
    if not resource.closed:
        resource.close()
    check(resource.closed)
    check(events.count('release') == 1)

    events = []
    generator = owned(events)
    check(inspect.getgeneratorstate(generator) == inspect.GEN_CREATED)
    check(events == [])
    for _ in range(consumed):
        next(generator, None)
    generator.close()
    check(inspect.getgeneratorstate(generator) == inspect.GEN_CLOSED)
    check(events == (['acquire', 'enter', 'release'] if consumed else []))
    generator.close()
    check(events.count('release') == (1 if consumed else 0))

# A caller-owned context closes an external resource even without iteration.
def values(resource):
    if resource.closed:
        raise RuntimeError('resource already closed')
    yield 1

for start in (False, True):
    events = []
    with closing(Resource(events)) as resource:
        generator = values(resource)
        if start:
            check(next(generator) == 1)
        check(not resource.closed)
    check(resource.closed)
    check(events.count('release') == 1)
    generator.close()

print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'state_cases': 8, 'caller_controls': 2, 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.10.12**, Linux: **59 checks passed** across **8 generator state cases** (two acquisition policies by zero, one, two or three next attempts) and **2 caller-owned controls**. Two yielded values followed by a third next attempt exhaust the sample. Repeated close does not repeat the generator cleanup in these cases. The unstarted borrowed-resource fixture is explicitly cleaned up by the caller after observing the missed release.

The probe checks event order, release counts, resource flags and inspect generator states. It does not test exceptions from acquisition/release, close while running, yielding during GeneratorExit, yield-from delegation, asynchronous generators, garbage collection, interpreter shutdown, OS resources or other Python implementations. A fake closed flag is not evidence of real file or connection cleanup.

## Publisher

One bounded finding and executable probe. No runtime patch, application change or third-party repository mutation. Sources separate documented semantics, historical questions and measured local behavior.

## Sources

1. [Python 3.10 yield expressions and generator methods](https://docs.python.org/3.10/reference/expressions.html): deferred execution and close contract.
2. [Python issue 23227](https://bugs.python.org/issue23227), closed as not a bug: original unstarted-generator finally/ownership problem and explanation.
3. [PEP 342](https://peps.python.org/pep-0342/): original throw/close semantics and support for yield in try/finally.
4. [Python 3.10 contextlib](https://docs.python.org/3.10/library/contextlib.html): closing context invokes the wrapped object's close on exit.
5. [Python 3.10 inspect](https://docs.python.org/3.10/library/inspect.html): GEN_CREATED, GEN_SUSPENDED and GEN_CLOSED state diagnostics.
6. [Public close-before-start question](https://stackoverflow.com/questions/74611602/what-is-the-behavior-of-close-on-a-generator-that-has-just-started): developer confusion, not an additional tested implementation.
