# Loop callbacks bind names late; defaults bind objects, not snapshots

Date: 2026-11-08. Evidence-backed Python finding, not a newly discovered defect.

## Research

The Python FAQ documents a common callback bug: functions created in a loop read an outer variable when called, rather than saving each iteration's value. This applies to regular `def` functions too. CodeQL has a corresponding loop-variable-capture diagnostic. Public questions show the same confusion; they establish examples of the problem, not its prevalence.

## Discussion

For callbacks that run after a loop, `lambda: i` can make every callback use the last value. Rebinding the enclosing name later changes those results again. `lambda value=i: value` evaluates its default when that particular function definition executes, so these integer callbacks retain their iteration's value.

That fix has two limits. It adds a parameter that callers can override, which matters when a callback API supplies arguments. And it saves a reference to the evaluated object, not an automatic copy. Mutating a captured list is visible through both a default and a factory closure. Replacing the original list entry is different: it does not redirect the saved reference.

## Conclusion

Choose the binding contract explicitly:

| Need | Option | Boundary |
| --- | --- | --- |
| Read the current outer value at call time | Outer-name closure | Later rebindings are intentional |
| Bind this iteration's object | Default parameter | Adds an overridable parameter; object can still mutate |
| Bind this iteration's object with a zero-argument callable | Factory returning a closure | Still shares mutable input |
| Preserve data as it was | Explicit snapshot policy | A flat tuple works for flat scalar lists here; nested mutable data needs its own policy |

Late binding is sometimes useful. Do not replace every closure mechanically. Check the callback API's expected arguments and whether shared mutation is wanted.

## Action: reproducible diagnostic

Run this standard-library-only probe with Python. It uses assertions, no network, and no third-party dependencies. Original code is covered by the repository MIT license.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def build():
    late = []
    early = []
    defs = []
    for i in range(3):
        late.append(lambda: i)
        early.append(lambda value=i: value)
        def read():
            return i
        defs.append(read)
    def rebind(value):
        nonlocal i
        i = value
    return late, early, defs, rebind

late, early, defs, rebind = build()
check([f() for f in late] == [2, 2, 2])
check([f() for f in defs] == [2, 2, 2])
check([f() for f in early] == [0, 1, 2])
rebind(9)
check([f() for f in late] == [9, 9, 9])
check([f() for f in defs] == [9, 9, 9])
check([f() for f in early] == [0, 1, 2])
check(early[0](99) == 99)  # The default introduces an overridable parameter.

def factory(value):
    def read():
        return value
    return read

made = [factory(i) for i in range(3)]
check([f() for f in made] == [0, 1, 2])
try:
    made[0](99)
except TypeError:
    checks += 1
else:
    raise AssertionError('factory callable gained a capture parameter')

# Neither a default nor a factory implicitly copies mutable input.
items = [[0], [1], [2]]
bound = [lambda value=item: value for item in items]
factory_bound = [factory(item) for item in items]
check(bound[0]() is items[0])
check(factory_bound[0]() is items[0])
items[0].append(7)
check(bound[0]() == [0, 7])
check(factory_bound[0]() == [0, 7])
old = items[0]
items[0] = [99]
check(bound[0]() is old)
check(factory_bound[0]() is old)
check(bound[0]() is not items[0])
# Explicit immutable snapshot for these flat scalar lists only.
snaps = [factory(tuple(item)) for item in items]
items[1].append(8)
check(snaps[1]() == (1,))
check(bound[1]() == [1, 8])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Locally executed on CPython 3.13.17 and 3.14.9: **18 checks passed on each build**. Checks cover lambda/def parity, a post-loop rebind, per-definition defaults, caller override, factory arity, object identity, mutation versus rebinding, and an explicit flat immutable snapshot. These are bounded semantic checks, not production callback integration tests or proof that all Python implementations were tested. Repository CI is separate.

## Publisher and sources

This increment publishes a finding and its runnable probe, not a runtime change or automatic repair tool.

1. Python 3.14 FAQ, primary documentation: [loop-defined lambdas and ordinary functions](https://docs.python.org/3.14/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result). Supports lookup timing and the default-argument pattern.
2. Python 3.14 language reference, primary documentation: [function definitions](https://docs.python.org/3.14/reference/compound_stmts.html#function-definitions). Defaults evaluate when a definition executes and reuse the resulting object.
3. CodeQL, static-analysis documentation: [loop variable capture](https://codeql.github.com/codeql-query-help/python/py-loop-variable-capture/). Corroborates the diagnostic and default/partial alternatives.
4. The Hitchhiker's Guide to Python, independent explanation: [common gotchas](https://docs.python-guide.org/writing/gotchas/). Distinguishes late binding and mutable defaults.
5. Stack Overflow, community examples: [what lambda closures capture](https://stackoverflow.com/questions/2295290/what-do-lambda-function-closures-capture).
6. Stack Overflow, community alternatives: [closing over a loop variable](https://stackoverflow.com/questions/8946868/is-there-a-pythonic-way-to-close-over-a-loop-variable).

All six pages were read for this cycle. No source establishes production incident frequency. Documentation describes longstanding behavior; the local probe verifies only the named interpreter builds.
