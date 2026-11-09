# A seed does not isolate a shared random generator

Date: 2026-11-09. Evidence-backed Python finding, not a new random-module defect.

## Research

Python documents that module-level random functions are bound methods of one shared Random instance. Calling random.seed resets that shared stream, while unrelated module-level draws advance it. A fixed seed therefore does not isolate a simulation from other code using the same generator. Separate Random instances have separate state.

## Discussion

The probe seeds the module stream, records a baseline, then repeats with one extra draw inserted after the first observation. The following observations shift. A different caller reseeding the module also changes the baseline. Neither behavior is randomness "ignoring" a seed; it is a different state history.

| Pattern | State ownership | Replay boundary |
| --- | --- | --- |
| random.seed followed by module functions | Shared instance | Other users of module functions can consume or reset it |
| Random(seed) passed to one simulation | Explicit instance | Code with access to that same instance can still advance it |
| Two Random instances from the same seed | Separate state | Equivalent call schedules can be compared within the tested runtime |
| getstate then setstate | Checkpoint of current state | Resume from that checkpoint, rather than restart at the seed |

Restarting with the seed is different from restoring a checkpoint taken after earlier draws. Assigning alias = rng is also not a new generator; the alias can advance the original instance. The probe demonstrates both distinctions. It interleaves calls to a separate noise generator and confirms they do not alter the local simulation stream.

## Conclusion

For repeatable non-security simulations, inject an explicitly owned Random instance instead of reseeding module state inside a library helper. Retain the seed, runtime version and call schedule needed for a meaningful replay. Use getstate/setstate for an in-memory checkpoint when that is the intended operation. The diagnostic restores its temporarily changed module state in finally, but that is only safe as an isolated process demonstration, not a pattern for concurrent production code where restoration could overwrite someone else's progress.

State isolation is not a blanket reproducibility guarantee. Python warns that most random-module algorithms and seeding functions may change across versions; its narrower compatibility promise concerns random() with a compatible seeder and the same seed. No guarantee about every higher-level API follows from passing version=2. Thread safety also does not fix which caller receives which draw under different scheduling. These tests are single-threaded and compare equivalent schedules separately on each named build, not all future versions or statistical independence of streams.

The default generator is not appropriate for passwords, tokens or other security purposes. Use the documented secrets facilities for those uses, not this reproducible simulation pattern. No security values are generated or stored here, and no state is serialized or read from untrusted input.

## Action: bounded state-isolation diagnostic

Original standard-library-only code under the repository MIT license. In-memory state only, no files or network. Seeds are public toy integers. Run without -O so assertions remain enabled.

```python
# Original in-memory simulation probe, MIT license (repository LICENSE).
import random
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def draws(rng, count=8):
    return [rng.random() for _ in range(count)]

# Keep module state restoration bounded to this isolated diagnostic process.
before = random.getstate()
try:
    random.seed(314159)
    baseline = draws(random)
    random.seed(314159)
    first = random.random()
    unrelated = random.random()  # Another module-level caller advances it.
    rest = draws(random, 7)
    check(first == baseline[0])
    check(unrelated == baseline[1])
    check(rest[:6] == baseline[2:])
    check([first] + rest != baseline)  # Concrete interference, not probability proof.

    random.seed(314159)
    check(draws(random) == baseline)
    random.seed(314159)
    random.seed(271828)  # Another caller can reset it too.
    check(draws(random) != baseline)
finally:
    random.setstate(before)
check(random.getstate() == before)

# Local generators isolate state even when calls to another are interleaved.
for seed in range(25):
    left, reference, noise = random.Random(seed), random.Random(seed), random.Random(999)
    observed = []
    for _ in range(12):
        observed.append(left.random())
        noise.random()
        noise.randrange(100)
    check(observed == draws(reference, 12))
    checkpoint = left.getstate()
    future = draws(left, 12)
    left.setstate(checkpoint)
    check(draws(left, 12) == future)
    clone = random.Random(0)
    clone.setstate(checkpoint)
    check(draws(clone, 12) == future)
    left.seed(seed)
    check(draws(left, 12) == observed)

# Aliasing is not isolation; passing the same object transfers access to it.
rng = random.Random(42)
alias = rng
checkpoint = rng.getstate()
alias.random()
check(rng.getstate() != checkpoint)
check(alias is rng)
# One extra draw shifts this actual call schedule.
rng.setstate(checkpoint)
expected = draws(rng)
rng.setstate(checkpoint)
rng.random()
check(draws(rng, 7) == expected[1:])
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

110 checks passed separately on CPython 3.13.17 and 3.14.9: seven module-interference/restoration checks, four replay/isolation checks for each of 25 seeds, and three alias/call-shift checks. Assertions about unequal sequences concern the exact seeded example, not a proof that different schedules or seeds can never collide. No benchmark, randomness-quality test, multi-thread test or cross-version state-file guarantee is claimed.

## Sources

1. [Python 3.13 random reference](https://docs.python.org/3.13/library/random.html): shared module instance, independent instances, bookkeeping, security warning and limited compatibility guarantees.
2. [Python 3.14 random reference](https://docs.python.org/3.14/library/random.html): corroborating versioned contracts.
3. [CPython random implementation, main](https://github.com/python/cpython/blob/main/Lib/random.py): module methods bound to one instance and state methods. Moving source is corroboration, not the identity of the tested builds.
4. [Python reproducibility discussion](https://discuss.python.org/t/preserve-randomization-from-3-13-to-3-14/104059/1), 2025-09-30: real test-output concern and shared-state explanation. Its tentative diagnosis and stability anecdotes are not treated as a confirmed RNG defect or a guarantee.
5. [Public checkpoint question](https://stackoverflow.com/questions/58894758/how-to-stash-random-state-generator-state), 2019-11-16: user need to resume rather than restart a sequence; the answer's initial overstatement is corrected in the same answer, and official docs govern our claims.
6. [Real Python random-data guide](https://realpython.com/python-random/): independent explanation of deterministic seeded sequences and distinction from security randomness.

The contribution is an original replay/isolation probe and explicit state-ownership guidance, not a newly discovered algorithm or a claim that a named test suite has a confirmed bug.
