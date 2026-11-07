# An except target is cleared after its handler, not restored

## Research
Python's language reference says a name bound by except ... as target is cleared at the end of that handler, as if a finally block deleted it. This also applies when the same name already had a value. Public reports show the surprise: initializing error before the try does not guarantee it can be read after a matching except binds that same name.

## Discussion
The probe distinguishes the two paths. If the handler never runs, the prior binding remains. If it runs, the prior value is overwritten and the target is then cleared; reading it as a local raises UnboundLocalError. Reassigning a different value to that target inside the handler does not exempt it from cleanup.

A different variable can retain a message or the exception object. Keeping the object also retains its traceback in this probe, so copying the exception into another binding is not a universal memory-management fix. When a message is all the caller needs, capture the message separately. A closure that looks up the cleared name later fails, while a default argument capturing the message during the handler keeps that string. These are separate value-capture choices, not a new scope created by except.

## Conclusion
Use a distinct handler target and an explicitly initialized result variable for later use. Decide what needs to survive: a short message, structured fields or the full exception/traceback. Do not reuse a result variable as the except target expecting its old value to be restored. The cleanup is documented behavior intended to reduce traceback/frame reference cycles, not a new Python defect or an automatic guarantee that every exception reference has disappeared.

## Action: executable probe
Original code under this repository's MIT license. In-memory controlled exceptions only. Run without Python optimization so assertions remain enabled.

```python
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def overwritten(raise_it):
    error = 'previous binding'
    try:
        if raise_it:
            raise ValueError('bad input')
    except ValueError as error:
        check(isinstance(error, ValueError))
        check(str(error) == 'bad input')
    return error

check(overwritten(False) == 'previous binding')
try:
    overwritten(True)
except UnboundLocalError:
    target_cleared = True
else:
    target_cleared = False
check(target_cleared)

def summary(raise_it):
    message = None
    try:
        if raise_it:
            raise ValueError('bad input')
    except ValueError as caught:
        message = str(caught)
    check('caught' not in locals())
    return message

check(summary(False) is None)
check(summary(True) == 'bad input')

def saved_object():
    saved = None
    try:
        raise ValueError('keep this explicitly')
    except ValueError as caught:
        saved = caught
    check('caught' not in locals())
    check(isinstance(saved, ValueError))
    check(saved.__traceback__ is not None)
    return str(saved)

check(saved_object() == 'keep this explicitly')

def rebound_in_handler():
    try:
        raise ValueError('original')
    except ValueError as caught:
        caught = 'replacement'
        check(caught == 'replacement')
    return 'caught' in locals()

check(rebound_in_handler() is False)

def closure_after_handler():
    try:
        raise ValueError('original')
    except ValueError as caught:
        late = lambda: str(caught)
        captured = lambda value=str(caught): value
        check(late() == 'original')
    check(captured() == 'original')
    try:
        late()
    except NameError:
        missing_cell = True
    else:
        missing_cell = False
    check(missing_cell)

closure_after_handler()
check(issubclass(UnboundLocalError, NameError))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 18 checks passed on CPython 3.13.17 and 3.14.9.
- Covers no-handler prior binding, matched-handler clearing, live target inside handler, separate message binding on both paths, separately retained exception/traceback, reassigned target cleanup, delayed closure lookup and captured message defaults.
- No except*, generators, async handlers, global/nonlocal targets, debugger behavior, memory-size measurement or garbage-collection timing was tested. Full exception objects may carry sensitive or large data; this probe uses only synthetic messages and makes no general sanitization claim.

## Sources
- [Python 3.14 compound statements](https://docs.python.org/3.14/reference/compound_stmts.html): except target cleanup and traceback-cycle rationale.
- [PEP 3110](https://peps.python.org/pep-3110/): primary historical design for exception syntax and target cleanup.
- [CPython issue 84905](https://github.com/python/cpython/issues/84905): May 2020 report about overwriting a parameter, expected behavior and same-scope clarification.
- [Exception deletes a prior variable](https://stackoverflow.com/questions/29268892/python-3-exception-deletes-variable-in-enclosing-scope-for-unknown-reason): public question about initializing a target before the handler.
- [Python 3 language gotcha](https://www.wefearchange.org/2013/04/python-3-language-gotcha-and-short): independent April 18, 2013 explanation and distinct-binding approach; no Python 2 compatibility claim is tested here.
- [Python tracker issue 39841](https://bugs.python.org/issue39841): March 3, 2020 report and language-reference explanation of prior-binding deletion.
