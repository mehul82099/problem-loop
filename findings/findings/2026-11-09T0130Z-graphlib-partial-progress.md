# A graph sorter becoming inactive does not prove every task finished

Date: 2026-11-09. Evidence-backed Python finding, not a new graphlib defect.

## Research

Python's TopologicalSorter can still release independent nodes after prepare() raises CycleError. The versioned documentation explicitly allows this partial progress. A scheduler that catches the exception and later reports success merely because is_active() is false can confuse exhaustion of available progress with completion of the entire graph.

## Discussion

There are two distinct incomplete states. First, a cyclic region and its downstream dependents can remain unresolved after all independent work is drained. Second, get_ready() can return an empty tuple while previously handed-out work is still outstanding; is_active() then remains true. A parallel scheduler must wait for completion reports, rather than busy-polling get_ready() or treating an empty tuple as global completion.

The graph mapping uses node -> predecessors, not node -> successors. A name used only as a predecessor is automatically added, so completion accounting must include those implicit nodes. A cycle report contains one detected cycle, not an exhaustive explanation of every blocked node. Nodes downstream of a cycle can be blocked without belonging to that cycle.

Calling done(node) is a scheduler acknowledgement. It does not run the task, inspect its result, or distinguish success from failure. Whether a failed task should release dependents is an application policy. Do not mark failed work done in a finally block merely to make the sorter drain if dependents require successful results. The independent scheduling article below illustrates a policy that marks processed results done even when they failed; that is not a universal dependency-success policy.

## Conclusion

| Observation | What it establishes | What it does not establish |
| --- | --- | --- |
| CycleError from prepare | At least one cycle exists | No independent work is available |
| Empty get_ready tuple | No new work is ready now | No previously handed-out work remains |
| is_active is false after draining | No further sorter progress remains | All original nodes ran successfully |
| done(node) accepted | A handed-out node was acknowledged | Its real task succeeded |

For fail-fast use, validate and reject cyclic input before running tasks. For an explicitly allowed partial-progress policy, keep a separate ledger of all nodes, handed-out work, completion and success, and report unresolved nodes rather than inventing a complete order. Partial execution can have side effects; this diagnostic does not authorize or implement it.

Python 3.14 also permits repeated prepare() calls before sorting starts; the tested 3.13 build rejects a second call. That version change does not change the completion distinction. Calling prepare once avoids relying on the newer behavior.

## Action: bounded in-memory diagnostic

Original standard-library-only code under the repository MIT license. No task execution, file access or network operations. The drain function simulates immediate completion, so its assertion that each active iteration returns a nonempty batch is deliberately inappropriate for a real asynchronous scheduler.

```python
# Original in-memory diagnostic, MIT license (repository LICENSE).
from graphlib import TopologicalSorter, CycleError
import json
import platform
import sys

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def raises(kind, operation):
    try:
        operation()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

def drain(graph):
    # Diagnostic only: 'done' here simulates completion, not actual task work.
    ts = TopologicalSorter(graph)
    cycle = None
    try:
        ts.prepare()
    except CycleError as exc:
        cycle = exc.args[1]
    completed = set()
    batches = []
    while ts.is_active():
        ready = ts.get_ready()
        check(bool(ready))  # Safe only in this synchronous simulation.
        for node in ready:
            check(set(graph.get(node, ())) <= completed)
        batches.append(set(ready))
        completed.update(ready)
        ts.done(*ready)
    all_nodes = set(graph).union(*(set(v) for v in graph.values()))
    return ts, completed, all_nodes - completed, cycle, batches

# Independent work progresses, but a downstream node is also blocked.
graph = {'a': {'b'}, 'b': {'a'}, 'downstream': {'a'},
         'root': set(), 'leaf': {'root'}}
ts, completed, blocked, cycle, batches = drain(graph)
check(completed == {'root', 'leaf'})
check(blocked == {'a', 'b', 'downstream'})
check(batches == [{'root'}, {'leaf'}])
check(not ts.is_active())
check(bool(blocked))  # inactive does not mean all nodes completed.
check(cycle[0] == cycle[-1])
check(all(before in graph[after] for before, after in zip(cycle, cycle[1:])))
raises(CycleError, lambda: list(TopologicalSorter(graph).static_order()))
raises(ValueError, lambda: ts.add('new'))

# get_ready hands work out once; it does not run or acknowledge it.
ts = TopologicalSorter({'child': {'parent'}})
ts.prepare()
check(ts.get_ready() == ('parent',))
check(ts.get_ready() == ())
check(ts.is_active())
raises(ValueError, lambda: ts.done('child'))
raises(ValueError, lambda: ts.done('absent'))
ts.done('parent')
check(ts.get_ready() == ('child',))
raises(ValueError, lambda: ts.done('parent'))
ts.done('child')
check(not ts.is_active())

# Control cases include implicit predecessors and a self-cycle.
for graph, expected_done, expected_blocked in [
    ({}, set(), set()),
    ({'child': {'implicit'}}, {'implicit', 'child'}, set()),
    ({'self': {'self'}}, set(), {'self'}),
    ({'a': set(), 'b': {'a'}, 'c': {'a'}, 'd': {'b', 'c'}},
     {'a', 'b', 'c', 'd'}, set()),
]:
    _, completed, blocked, cycle, _ = drain(graph)
    check(completed == expected_done)
    check(blocked == expected_blocked)
    check((cycle is not None) == bool(expected_blocked))

# Repeated prepare is separately versioned; use only one for portable code.
ts = TopologicalSorter({'single': set()})
ts.prepare()
if sys.version_info >= (3, 14):
    check(ts.prepare() is None)
    check(ts.get_ready() == ('single',))
else:
    raises(ValueError, ts.prepare)
    check(ts.get_ready() == ('single',))
raises(ValueError, ts.prepare)  # Work has now been handed out.
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

Executed on CPython 3.13.17 and 3.14.9: 47 checks passed on each build. Checks cover a two-node cycle, a downstream blocked node, an independent chain, a self-cycle, an empty graph, a diamond DAG, an implicit predecessor, outstanding handed-out work, invalid done calls, static_order cycle rejection, and repeated prepare behavior. Tests compare sets within batches, not incidental order among independent nodes. This is a small deterministic probe, not a production scheduler or a performance/concurrency guarantee.

## Sources

1. [Python 3.13 graphlib reference](https://docs.python.org/3.13/library/graphlib.html): partial progress after CycleError, input direction, implicit nodes, and ready/done/active contracts.
2. [Python 3.14 graphlib reference](https://docs.python.org/3.14/library/graphlib.html): same contracts and repeated-prepare version note.
3. [CPython change #131317](https://github.com/python/cpython/pull/131317): merged implementation discussion for repeated prepare calls, not an instruction to modify that repository.
4. [CPython graphlib implementation, main](https://github.com/python/cpython/blob/main/Lib/graphlib.py): corroborates ready/outstanding/completed bookkeeping. Main is moving source, not the tested release identity.
5. [Phil Uvarov, Python graphlib](https://philuvarov.io/python-top-sort/), 2024-07-21: independent scheduling use case and explicit result handling, including its chosen failed-result policy.
6. [Buralog, partial work after a cycle](https://buralog.jp/python-20261019-topological-cycle-partial-work/), page dated 2026-10-21: independent corroborating example on a separately reported 3.11 build. Its reported execution is not counted as our test.

These are documented behaviors, not a newly discovered vulnerability or a claim that a named production scheduler is broken. The increment adds a local reproducible boundary test; it does not claim the idea is new.
