# A failed list.extend can leave a partial destination

## Research
Public Python discussions show a common expectation: catching an iterator error after list.extend should leave the destination unchanged. On the CPython builds tested here, items yielded before a generator raises remain appended. The caller's exception handler does not roll back the list, and aliases observe the same partial result.

The current Python 3.14 tutorial says extend appends all items and is "Similar to" slice assignment. Older public questions quote "equivalent to" wording. This finding does not claim that older wording is current, or that either operation promises transaction semantics on every Python implementation.

## Discussion
The CPython 3.14 implementation appends iterator values in a loop and returns an error when iteration fails; the error path does not undo previous appends. The probe reproduces failure before any item, after one item and after three items. This is a known failure-mode distinction, not a newly discovered bug.

For a finite source that does not itself mutate the destination or its contents, first collecting the values with list(iterable) defers the explicit destination extension until source iteration succeeds. This costs memory for the collected references. It does not undo source work, deep-copy objects, validate their contents or provide concurrency isolation. A source can itself mutate the destination during staging; the final test demonstrates that limit.

## Conclusion
If a source failure must not expose a partially extended destination, stage a bounded finite source before the explicit destination write. State the assumptions. Do not call this a general transaction or a guarantee against allocation failure during the later write. For unbounded sources or costly side effects, choose an application-level commit protocol rather than relying on list mutation to roll itself back.

## Action: executable probe
Original code under this repository's MIT license. In-memory lists and generators only. Run without Python optimization so assertions remain enabled.

```python
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def failing(values, events):
    for value in values:
        events.append(value)
        yield value
    raise RuntimeError('source failed')

def run(operation):
    try:
        operation()
    except RuntimeError as error:
        return str(error)
    raise AssertionError('expected source failure')

for values in [[], [1], [1, 2, 3]]:
    target = ['existing']
    alias = target
    events = []
    check(run(lambda: target.extend(failing(values, events))) == 'source failed')
    check(target == ['existing'] + values)
    check(alias is target and alias == ['existing'] + values)
    check(events == values)

# Stage the finite iterable before touching the destination.
def staged_extend(target, iterable):
    pending = list(iterable)
    target.extend(pending)

target = ['existing']
events = []
check(run(lambda: staged_extend(target, failing([1, 2], events))) == 'source failed')
check(target == ['existing'])
check(events == [1, 2])  # Source work is not rolled back.
check(staged_extend(target, iter([4, 5])) is None)
check(target == ['existing', 4, 5])

# Staging is shallow, not isolation of yielded object contents.
item = {'value': 1}
destination = []
staged_extend(destination, iter([item]))
check(destination[0] is item)
item['value'] = 2
check(destination == [{'value': 2}])

# A source that mutates the destination defeats a destination-untouched promise.
def interfering(target):
    target.append('source effect')
    yield 1
    raise RuntimeError('source failed')

target = ['existing']
check(run(lambda: staged_extend(target, interfering(target))) == 'source failed')
check(target == ['existing', 'source effect'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 21 checks passed on CPython 3.13.17 and 3.14.9.
- Covers three generator-failure positions, aliases, preserved error message, staging failure/success, retained source effects, shallow references and a deliberately destination-mutating source.
- Only RuntimeError from these finite generators was tested. No slice-assignment behavior, list subclasses, custom length hints, allocation failures, concurrent access, free-threaded build, alternative interpreter, database or file transaction was tested. This is not a thread-safety finding.

## Sources
- [Python 3.14 tutorial, lists](https://docs.python.org/3.14/tutorial/datastructures.html): current extend description and "Similar to" wording.
- [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html): mutable sequence operation contract; no general rollback promise asserted here.
- [CPython list implementation, 3.14 branch](https://github.com/python/cpython/blob/3.14/Objects/listobject.c): iterator extension loop and error path. Moving branch is implementation context, not identity of the tested builds.
- [Python discussion: list extension behavior](https://discuss.python.org/t/inconsistent-undocumented-list-extension-behaviour/67012): public failing-generator example and wording concern; older quoted docs are not current claims.
- [Is list.extend(iterator) guaranteed to be lazy?](https://stackoverflow.com/questions/57194152/is-python-list-extenditerator-guaranteed-to-be-lazy): historical failure/partial mutation examples. No portable slice-assignment atomicity claim adopted.
- [Generator expression referencing its destination](https://stackoverflow.com/questions/73876053/list-extend-with-a-generator-expression-referencing-the-list-itself): source/destination interaction risk; no unbounded reproduction run here.
