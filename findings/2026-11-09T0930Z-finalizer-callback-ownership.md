# A weak finalizer can still strongly retain its owner

Date: 2026-11-09. Evidence-backed Python lifetime finding, not a new interpreter defect.

## Research

The versioned weakref references explicitly warn that the callback, positional arguments and keyword arguments must not own a reference to the target, directly or indirectly. A bound method such as `obj.close` refers to its instance. Registering `weakref.finalize(obj, obj.close)` therefore defeats collection-triggered cleanup of that instance while the registration remains live.

A February 2019 public question demonstrates the same trap through a callback argument rather than a bound method. CPython issue 87111 clarifies why passing independent data extracted from an attribute can be different: the value need not refer back to the instance. The closed Redis VL issue 656 reports a bound-method registration problem in a real library; its thread says a fix shipped in 0.25.0. That is historical motivation only. This probe does not install Redis VL, reproduce its reported memory growth, verify its release contents or claim the library remains affected.

## Discussion

The relevant question is the reference path, not whether a callable looks like a method, function or lambda. Moving `obj.close()` into a lambda with an owner captured as a default argument still retains the owner. So does passing the owner to a free function as an argument or keyword. Conversely, an independent state dictionary can outlive the owner without keeping it alive, provided it has no reference path back to the owner.

| Registration or action | Result in the bounded probe |
| --- | --- |
| Bound method, owner argument, owner keyword, captured owner | Owner survives deletion and explicit collection; callback has not run |
| Explicit call of that live finalizer | Callback runs once; registration releases its owner reference |
| Free function plus independent state | Owner is collected and callback updates the surviving state |
| detach on bound-method registration | Callback does not run; returned tuple retains owner until tuple is discarded |

The finalizer's `atexit` flag is false in every fixture to avoid conflating collection with shutdown. The documentation describes shutdown behavior separately. This finding makes no shutdown-order, crash-cleanup or prompt resource-release guarantee.

## Conclusion

If finalization is used, pass only the independent state needed for cleanup, with no direct or indirect path back to the target. Inspect both callback captures and arguments. A wrapper alone does not remove ownership. Keep explicit resource lifetime management separate from this memory-only demonstration; these fixtures are not a connection or file cleanup framework.

This differs from the repository's method-cache lifetime finding: the retaining registration here is a finalizer, and its explicit call/detach contracts determine release. No cache keys or cache invalidation are involved.

## Action

Original code under this repository's MIT license. Run without Python optimization so assertions remain enabled. The callback only appends labels and changes a dictionary. No files, network connections or external resources are opened.

```python
import gc
import json
import platform
import weakref

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class Owner:
    def __init__(self, label, events):
        self.label = label
        self.events = events

    def close(self):
        self.events.append(self.label)

def close_owner(owner):
    owner.close()

def release_state(state, events):
    events.append(state['label'])
    state['closed'] = True

for iteration in range(25):
    # Each callback registration below retains its owner by a different path.
    for kind in ('bound', 'argument', 'keyword', 'closure'):
        events = []
        obj = Owner(kind, events)
        ref = weakref.ref(obj)
        if kind == 'bound':
            fin = weakref.finalize(obj, obj.close)
        elif kind == 'argument':
            fin = weakref.finalize(obj, close_owner, obj)
        elif kind == 'keyword':
            fin = weakref.finalize(obj, close_owner, owner=obj)
        else:
            fin = weakref.finalize(obj, lambda owner=obj: owner.close())
        fin.atexit = False
        del obj
        gc.collect()
        check(ref() is not None)
        check(fin.alive)
        check(events == [])
        # Explicit invocation releases this registration, and invokes once.
        check(fin() is None)
        gc.collect()
        check(ref() is None)
        check(not fin.alive)
        check(events == [kind])
        check(fin() is None)
        check(events == [kind])

    # Passing an attribute value is different if it has no path to the owner.
    events = []
    obj = Owner('independent state', events)
    obj.state = {'label': 'independent state', 'closed': False}
    state = obj.state
    ref = weakref.ref(obj)
    fin = weakref.finalize(obj, release_state, obj.state, events)
    fin.atexit = False
    del obj
    gc.collect()
    check(ref() is None)
    check(not fin.alive)
    check(state['closed'])
    check(events == ['independent state'])
    check(fin() is None)
    check(events == ['independent state'])

    # detach does not invoke the callback, but its returned tuple is strong.
    events = []
    obj = Owner('detached', events)
    ref = weakref.ref(obj)
    fin = weakref.finalize(obj, obj.close)
    fin.atexit = False
    del obj
    detached = fin.detach()
    gc.collect()
    check(ref() is not None)
    check(detached[0] is ref())
    check(not fin.alive)
    check(events == [])
    del detached
    gc.collect()
    check(ref() is None)
    check(events == [])
    check(fin.detach() is None)

print(json.dumps({'checks': checks, 'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **1,225 checks passed per build**. Each of 25 repetitions checks four retaining paths, independent attribute state, explicit at-most-once invocation and detach tuple lifetime. Repetition checks consistency of these small fixtures, not a stress benchmark. The probe explicitly invokes or detaches every retaining registration, so it leaves none of its intentionally retained owners registered for shutdown.

No byte-size or RSS measurements, cyclic owner graphs, callback exceptions, resurrection, asynchronous cleanup, threads, interpreter shutdown or other Python implementation was tested. Collection timing in these CPython runs is not a cross-interpreter timing guarantee. Real state can contain hidden back-references even when the outer holder looks independent.

## Publisher

One bounded finding with a standalone probe. Sources distinguish documented behavior, historical reports and locally verified observations. No third-party repository was changed.

## Sources

1. [Python 3.13 weakref reference](https://docs.python.org/3.13/library/weakref.html), primary documentation: finalize ownership warning, call/detach and atexit contracts.
2. [Python 3.14 weakref reference](https://docs.python.org/3.14/library/weakref.html), primary documentation: same ownership warning and independent-state example.
3. [PEP 205](https://peps.python.org/pep-0205/), standards-track historical background: weak references allow lookup without themselves keeping an object alive. Predates finalize; not a finalize specification.
4. [python: what stops garbage collection](https://stackoverflow.com/questions/54756743/python-what-stops-garbage-collection), February 18, 2019 community question and answer: passing the owner as a callback argument keeps it alive.
5. [CPython issue 87111](https://github.com/python/cpython/issues/87111), documentation discussion: independent attribute values differ from bound methods; the reference path back to the instance matters.
6. [Redis VL issue 656](https://github.com/redis/redis-vl-python/issues/656), historical library report, closed: bound-method retention reported July 31, 2026; August 6 thread comment reports a fix in 0.25.0. No current vulnerability or unverified memory-impact claim is adopted here.
