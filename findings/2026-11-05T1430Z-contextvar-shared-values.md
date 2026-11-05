# Copying a context separates bindings, not the mutable objects they reference

Date: 2026-11-05. A documented context/value distinction, not a new contextvars defect.

## Research

The [contextvars reference](https://docs.python.org/3/library/contextvars.html) describes Context as a mapping from ContextVars to values and records set operations in the current context. It describes context copies as shallow. [PEP 567](https://peps.python.org/pep-0567/) gives the context-copy and context-local binding model. A [Python Help discussion](https://discuss.python.org/t/diverging-non-trivial-values-in-contextvars/69548) asks how nontrivial dictionary values can diverge across copied contexts. This is a public developer problem about intended semantics, not evidence of a new regression.

## Discussion

If a ContextVar holds a dictionary, copying the context does not recursively copy that dictionary. Mutating the dictionary returned by get changes the object both bindings reference. By contrast, set with a replacement dictionary changes the binding only in the current context. Leaving Context.run restores the outer binding; it does not undo object mutations that happened while inside.

A copy-and-set update can separate the outer dictionary for one context. It is still shallow: nested lists, dictionaries or other mutable objects can remain shared. The probe makes that limitation visible rather than presenting dict(value) as deep isolation.

## Conclusion

Choose a value/update policy separately from context propagation. Prefer immutable values where practical, or set an application-appropriate replacement rather than mutating a shared value in place. If nested values must diverge, define their copy policy too. Context-local bindings are not transactional rollback, deep-copy guarantees or protection against code that can reach a shared object.

## Action: synchronous copied-context probe

Ran 11 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover shared dictionary identity and mutation, a context-local replacement binding, a shallow copy-and-set update, remaining nested sharing and reset of the outer binding. Only local sample state and synchronous Context.run are used.

```python
import json
import platform
from contextvars import ContextVar, copy_context

state = ContextVar('state')
original = {'count': 0, 'nested': []}
token = state.set(original)
checks = 0
try:
    copied = copy_context()
    assert copied[state] is original
    checks += 1
    copied.run(lambda: state.get().__setitem__('count', 1))
    assert state.get()['count'] == 1  # Same dictionary mutated.
    checks += 1
    replacement = {'count': 2, 'nested': []}
    copied.run(state.set, replacement)
    assert copied[state] is replacement
    checks += 1
    assert state.get() is original  # New binding is context-local.
    checks += 1
    assert state.get()['count'] == 1
    checks += 1

    isolated_update = copy_context()
    def replace_count():
        next_value = dict(state.get())
        next_value['count'] = 3
        state.set(next_value)
    isolated_update.run(replace_count)
    assert isolated_update[state]['count'] == 3
    checks += 1
    assert state.get()['count'] == 1
    checks += 1
    assert isolated_update[state] is not original
    checks += 1
    # A shallow replacement still shares nested mutable values.
    assert isolated_update[state]['nested'] is original['nested']
    checks += 1
    isolated_update.run(lambda: state.get()['nested'].append('shared'))
    assert state.get()['nested'] == ['shared']
    checks += 1
finally:
    state.reset(token)
assert state.get(None) is None
checks += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- No asyncio task scheduling, thread propagation, concurrent mutation, framework request lifecycle or deep-copy behavior is tested.
- No mutable default is used, so the shared value in this example comes from the copied binding, not a default-argument pattern.
- No production context was changed. No new runtime defect, security guarantee, performance benchmark or generic isolation library is claimed.
