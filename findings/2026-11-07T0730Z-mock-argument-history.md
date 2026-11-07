# Mock call history retains argument references, not value snapshots

## Research
Python's unittest.mock examples explicitly say that call_args and call_args_list store references to arguments. Mutating a list or dictionary after a call changes what a later assertion sees through those references. Public issue reports describe multiple recorded calls apparently acquiring the last state of one reused object. That is documented behavior, not evidence that the calls were replayed or that the test runner lost history.

## Discussion
The probe calls one Mock twice with the same nested dictionary and proves that both call records reference that dictionary. The first saved call object sees the appended item too. Rebinding the caller's variable to a new list is different: the call still refers to the old list.

For value-at-call-time tests, a side_effect can inspect immediately or capture an explicit copy. The example observer below deep-copies the pair (args, kwargs) in one operation so aliases shared between positional and keyword arguments survive within that snapshot. Each call gets a separate snapshot. The original Mock history still holds the original objects; the observer does not change that behavior. Returning DEFAULT allows the configured return_value to be used.

## Conclusion
Decide whether the test needs object identity, current object contents or a historical value snapshot. Use normal call history for the first two. For historical values, check them at call time or record only the fields needed by the assertion. Deep-copying every argument is not a universal fix: arbitrary objects may reject copying, copying can run custom code, and identity-based expectations change. This small observer is scoped to the built-in containers shown and is not a replacement for an existing side_effect.

## Action: executable probe
Original code under this repository's MIT license. In-memory mocks and built-in containers only. Run without Python optimization so assertions remain enabled.

```python
from copy import deepcopy
from unittest.mock import DEFAULT, Mock
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

payload = {'items': [1]}
m = Mock(return_value=None)
m(payload, meta=payload)
first = m.call_args
check(first.args[0] is payload)
check(first.kwargs['meta'] is payload)
payload['items'].append(2)
m(payload, meta=payload)
check(m.call_count == 2)
check(m.call_args_list[0].args[0] is m.call_args_list[1].args[0])
check(first.args[0] == {'items': [1, 2]})
check(first.args[0] is first.kwargs['meta'])
try:
    m.assert_called_with({'items': [1]}, meta={'items': [1]})
except AssertionError:
    old_value_failed = True
else:
    old_value_failed = False
check(old_value_failed)
m.assert_called_with({'items': [1, 2]}, meta={'items': [1, 2]})
check(m.call_args.args[0] == {'items': [1, 2]})

# A deliberately scoped observer for copyable built-in containers.
# One deepcopy of the pair preserves aliases across args and kwargs.
snapshots = []
def capture(*args, **kwargs):
    snapshots.append(deepcopy((args, kwargs)))
    return DEFAULT

observed = Mock(side_effect=capture, return_value='ok')
source = {'items': [3]}
check(observed(source, meta=source) == 'ok')
source['items'].append(4)
check(observed(source, meta=source) == 'ok')
source['items'].clear()
check(snapshots[0][0][0] == {'items': [3]})
check(snapshots[1][0][0] == {'items': [3, 4]})
check(snapshots[0][0][0] is snapshots[0][1]['meta'])
check(snapshots[0][0][0] is not source)
check(snapshots[0][0][0] is not snapshots[1][0][0])
check(observed.call_args_list[0].args[0] == {'items': []})
check(observed.call_args_list[1].args[0] is source)
check(observed.call_count == len(snapshots) == 2)

# Clearing the caller's variable binding is not mutation of its old list.
old = [7]
rebound = Mock(return_value=None)
rebound(old)
old = [8]
check(rebound.call_args.args[0] == [7])
check(rebound.call_args.args[0] is not old)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9. The successful assert_called_with call also executed on both builds.
- Covers positional/keyword references, nested mutation, reused-object history, failed old-value assertion, successful current-value assertion, explicit snapshots, aliases across arguments, independence between snapshots, return_value preservation and variable rebinding.
- No patch targets, AsyncMock, threads, custom copy protocols, sockets, file handles, exception-raising side effects, spec/autospec behavior, production test suite or performance measurement was tested. A snapshot is only as faithful as the selected copying or field-extraction policy.

## Sources
- [Python 3.14 mock examples](https://docs.python.org/3.14/library/unittest.mock-examples.html): mutable-argument reference semantics, identity tradeoff and call-time checking/copying options.
- [Python 3.14 unittest.mock](https://docs.python.org/3.14/library/unittest.mock.html): call_args, call_args_list, side_effect and DEFAULT/return_value behavior.
- [CPython issue 76813](https://github.com/python/cpython/issues/76813): historical mutable-argument report, closed as not a bug; discussion of copying cost, identity and unsupported objects.
- [Call arguments at their original state](https://stackoverflow.com/questions/40248075/how-do-we-ensure-that-the-calls-in-the-mock-call-args-list-contain-calls-with-ar): public test-author question. No third-party package was installed or endorsed.
- [Python tracker issue 45305](https://bugs.python.org/issue45305): September/October 2021 report and explanation distinguishing mutation from expected historical state; closed as not a bug.
- [Dealing with mutable arguments in Unit Tests](https://saisankargochhayat.medium.com/dealing-with-mutable-arguments-in-unit-tests-b0a847160b): independent March 16, 2023 explanation of the test confusion. Its copying recommendation is limited here by identity and copyability caveats.
