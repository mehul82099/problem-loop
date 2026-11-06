# heapq.merge trusts input order; reverse does not reverse streams

## Research
A public question expected heapq.merge with reverse=True to turn two ascending inputs into descending output. The current documentation requires every input to be sorted in the output direction. merge is a lazy merge of ordered streams, not a general sorting operation or an input-order validator.

## Discussion
An out-of-order input can silently produce out-of-order output. reverse=True changes comparison direction; it does not reverse or sort each input. When key is supplied, each input must be ordered by that same key and direction. Lexicographic tuple ordering may not match a selected field's ordering.

This is documented behavior, not a new defect. A 2017 documentation issue and its merged clarification already explain the reverse precondition. The probe below checks current behavior independently, including a single unsorted stream and an unsorted value reached only after a valid-looking prefix. It does not rely on old implementation details or make stability claims for equal keys.

## Conclusion
Use merge when upstream order is an established contract. For finite unordered inputs, sort the combined data, or sort each input with matching key/reverse before merging. Both choices materialize data and lose the benefit of already ordered streaming inputs. For unbounded inputs, define and enforce the upstream ordering contract; do not mistake a correct output prefix for validation of the whole stream.

## Action: executable probe
Original code under this repository's MIT license. In-memory values only. Run without Python optimization so assertions remain enabled.

```python
from heapq import merge
from itertools import chain
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(list(merge()) == [])
check(list(merge([], [])) == [])
check(list(merge([1, 3], [2, 4])) == [1, 2, 3, 4])
check(list(merge([3, 1], [2])) == [2, 3, 1])  # No order error.
check(list(merge([1, 3], [2, 4], reverse=True)) == [2, 4, 1, 3])
check(list(merge([3, 1], [4, 2], reverse=True)) == [4, 3, 2, 1])
check(list(merge([4, 1])) == [4, 1])  # Even one stream must be sorted.
check(list(merge([1, 1], [1, 2])) == [1, 1, 1, 2])

left = [('a', 1), ('b', 4)]
right = [('c', 2), ('d', 3)]
by_score = lambda row: row[1]
check([x[1] for x in merge(left, right, key=by_score)] == [1, 2, 3, 4])
# Lexicographic order is not order by score.
wrong = sorted([('a', 4), ('b', 1)])
check([x[1] for x in merge(wrong, [('c', 2)], key=by_score)] == [2, 4, 1])
check([x[1] for x in merge(sorted(wrong, key=by_score), [('c', 2)],
                          key=by_score)] == [1, 2, 4])
check([x[1] for x in merge(sorted(left, key=by_score, reverse=True),
                          sorted(right, key=by_score, reverse=True),
                          key=by_score, reverse=True)] == [4, 3, 2, 1])

seen = []
def source():
    for value in [1, 3, 0]:
        seen.append(value)
        yield value

result = merge(source(), [2, 4])
check(seen == [])
check(next(result) == 1)
check(seen == [1])
check(list(result) == [2, 3, 0, 4])
check(seen == [1, 3, 0])
# For finite unordered data, a full sort is the separate operation.
check(sorted(chain([3, 1], [2])) == [1, 2, 3])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 18 checks passed on CPython 3.13.17 and 3.14.9.
- Covers empty inputs, sorted ascending/descending input, unsorted input, reverse mismatch, single stream, duplicate values, selected-field key order, matching key/direction, lazy consumption and a finite full-sort alternative.
- Exact invalid-input outputs illustrate these builds; no sensible sorted-output guarantee is claimed when the precondition is violated.
- No timings, memory benchmarks, infinite-stream completion, NaNs, mixed incomparable values, unstable key functions, async input, files or production log pipelines were tested. The demonstration key returns comparable integers and is deterministic. No order-checking wrapper or transactional rollback is provided.

## Sources
- [Python 3.14 heapq documentation](https://docs.python.org/3.14/library/heapq.html): sorted-input, key and reverse contract.
- [CPython heapq implementation, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/heapq.py): implementation reference, not a pinned build identity or new defect claim.
- [Real Python heapq guide](https://realpython.com/python-heapq-module/): independent explanation of merging ordered streams; published June 24, 2020.
- [CPython documentation issue 73908](https://github.com/python/cpython/issues/73908): historical reverse-direction confusion, not a current open bug.
- [CPython PR 300](https://github.com/python/cpython/pull/300): corresponding documentation clarification.
- [How to use heapq.merge?](https://stackoverflow.com/questions/64349081/how-to-use-heapq-merge): concrete expectation mismatch with ascending input and reverse=True; October 14, 2020.
