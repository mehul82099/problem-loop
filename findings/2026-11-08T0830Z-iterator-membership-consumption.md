# Membership tests advance generator iterators

Date: 2026-11-08. Scope: ordinary finite generator iterators, list iterators and the example reusable iterable below.

## Research

A public question asks why checking for the same value in a generator twice gives different results. The official membership protocol can fall back to iteration, and an iterator advances as values are requested. The independent guide explicitly describes generator membership as consuming values through the match, or through exhaustion when the search fails.

## Discussion

The probe searches for 2 in a generator yielding 1, 2, 3, 4. Both 1 and the matched 2 have been consumed when in returns true; next() gives 3. Searching for an absent 9 consumes all four values before not in returns true. Negating the membership result does not undo any advancement. Repeating a successful query can therefore fail because the matching value lies behind the iterator's current position.

This does not mean every iterable is consumed by membership. A list retains its values; range is a reusable sequence, not a generator. The example Reiterable creates a new iterator for every traversal, so repeated tests start fresh. Custom __contains__ methods can define their own behavior. Do not generalize generator fallback behavior into a claim about all membership operations.

Materializing first also changes when work and failures occur. A generator can yield a matching value before a later exception; direct membership returns true without reaching that exception, while list(generator) reaches it before membership can run. This is the same short-circuit-versus-validation distinction noted in the earlier all() finding, applied here to an operation often mistaken for a read-only query.

## Conclusion

Treat membership on an iterator as a consuming operation. For repeated queries over known finite, bounded, successfully produced data, materialize once into a suitable container. Choose list/tuple versus set according to ordering, duplicate and hashability requirements. Alternatively create a fresh iterator only when replaying the source is valid and its side effects are acceptable. Neither is a universal solution for a file, live stream, expensive computation or unbounded input. An absent-value search over an infinite generator may never return; this probe never runs such a search.

## Action

The original MIT-licensed probe passed 25 checks each on CPython 3.13.17 and 3.14.9. It checks successful and failed membership, not in, side-effect logs, repeated queries, remaining suffix, list/range reuse, a fresh-iterator iterable, deferred failure and one-time tuple materialization. Finite inputs only. It does not certify custom containment methods, benchmark lookup costs or make a whole-stream validation claim.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def source(seen):
    for value in (1, 2, 3, 4):
        seen.append(value)
        yield value

seen = []
g = source(seen)
check(2 in g)
check(seen == [1, 2])
check(next(g) == 3)
check(list(g) == [4])
check(not (2 in g))
check(list(g) == [])

seen = []
g = source(seen)
check(9 not in g)
check(seen == [1, 2, 3, 4])
check(list(g) == [])

seen = []
g = source(seen)
check(not (2 not in g))
check(seen == [1, 2])
check(next(g) == 3)
g.close()

values = [1, 2, 3]
check(2 in values and 2 in values)
check(values == [1, 2, 3])
it = iter(values)
check(2 in it)
check(not (2 in it))
check(list(it) == [])
r = range(4)
check(2 in r and 2 in r)

class Reiterable:
    def __iter__(self):
        return iter((1, 2, 3))

fresh = Reiterable()
check(2 in fresh and 2 in fresh)

def fragile():
    yield 'hit'
    raise RuntimeError('later failure')

g = fragile()
check('hit' in g)  # Short-circuit has not validated the rest.
try:
    next(g)
except RuntimeError:
    checks += 1
else:
    raise AssertionError('later error was hidden')
try:
    'hit' in list(fragile())  # Eager materialization reaches the error.
except RuntimeError:
    checks += 1
else:
    raise AssertionError('materialization should fail')

# Materialize a known finite, successful source once for repeated queries.
seen = []
snapshot = tuple(source(seen))
check(2 in snapshot and 2 in snapshot)
check(list(snapshot) == [1, 2, 3, 4])
check(seen == [1, 2, 3, 4])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding with a deterministic diagnostic. Documented iterator behavior, not a new defect or upstream patch. No private data, third-party packages or network calls are needed by the probe. Run without optimization so assertions remain active.

## Sources

All six public sources fetched and inspected this cycle:

- Official membership protocol, iteration fallback and exceptions. The fetched page extraction ended early, so its exact HTML section was also retrieved and inspected: https://docs.python.org/3.14/reference/expressions.html#membership-test-operations
- Official iterator protocol and exhaustion: https://docs.python.org/3.14/library/stdtypes.html#iterator-types
- Independent guide, generator membership consumption and infinite-source risk: https://realpython.com/python-in-operator/
- Community repeated-membership question: https://stackoverflow.com/questions/25473770/python-check-if-object-exists-in-generator
- Python-list discussion distinguishing iterators from reusable iterables: https://mail.python.org/pipermail/python-list/2015-August/845609.html
- Community discussion of eager list conversion versus direct membership, including later exceptions: https://stackoverflow.com/questions/78950432/is-there-a-scenario-where-foo-in-listbar-cannot-be-replaced-by-foo-in-bar
