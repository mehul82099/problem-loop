# timedelta.seconds is a normalized component, not the total duration

Date: 2026-11-06. A documented duration boundary, not a new datetime defect.

## Research

The [Python 3.14 datetime reference](https://docs.python.org/3.14/library/datetime.html) explicitly warns about confusing seconds with total_seconds. Timedelta stores normalized days, seconds and microseconds; seconds is between zero and 86399 even for negative durations. The same reference warns that total_seconds loses microsecond accuracy for very large intervals, greater than about 270 years on most platforms.

A [community comparison](https://stackoverflow.com/questions/51652952/python-timedelta-seconds-vs-total-seconds), a [negative-days question](https://stackoverflow.com/questions/42361050/datetime-datetime-today-datetime-datetime-today-days-giving-1), and a [negative-duration question](https://stackoverflow.com/questions/8408397/python-timedelta-issue-with-negative-values) show recurring confusion. An [independent library's pitfalls guide](https://whenever.readthedocs.io/en/stable/stdlib-pitfalls/timedelta-seconds.html) illustrates the same distinction; no third-party replacement is evaluated or endorsed. The [numeric types reference](https://docs.python.org/3.14/library/stdtypes.html) supplies integer arithmetic semantics for the exact component reconstruction below.

## Discussion

A 25-hour duration has seconds=3600 because the remaining 24 hours occupy days. A negative one-microsecond duration has days=-1, seconds=86399 and microseconds=999999. Looking only at seconds loses the sign and the day contribution. Even a positive duration below one day can lose its fractional component if seconds is used alone.

Use total_seconds when a floating-point total is the intended representation. Use direct timedelta comparison when comparing durations, avoiding an unnecessary numeric conversion. If exact integer microseconds are required, combine the normalized integer components; the probe does that without a floating-point intermediate. It does not claim floating-point conversion is always exact.

## Conclusion

Choose the duration representation required by the application rather than treating a component as a total. Do not fix a negative duration with abs unless losing direction is actually intended. No wall-clock measurement, timezone arithmetic, deadline policy or rounding convention is established by this finding.

## Action

Original MIT-licensed probe using five small fixed durations, with no current-time calls, sleeps, files or network.

```python
import json
import platform
from datetime import timedelta

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def integer_microseconds(value):
    return ((value.days * 86400 + value.seconds) * 1_000_000
            + value.microseconds)

cases = [
    (timedelta(hours=25), (1, 3600, 0), 90_000_000_000),
    (timedelta(seconds=-1), (-1, 86399, 0), -1_000_000),
    (timedelta(microseconds=-1), (-1, 86399, 999999), -1),
    (timedelta(seconds=1, microseconds=500000), (0, 1, 500000), 1_500_000),
    (timedelta(0), (0, 0, 0), 0),
]
for duration, components, expected_us in cases:
    check((duration.days, duration.seconds, duration.microseconds) == components)
    check(integer_microseconds(duration) == expected_us)
    check(duration.total_seconds() == expected_us / 1_000_000)
    check(0 <= duration.seconds < 86400)

# Direct timedelta comparison preserves the sign; seconds alone does not.
negative = timedelta(microseconds=-1)
check(negative < timedelta(0))
check(negative.seconds > 0)
fraction = timedelta(seconds=1, microseconds=500000)
check(fraction.seconds == 1)
check(fraction.total_seconds() == 1.5)

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 24 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Checks cover multi-day, negative whole/fractional, positive fractional and zero durations, integer reconstruction and comparison. Large-interval float precision, overflow and timestamp subtraction are outside scope. Repository CI is separate.

## Publisher

One evidence-backed finding with a bounded executable probe. No date/time library replacement or production scheduling changes.
