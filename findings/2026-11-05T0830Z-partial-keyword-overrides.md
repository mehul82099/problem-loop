# functools.partial keyword values are defaults that callers can override

Date: 2026-11-05. A documented call-binding distinction, not a new Python or Pyright defect.

## Research

The [functools reference](https://docs.python.org/3/library/functools.html) says extra positional arguments are appended and extra keyword arguments extend and override stored keywords. [PEP 309](https://peps.python.org/pep-0309/) records the same rule in its accepted design. A [historical Pyright issue](https://github.com/microsoft/pyright/issues/2777) shows this distinction caused a type-checking mismatch; that issue was closed after a fix announced for Pyright 1.1.203. It is evidence of past confusion, not an open current bug.

## Discussion

The word "freezes" in partial-application explanations does not mean that a stored keyword is protected against call-time replacement. For example, `partial(int, base=2)('10', base=10)` returns 10, not 2. That override affects this invocation; it does not replace the stored base for future calls.

Positionals follow a different rule: they are appended to stored positional arguments. A positional value cannot replace a stored keyword for the same parameter. Binding both ways can instead raise TypeError for multiple values. Whether a particular combination is accepted still depends on the wrapped callable's signature.

## Conclusion

Use partial when caller-overridable defaults match the intended API. If a caller should not select a particular option, expose an explicit wrapper signature that omits it, and supply it inside the wrapper. Do not forward unrestricted caller keywords to that fixed option. This is API shape, not a security boundary or protection against Python code that can change objects or access the underlying function.

## Action: reproducible call-binding probe

Ran 14 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe covers keyword override, unchanged subsequent defaults, positional append, duplicate argument errors and an explicit-signature binary-only wrapper.

```python
import json
import platform
from functools import partial

checks = 0

def equal(got, expected):
    global checks
    assert got == expected, (got, expected)
    checks += 1

def type_error(call):
    global checks
    try:
        call()
    except TypeError:
        checks += 1
    else:
        raise AssertionError('expected TypeError')

binary_default = partial(int, base=2)
equal(binary_default('10'), 2)
equal(binary_default('10', base=10), 10)
equal(binary_default('10'), 2)  # Per-call override did not mutate defaults.
equal(binary_default.keywords, {'base': 2})

def capture(*args, **kwargs):
    return args, kwargs

p = partial(capture, 'prefix', mode='first')
equal(p('tail', mode='second', extra=3),
      (('prefix', 'tail'), {'mode': 'second', 'extra': 3}))
equal(p(), (('prefix',), {'mode': 'first'}))

def pair(a, b):
    return a, b

by_keyword = partial(pair, b=2)
equal(by_keyword(1), (1, 2))
equal(by_keyword(1, b=3), (1, 3))
type_error(lambda: by_keyword(1, 3))  # Positional plus keyword for b.
by_position = partial(pair, 1)
equal(by_position(2), (1, 2))
type_error(lambda: by_position(2, a=3))

# Explicit API for callers that must not select a base. Not a sandbox.
def binary_only(text):
    return int(text, base=2)

equal(binary_only('10'), 2)
type_error(lambda: binary_only('10', base=10))
type_error(lambda: binary_only('10', 10))
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- The wrapper is deliberately specific to `int` conversion. It is not a generic argument-locking library, validator or sandbox.
- Tests cover the named built-in and ordinary function cases only. They do not cover Placeholder, partialmethod, descriptors, custom signatures, subclassing or static-checker versions.
- No current Pyright failure, performance result or production impact is claimed. No application code was changed.
