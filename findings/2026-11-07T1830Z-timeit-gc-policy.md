# timeit chooses a garbage-collection policy before your setup runs

## Research
A public Python question reports different relative performance from `timeit` and a direct timer. The current timeit reference explains an important possible cause: it temporarily disables automatic garbage collection by default. The gc reference makes the scope precise: this collector supplements CPython reference counting. Disabling it is not disabling every form of memory reclamation.

## Discussion
A benchmark measures a workload under a policy. Removing collector work can improve repeatability while excluding a cost the real workload pays. The independent guide below calls disabling GC a best practice; the official timeit note explicitly gives both the comparability benefit and the representativeness cost. Neither policy is automatically right for every benchmark.

Do not infer a speedup for your code from another person's ratios. Their public example motivates checking the harness, not transferring their performance result. This probe records enabled states only. It does not measure collection frequency, elapsed-time differences, memory use or throughput.

## Conclusion
Name the collector policy beside benchmark results:

| Question | Policy to consider | Boundary |
| --- | --- | --- |
| Cost of a small operation excluding automatic cyclic collection | Default timeit | Excluded costs must be stated. |
| Cost with automatic collection enabled | Enable it in setup, as the official docs describe | Enabled does not guarantee a collection occurs during a short run. |
| End-to-end latency or allocation lifecycle | A representative larger workload and explicit lifetime boundaries | A microbenchmark alone cannot establish application performance. |

The tested implementation disables collection before setup, then re-enables it in finally only if it was initially enabled. That is not a general state-rollback guarantee for code that changes GC itself. In particular, when the collector starts disabled and setup enables it, it remains enabled after this run, including when the statement raises. A harness that owns the policy should restore its own original setting in finally. Avoid concurrent GC-policy changes in the same interpreter.

## Action: state probe, not a speed benchmark
Original code under this repository's MIT license. Eight cases cover initially enabled/disabled, setup opt-in/default, and normal/exceptional statement paths. Run without `-O` so assertions remain active. Setup uses a callable; the official documentation also shows a setup string.

```python
import gc
import json
import platform
import timeit

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

original = gc.isenabled()
try:
    for initial in (True, False):
        for opt_in in (False, True):
            for fail in (False, True):
                (gc.enable if initial else gc.disable)()
                observations = []
                def setup():
                    observations.append(('setup-before', gc.isenabled()))
                    if opt_in:
                        gc.enable()
                    observations.append(('setup-after', gc.isenabled()))
                def statement():
                    observations.append(('statement', gc.isenabled()))
                    if fail:
                        raise ValueError('expected')
                caught = False
                try:
                    timeit.Timer(statement, setup).timeit(number=3)
                except ValueError:
                    caught = True
                check(caught == fail)
                check(observations[:2] == [
                    ('setup-before', False), ('setup-after', opt_in)])
                check(observations[2:] == [('statement', opt_in)] * (1 if fail else 3))
                # An initially disabled collector enabled by setup stays enabled.
                check(gc.isenabled() == (initial or opt_in))
finally:
    (gc.enable if original else gc.disable)()
check(gc.isenabled() == original)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 33 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout. The published probe intentionally discards timeit's timing return value.
- Each case verifies setup enters with collection disabled, the statement sees the selected policy, normal runs execute it three times, exceptions stop after the first call, and the observed final state follows the tested implementation. The outer finally restores the process's initial enabled flag.
- No cycles, forced collections, callbacks, thresholds, allocation benchmark, alternate interpreter, free-threaded build, multi-threaded policy changes or production workload were tested. Enabling automatic collection does not promise an immediate sweep. No recommendation to disable collection in production is made.
- The source branch can change. Historical community snippets that omit finally do not describe the tested current exceptional path.

## Sources
- [Python 3.14 timeit reference](https://docs.python.org/3.14/library/timeit.html): default collection policy, setup exclusion and opt-in guidance.
- [Python 3.14 gc reference](https://docs.python.org/3.14/library/gc.html): enable/disable/isenabled and the collector's relationship to reference counting.
- [CPython 3.14 timeit implementation](https://github.com/python/cpython/blob/3.14/Lib/timeit.py): state capture, disabling before inner/setup, and conditional re-enable in finally; mutable branch.
- [Public policy question](https://stackoverflow.com/questions/4523817/what-does-timeit-gain-by-turning-off-garbage-collection): historical rationale and old exceptional-path discussion. Old code is not used as current implementation evidence.
- [Public conflicting-timings question](https://stackoverflow.com/questions/63757763/timeit-and-its-default-timer-completely-disagree): user-reported benchmark discrepancy and collector explanation. Its timings and object counts were not reproduced here.
- [Independent benchmarking guide](https://superfastpython.com/python-benchmarking-best-practices/): recommends disabling collection for consistency. This finding limits that recommendation using the official representativeness caveat rather than treating it as universal.
