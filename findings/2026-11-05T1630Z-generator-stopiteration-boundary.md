# An unguarded next inside a generator is not a normal exhaustion boundary

Date: 2026-11-05. A documented generator exception distinction, not a new Python defect.

## Research

[PEP 479](https://peps.python.org/pep-0479/) explains why StopIteration escaping a generator frame becomes RuntimeError rather than silently ending the generator. The [exceptions reference](https://docs.python.org/3/library/exceptions.html) documents the conversion and original exception as the cause, with the rule enabled by default since Python 3.7. [Real Python's StopIteration reference](https://realpython.com/ref/builtin-exceptions/stopiteration/) contrasts custom iterator exhaustion with generator return. These establish longstanding semantics, not a recent regression.

## Discussion

A loop that repeatedly does `yield next(iterator)` forwards values but eventually lets the source's exhaustion escape its own generator frame. It can yield a valid prefix and then raise RuntimeError even when the source ended normally. Catching StopIteration outside that generator does not turn the escaping exception back into a normal end of iteration.

For simple forwarding, yield from handles the source's normal exhaustion. When extra processing requires an explicit next loop, catch the expected StopIteration narrowly around that next call and return. Do not broadly suppress RuntimeError: that can hide unrelated failures. The probe also checks that an ordinary ValueError from the source remains visible.

## Conclusion

Use return to end a generator body normally, not an explicit raise StopIteration. Use yield from for simple delegation, or put the intended exhaustion boundary directly around the source advance. These examples are equivalent only for the tested ordinary value iteration; they do not claim identical send, throw, close or return-value delegation semantics.

## Action: forwarding and failure probe

Ran 16 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Empty, one-item and two-item sources cover the broken pattern and two normal forwarding patterns. Two source-failure checks confirm that ValueError is not swallowed. No file, network or production iterator is used.

```python
import json
import platform

checks = 0

def broken_forward(items):
    iterator = iter(items)
    while True:
        yield next(iterator)

def forward(items):
    yield from items

def explicit_forward(items):
    iterator = iter(items)
    while True:
        try:
            value = next(iterator)
        except StopIteration:
            return
        yield value

for values in [[], [1], [1, 2]]:
    observed = []
    try:
        for value in broken_forward(values):
            observed.append(value)
    except RuntimeError as exc:
        assert isinstance(exc.__cause__, StopIteration)
        checks += 1
    else:
        raise AssertionError('expected escaping exhaustion error')
    assert observed == values
    checks += 1
    assert list(forward(values)) == values
    checks += 1
    assert list(explicit_forward(values)) == values
    checks += 1

def failing_source():
    yield 1
    raise ValueError('source failure')

for wrapper in [forward, explicit_forward]:
    iterator = wrapper(failing_source())
    assert next(iterator) == 1
    checks += 1
    try:
        next(iterator)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('unexpected source error was hidden')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- Only synchronous generators and ordinary iteration are tested. Async generators, coroutines, custom iterator classes and full delegation protocols are outside scope.
- The valid prefix already yielded before a failure is not rolled back. Buffering, application effects and retry policy remain separate decisions.
- No new runtime bug, generic exception wrapper, production change or performance benchmark is claimed.
