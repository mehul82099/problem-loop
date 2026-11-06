# ExitStack cannot clean an entry that never registered its exit

## Research
A public Python question shows a service manager acquiring two services, failing on the third in `__enter__`, and never calling `__exit__`. Wrapping a manager in ExitStack.enter_context does not make its partial acquisition safe automatically. In the Python 3.14 implementation, entry runs before the exit callback is registered.

## Discussion
This is documented context-management behavior, not a new defect. An outer ExitStack unwinds earlier successful entries, but the manager whose `__enter__` raises must clean its own partial work. Catching the exception outside the with statement does not release an unregistered resource by itself.

The standard library documents an internal ExitStack pattern for cleanup during `__enter__`. Register each successful acquisition before doing validation or another acquisition that might fail. On success, transfer that cleanup responsibility with pop_all; transfer does not run cleanup. The new owner must later be closed. An ordinary callback cannot suppress an exception through its return value, which suits simple release actions.

## Conclusion
Keep two ownership boundaries visible: the outer stack owns successfully entered managers, and each manager owns failures during its own setup. Use normal context managers or try/finally for simpler fixed lifetimes. Do not blindly pre-register an arbitrary manager's `__exit__` with push: that method may require state that entry never initialized.

## Action: executable probe
Original code under this repository's MIT license. The fake resource makes its lifetime observable without opening anything. Its safe branch registers release immediately after acquisition, transfers ownership on success, and closes that owner on normal exit. It is a one-entry demonstration, not a reentrant resource-manager library.

```python
from contextlib import ExitStack
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

class Resource:
    def __init__(self, name, events, fail=False, safe=False):
        self.name, self.events = name, events
        self.fail, self.safe, self.live = fail, safe, False

    def release(self):
        self.events.append('release:' + self.name)
        self.live = False

    def __enter__(self):
        self.events.append('acquire:' + self.name)
        self.live = True
        if not self.safe:
            if self.fail:
                raise ValueError('validation failed')
            return self
        with ExitStack() as pending:
            pending.callback(self.release)
            if self.fail:
                raise ValueError('validation failed')
            self.owner = pending.pop_all()
        return self

    def __exit__(self, *exc):
        self.events.append('exit:' + self.name)
        if self.safe:
            self.owner.close()
        else:
            self.release()

for safe in (False, True):
    events = []
    first = Resource('first', events)
    second = Resource('second', events, fail=True, safe=safe)
    caught = False
    try:
        with ExitStack() as outer:
            check(outer.enter_context(first) is first)
            outer.enter_context(second)
            raise AssertionError('body must not run')
    except ValueError:
        caught = True
    check(caught)
    check(not first.live)
    check(second.live == (not safe))
    check('exit:second' not in events)
    check(events == (['acquire:first', 'acquire:second']
                     + (['release:second'] if safe else [])
                     + ['exit:first', 'release:first']))
    if second.live:
        second.release()  # Repair the deliberately broken fake resource.
    check(not second.live)

events = []
resource = Resource('ok', events, safe=True)
with ExitStack() as outer:
    check(outer.enter_context(resource) is resource)
    check(resource.live)
    check(events == ['acquire:ok'])
check(not resource.live)
check(events == ['acquire:ok', 'exit:ok', 'release:ok'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Compares broken and safe failed entry, earlier successful cleanup, absence of the failed manager's exit, cleanup order, and a successful ownership transfer.
- The deliberately broken fake resource is explicitly repaired by the probe. No real services or handles are leaked.
- No real service startup, files, asynchronous cancellation, nested/reentrant use of one manager, cleanup failures, process crash, or database rollback was tested. Release callbacks can themselves fail; registration is not a guarantee of successful cleanup.

## Sources
- [Python 3.14 contextlib](https://docs.python.org/3.14/library/contextlib.html): enter_context, callback, pop_all and cleanup during `__enter__`.
- [CPython 3.14 implementation](https://github.com/python/cpython/blob/3.14/Lib/contextlib.py): entry precedes exit registration. Branch source can change.
- [Public service-runner question, August 2019](https://stackoverflow.com/questions/57524533/why-exit-is-not-executed-when-enter-raises-exception): partial-acquisition failure report, not evidence that the suggested outer catch fixes cleanup.
- [ExitStack guide, November 2026](https://prepwithproof.com/blog/python-exitstack-dynamic-resources-cleanup-order): failed entry and registration boundaries.
- [Dynamic resource lifetime guide](https://nalar.dev/manage-dynamic-resource-lifetimes-in-python-with-exitstack/): acquire/register ordering and ownership transfer.
- [Historical ExitStack essay, December 2015](https://www.rath.org/on-the-beauty-of-pythons-exitstack.html): cleanup motivation; its old examples are not the current API reference.
