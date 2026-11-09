# Keep the ISO week-year with its week number

Date: 2026-11-09. Evidence-backed Python finding, not a new datetime defect.

## Research

A public Python question shows the first and last days of 2019 both formatted as '2019-W01' by mixing %Y with %V. The calendar year and ISO week-year are different fields near New Year. Python's isocalendar returns ISO year, week and weekday together; fromisocalendar converts that tuple back to a date.

## Discussion

The ISO week starts on Monday, and week 1 contains the year's first Thursday. A late-December date can therefore be in the next ISO year, while an early-January date can remain in the previous ISO year. Keeping date.year with isocalendar().week silently mixes two calendars.

| Gregorian date | Computed ISO year/week/weekday | Week key |
| --- | --- | --- |
| 2019-01-01 | 2019 / 1 / 2 | 2019-W01 |
| 2019-12-31 | 2020 / 1 / 2 | 2020-W01 |
| 2021-01-01 | 2020 / 53 / 5 | 2020-W53 |
| 2025-12-29 | 2026 / 1 / 1 | 2026-W01 |
| 2026-12-31 | 2026 / 53 / 4 | 2026-W53 |
| 2027-01-01 | 2026 / 53 / 5 | 2026-W53 |

These exact date tuples are calculated by the attached probe, not inferred from a remembered calendar. The mixed pair (date.year, ISO week) collides for the two 2019 dates shown, even though they belong to different ISO weeks. Conversely, 2020-12-28 and 2021-01-03 belong to the same ISO week despite having different Gregorian years.

ISO years have 52 or 53 weeks. Incrementing a week integer without validating the ISO year can create a nonexistent week such as 2021-W53. For a specific day, use the full ISO tuple and fromisocalendar, including its weekday. A week key alone intentionally loses the day; it is a grouping label, not a unique date or instant.

## Conclusion

Build ISO week keys from the ISO year and ISO week returned by the same isocalendar call. If formatting directives are used, %G is the ISO year paired with %V; %Y is the Gregorian year. The helper below avoids platform strftime support altogether and uses the returned integers.

Do not relabel a fiscal, locale-specific, Sunday-start or business week as ISO. Also do not pass a timestamp straight into a date-only grouping rule: first choose the reporting timezone and derive its date. The helper deliberately rejects datetime instances rather than silently discarding time and timezone. It is not a fiscal-calendar implementation, timezone converter, schedule or holiday rule.

## Action: date-only key helper and boundary diagnostic

Original standard-library-only code under the repository MIT license. No current clock, timestamp conversion, network or file operations. Run without -O so assertions remain enabled. The bounded full-cycle test checks all 146,097 Gregorian dates from 2000-01-01 through 2399-12-31, not every possible date or timezone.

```python
# Original date-only diagnostic, MIT license (repository LICENSE).
from datetime import date, datetime, timedelta
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def iso_week_key(day):
    # Date-only input requires caller to choose a reporting timezone upstream.
    if type(day) is not date:
        raise TypeError('expected an exact date, not datetime or text')
    iso = day.isocalendar()
    return f'{iso.year:04d}-W{iso.week:02d}'

def raises(kind, operation):
    try:
        operation()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

for day, expected in (
    (date(2019, 1, 1), (2019, 1, 2)),
    (date(2019, 12, 31), (2020, 1, 2)),
    (date(2021, 1, 1), (2020, 53, 5)),
    (date(2025, 12, 29), (2026, 1, 1)),
    (date(2026, 12, 31), (2026, 53, 4)),
    (date(2027, 1, 1), (2026, 53, 5)),
):
    check(day.isocalendar() == expected)
    check(date.fromisocalendar(*expected) == day)
    check(iso_week_key(day) == f'{expected[0]:04d}-W{expected[1]:02d}')

# Mixed calendar-year/ISO-week labels collide for distinct ISO weeks.
first, last = date(2019, 1, 1), date(2019, 12, 31)
mixed = lambda d: (d.year, d.isocalendar().week)
check(mixed(first) == mixed(last))
check(iso_week_key(first) != iso_week_key(last))
check(iso_week_key(date(2020, 12, 28)) == iso_week_key(date(2021, 1, 3)))
check(iso_week_key(date(2021, 1, 4)) == '2021-W01')
raises(ValueError, lambda: date.fromisocalendar(2021, 53, 1))
raises(ValueError, lambda: date.fromisocalendar(2026, 0, 1))
raises(ValueError, lambda: date.fromisocalendar(2026, 1, 8))
for bad in ('2026-01-01', None, datetime(2026, 1, 1)):
    raises(TypeError, lambda: iso_week_key(bad))

# Gregorian 400-year cycle, all days, no platform strftime dependency.
day, stop = date(2000, 1, 1), date(2400, 1, 1)
while day < stop:
    iso = day.isocalendar()
    check(date.fromisocalendar(*iso) == day)
    monday = day - timedelta(days=iso.weekday-1)
    thursday = monday + timedelta(days=3)
    check(iso.year == thursday.year)
    check(1 <= iso.week <= 53 and 1 <= iso.weekday <= 7)
    day += timedelta(days=1)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

438,319 checks passed separately on CPython 3.13.17 and 3.14.9. The full 400-year date range checks roundtrip conversion, ISO-year agreement with the week's Thursday, and valid field ranges, plus 28 focused checks for exact year-boundary cases, mixed-key collision, a week spanning Gregorian years, invalid ISO dates and rejected helper types. The roundtrip is a consistency test of Python's paired APIs, not an independent implementation of ISO 8601. No strftime portability guarantee is claimed.

## Sources

1. [Python 3.13 datetime reference](https://docs.python.org/3.13/library/datetime.html): isocalendar rules and inverse fromisocalendar.
2. [Python 3.14 datetime reference](https://docs.python.org/3.14/library/datetime.html): corroborating versioned contract.
3. [Python 3.14 time reference](https://docs.python.org/3.14/library/time.html): %Y, %G and %V definitions and platform-format caveats.
4. [Public mixed-year formatting question](https://stackoverflow.com/questions/62640924/datetime-iso-week-says-first-and-last-day-of-year-are-both-in-same-week), 2020-06-29: user-visible collision example, not a new bug report here.
5. [ISO Week Date library rationale](https://fbruzzesi.github.io/iso-week-date/user-guide/why-iso-week-date/): independent explanation of year-label and week-arithmetic pitfalls. No dependency installed or recommendation to adopt the library.
6. [Timeanddate week-number explainer](https://www.timeanddate.com/date/week-numbers.html): independent context that week numbering schemes vary; Python's explicit contract governs the code here.

The contribution is an original boundary probe and date-only reporting contract, not a newly discovered calendar rule or evidence that a named production report is wrong.
