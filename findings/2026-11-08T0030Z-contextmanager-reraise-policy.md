# A generator context manager can log an error and silently suppress it

## Research
Public Python questions ask how an exception from a with block reaches a generator context manager and whether observing it changes propagation. The current contextlib reference is explicit: the body's exception is raised at the paused yield. If the generator catches it only to log or observe it, the generator must re-raise it unless suppression is intended.

## Discussion
A finally block and an except block answer different questions. Finally arranges cleanup on normal and exceptional exit. Catching the body error and then letting the generator finish normally indicates that the error was handled. The caller resumes after the with statement, not at the next line inside the interrupted body.

That means visible error reporting is not proof of failed control flow. A function that records an error but swallows it can let caller code proceed as if the managed block completed. The probe uses an event list instead of a logging service so the policy is inspectable without output configuration or side effects. It compares a deliberate suppression branch against an observation-plus-bare-raise branch.

This is documented behavior, not a new contextlib defect. It is distinct from the repository's earlier ExitStack failed-entry finding: this probe concerns body-exception handling after entry succeeded.

## Conclusion
Make the exception policy explicit:

| Intent | Generator context-manager shape | Caller outcome |
| --- | --- | --- |
| Cleanup without intercepting failures | yield inside try/finally | Body exception propagates unless cleanup changes it. |
| Observe an expected failure, keep propagation | Catch the named type, record it, then bare raise | The same exception can reach the caller. |
| Deliberately tolerate a narrow failure | Catch only the named type and finish | Caller continues after with; interrupted body does not resume. |

Do not copy the class-based __exit__ return-value convention into generator code. A generator's normal termination after catching the error is the suppression signal; it need not return True. Keep broad catches out of cleanup-only helpers unless their policy really includes every error they catch. Cleanup exceptions, cancellation and exception groups require their own handling, not assumptions from this small synchronous example.

## Action: deterministic control-flow probe
Original code under this repository's MIT license. Six cases combine two policies with normal, matched-error and unmatched-error bodies. The string resource is a marker, not a real acquired service. Run without `-O` so assertions remain enabled.

```python
from contextlib import contextmanager
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

@contextmanager
def observed(events, reraise):
    events.append('enter')
    try:
        yield 'resource'
        events.append('after-yield')
    except ValueError:
        events.append('observed-error')
        if reraise:
            raise
    finally:
        events.append('cleanup')

for reraise in (False, True):
    for kind in ('normal', 'value-error', 'other-error'):
        events = []
        failure = ValueError('expected') if kind == 'value-error' else RuntimeError('other')
        escaped = None
        try:
            with observed(events, reraise) as resource:
                check(resource == 'resource')
                events.append('body')
                if kind != 'normal':
                    raise failure
                events.append('body-end')
            events.append('after-with')
        except (ValueError, RuntimeError) as error:
            escaped = error
            events.append('caller-caught')
        if kind == 'normal':
            expected = ['enter', 'body', 'body-end', 'after-yield', 'cleanup', 'after-with']
            check(escaped is None)
        elif kind == 'value-error' and not reraise:
            expected = ['enter', 'body', 'observed-error', 'cleanup', 'after-with']
            check(escaped is None)
        else:
            expected = ['enter', 'body']
            if kind == 'value-error':
                expected.append('observed-error')
            expected += ['cleanup', 'caller-caught']
            check(escaped is failure)
        check(events == expected)
        check(events.count('cleanup') == 1)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 24 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Each case checks the yielded marker, whether the original exception object escapes, the full event order, and cleanup running exactly once. Normal bodies reach after-yield code; failed bodies do not. Suppressed matched errors reach after-with; re-raised and unmatched errors reach the caller's handler instead.
- No logger, file, database transaction, network resource, exception replacement during cleanup, asynchronous context manager, cancellation, BaseException subclass or exception group was tested. No promise of rollback or universal exception transparency is made.

## Sources
- [Python 3.14 contextlib reference](https://docs.python.org/3.14/library/contextlib.html): exception injection at yield and re-raise requirement for observation-only handlers.
- [PEP 343](https://peps.python.org/pep-0343/): primary with-statement and generator-decorator design. Historical design, not every detail of the current implementation.
- [CPython 3.14 contextlib implementation](https://github.com/python/cpython/blob/3.14/Lib/contextlib.py): generator exit and exception handling; mutable branch.
- [Public body-exception question](https://stackoverflow.com/questions/50715920/python-exception-handling-inside-with-block): confusion about cleanup and throwing into the paused generator.
- [Public log-and-suppress question](https://stackoverflow.com/questions/50233935/ignore-and-log-error-with-contextlib-contextmanager): example of recording an exception and continuing after the context. Its traceback-customization code is not adopted.
- [Independent context-manager guide](https://thinkinginpython.com/15_Techniques--Context_Managers.html): corroborates finally cleanup, suppression and re-raise policy. No type-checking or broad reusable-manager claims from the guide are tested here.
