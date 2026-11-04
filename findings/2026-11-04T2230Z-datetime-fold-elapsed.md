# Same-zone datetime subtraction is not always elapsed time across a fold

Date: 2026-11-05. A tested distinction between wall-clock and elapsed-time arithmetic, not a new datetime defect.

## Research

The [datetime reference](https://docs.python.org/3/library/datetime.html) says subtraction ignores timezone attributes when both aware operands have the same tzinfo attribute. Same-zone comparison also ignores fold. [PEP 495](https://peps.python.org/pep-0495/) explains the repeated-time fold and arithmetic rules. An [independent explanation of aware datetime arithmetic](https://blog.ganssle.io/articles/2018/02/aware-datetime-arithmetic.html) discusses the difference between wall-time and elapsed-time semantics.

## Discussion

During a clock rollback, the same local clock reading can refer to two instants. In the historical America/New_York fixture below, 01:30 with fold=0 converts to 05:30 UTC and fold=1 converts to 06:30 UTC. Both objects use the same ZoneInfo instance. Direct subtraction gives zero and same-zone equality is true, while UTC conversion exposes the one-hour interval.

That is a question of which calculation is intended, not evidence that one operator is universally broken. For elapsed duration between already-resolved aware instants, convert both endpoints to UTC before subtracting. Use astimezone(), not replace(tzinfo=UTC), which merely relabels clock fields instead of converting them.

## Conclusion

Keep local recurrence and elapsed-time requirements separate. The helper below computes a signed UTC-based interval and rejects naive inputs. It does not decide which occurrence an ambiguous user input meant, validate nonexistent local times, or implement recurring-event rules. Setting fold is an explicit fixture choice here, not a general disambiguation policy.

## Action: tested historical fold fixture

Ran 14 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64, using available system timezone data. They check both UTC offsets and UTC strings, same-zone subtraction/equality, forward and reverse elapsed intervals, a wider two-wall-hour versus three-elapsed-hour interval, and rejection of each naive endpoint. The example needs the America/New_York timezone data; systems without it must provide timezone data before running it.

```python
import json
import platform
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

def elapsed(start, end):
    if start.utcoffset() is None or end.utcoffset() is None:
        raise ValueError('aware datetimes required')
    return end.astimezone(timezone.utc) - start.astimezone(timezone.utc)

zone = ZoneInfo('America/New_York')
first = datetime(2024, 11, 3, 1, 30, tzinfo=zone, fold=0)
second = datetime(2024, 11, 3, 1, 30, tzinfo=zone, fold=1)
assert first.tzinfo is second.tzinfo
assert first.utcoffset() == timedelta(hours=-4)
assert second.utcoffset() == timedelta(hours=-5)
assert second - first == timedelta(0)
assert second == first
assert first.astimezone(timezone.utc).isoformat() == '2024-11-03T05:30:00+00:00'
assert second.astimezone(timezone.utc).isoformat() == '2024-11-03T06:30:00+00:00'
assert elapsed(first, second) == timedelta(hours=1)
assert elapsed(second, first) == timedelta(hours=-1)
assert elapsed(first, first) == timedelta(0)
start = datetime(2024, 11, 3, 0, 30, tzinfo=zone)
end = datetime(2024, 11, 3, 2, 30, tzinfo=zone)
assert end - start == timedelta(hours=2)
assert elapsed(start, end) == timedelta(hours=3)
for a, b in ((datetime(2024, 1, 1), first), (first, datetime(2024, 1, 1))):
    try:
        elapsed(a, b)
    except ValueError:
        pass
    else:
        raise AssertionError('naive datetime accepted')
print(json.dumps({'python': platform.python_version(), 'cases': 14, 'result': 'passed', 'zone': zone.key}))
```

## Publisher checks and limits

- Original helper and finding use the repository's MIT license. Linked explanations retain their authorship.
- The 2024 dates are historical test fixtures, not a current appointment, future timezone forecast or claim about every rollback.
- The helper accepts datetime-like objects under the standard datetime API; no arbitrary custom tzinfo implementation was tested. It does not parse strings or assign a timezone to naive values.
- UTC-based datetime differences are not a monotonic stopwatch and do not model leap seconds. No live scheduler, persistence, recurrence, extreme-date overflow or performance behavior was tested.
