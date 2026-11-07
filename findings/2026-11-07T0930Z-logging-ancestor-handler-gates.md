# Propagated log records use ancestor handler gates, not ancestor logger gates

## Research
Python logging distinguishes a logger's effective level from the levels on its handlers. The documentation says propagated records go directly to ancestor handlers: ancestor logger levels and filters are not reconsidered. A child with an explicit DEBUG level can therefore send a DEBUG record to a handler attached to an ERROR-level parent if that handler's threshold permits it. A public Python tracker discussion confirms this is intentional behavior.

## Discussion
The probe uses a unique named parent/child pair, with propagation stopped at the parent so the process root is untouched. A child DEBUG event reaches the parent handler even though a direct parent DEBUG call is rejected. A parent logger filter blocks a direct parent call, not the propagated child record. Moving the gate to the handler blocks records delivered to that handler.

NOTSET on a non-root child is different: it delegates effective-level lookup to ancestors before a normal logging call creates a record. The probe then attaches a second capturing handler to the child and shows the same record object delivered to both handlers. Setting child.propagate=False stops the ancestor delivery but leaves the child's own handler active. An origin logger filter blocks both deliveries in the final case.

## Conclusion
Use the origin logger's effective level for record generation policy and each handler's level/filter for that destination's output policy. Avoid redundant handlers in a hierarchy when duplicate output is not intended. Do not treat an ancestor logger's threshold or filter as a blanket restriction on explicitly configured descendants. This is documented behavior, not a new defect. Handler filters here simply accept or reject; replacement-record filters are outside this probe.

## Action: executable probe
Original code under this repository's MIT license. Captures records in memory using unique logger names. No root configuration, files or network output. Run in a fresh Python process without optimization so assertions remain enabled; process-wide logging.disable settings from a host application could change the result.

```python
import json
import logging
import platform
import uuid

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class Capture(logging.Handler):
    def __init__(self):
        super().__init__()
        self.records = []

    def emit(self, record):
        self.records.append(record)

name = 'propagation_probe_' + uuid.uuid4().hex
parent = logging.getLogger(name)
child = logging.getLogger(name + '.child')
outer = Capture()
inner = Capture()
reject = lambda record: False
try:
    parent.propagate = False  # Stop before the process root logger.
    parent.setLevel(logging.ERROR)
    child.setLevel(logging.DEBUG)
    child.propagate = True
    parent.addHandler(outer)
    check(child.parent is parent)
    check(child.getEffectiveLevel() == logging.DEBUG)
    child.debug('child debug')
    check(len(outer.records) == 1)
    check(outer.records[-1].levelno == logging.DEBUG)
    parent.debug('parent debug')
    check(len(outer.records) == 1)

    parent.addFilter(reject)
    child.info('child ignores parent logger filter')
    check(len(outer.records) == 2)
    parent.error('parent filter blocks direct event')
    check(len(outer.records) == 2)
    parent.removeFilter(reject)

    outer.setLevel(logging.ERROR)
    child.warning('handler threshold blocks this')
    check(len(outer.records) == 2)
    child.error('handler accepts this')
    check(len(outer.records) == 3)
    outer.addFilter(reject)
    child.error('handler filter blocks this')
    check(len(outer.records) == 3)
    outer.removeFilter(reject)

    child.setLevel(logging.NOTSET)
    check(child.getEffectiveLevel() == logging.ERROR)
    child.info('inherited threshold blocks creation')
    check(len(outer.records) == 3)
    child.error('inherited threshold accepts')
    check(len(outer.records) == 4)

    child.setLevel(logging.DEBUG)
    outer.setLevel(logging.NOTSET)
    child.addHandler(inner)
    child.warning('two handlers')
    check(len(inner.records) == 1 and len(outer.records) == 5)
    check(inner.records[-1] is outer.records[-1])
    child.propagate = False
    child.warning('local only')
    check(len(inner.records) == 2 and len(outer.records) == 5)
    child.propagate = True
    child.addFilter(reject)
    child.error('origin filter blocks both')
    check(len(inner.records) == 2 and len(outer.records) == 5)
    child.removeFilter(reject)
    check(outer.records[-1].name == child.name)
finally:
    parent.removeFilter(reject)
    child.removeFilter(reject)
    parent.removeHandler(outer)
    child.removeHandler(inner)
    outer.close()
    inner.close()
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 18 checks passed on CPython 3.13.17 and 3.14.9.
- Covers explicit child versus direct parent levels, ancestor logger filter bypass, handler threshold/filter rejection, inherited NOTSET effective level, duplicate handler delivery of one record, propagation stop and origin filter rejection.
- Removes its handlers/filters and closes its handlers in finally. Unique logger objects remain in the logging registry until process exit. No threads, custom levels, replacement filters, queue handlers, dictConfig, basicConfig, root-handler mutation or performance benchmark was tested.

## Sources
- [Python 3.14 logging](https://docs.python.org/3.14/library/logging.html): propagate semantics, effective logger levels, handler levels and duplicate-handler warning.
- [Python 3.14 logging HOWTO](https://docs.python.org/3.14/howto/logging.html): logging flow and handler/logger roles.
- [CPython logging implementation, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/logging/__init__.py): callHandlers context, not exact tested build identity.
- [Why does a basicConfig level have no effect?](https://stackoverflow.com/questions/32471999/why-does-python-logging-level-in-basicconfig-have-no-effect): community explanation of logger versus handler thresholds. This probe does not call basicConfig.
- [Python Logging Notes](https://klauer.github.io/python-logging-notes/): independent call flow explanation; its origin logger gates must not be confused with ancestor gates.
- [Python tracker issue 30862](https://bugs.python.org/issue30862): July-December 2017 discussion of parent-level checking, intentional propagation behavior and documentation clarification.
