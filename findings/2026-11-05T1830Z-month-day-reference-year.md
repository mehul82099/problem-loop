# Yearless month/day parsing inherits a non-leap default year

Date: 2026-11-06. A documented partial-date parsing distinction, not a new datetime defect.

## Research

The version-specific [Python 3.13 datetime reference](https://docs.python.org/3.13/library/datetime.html) and [Python 3.14 reference](https://docs.python.org/3.14/library/datetime.html) warn about parsing a day of month without a year and recommend explicitly adding a leap year for partial-date inputs. A [CPython change discussion](https://github.com/python/cpython/pull/144570) records the compatibility problem around yearless parsing. Newer removal behavior is not tested here; the baseline below is limited to the two named builds.

## Discussion

On these builds, strptime('02/28', '%m/%d') returns a datetime in 1900. Parsing '02/29' with the same format raises ValueError because 1900 is not a leap year. An otherwise reasonable-looking month/day parser can therefore reject leap day even when the application means a year-independent recurring date.

The helper below chooses an exact ASCII MM/DD input shape and appends the explicit reference year 2000 before calendar parsing. It returns only the month/day pair so that the artificial reference year is not mistaken for the actual event year. An annual schedule still needs its own rule for February 29 in non-leap years; this helper does not choose one.

## Conclusion

Do not let the parser's implicit year define a partial-date policy. If the input truly represents a month/day rather than a full date, validate it with an explicit leap reference year and keep that reference separate from event scheduling. If the input should contain an actual year, require it instead of inserting a guessed one.

## Action: explicit-reference-year probe

Ran 13 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Two baseline checks demonstrate the 1900 default and leap-day failure. The helper tests four valid month/day pairs and seven invalid shape or calendar inputs. Baseline DeprecationWarning is locally suppressed to keep the diagnostic output clear; warning emission and exact wording are not asserted.

```python
import json
import platform
import re
import warnings
from datetime import datetime

# Exact ASCII MM/DD policy. The reference year is not an event year.
def parse_month_day(text):
    if re.fullmatch(r'[0-9]{2}/[0-9]{2}', text) is None:
        raise ValueError('expected MM/DD')
    parsed = datetime.strptime(text + ';2000', '%m/%d;%Y')
    return parsed.month, parsed.day

checks = 0
with warnings.catch_warnings():
    warnings.simplefilter('ignore', DeprecationWarning)
    assert datetime.strptime('02/28', '%m/%d').year == 1900
    checks += 1
    try:
        datetime.strptime('02/29', '%m/%d')
    except ValueError:
        checks += 1
    else:
        raise AssertionError('expected non-leap default-year failure')
for text, expected in [('02/29', (2, 29)), ('02/28', (2, 28)),
                       ('12/31', (12, 31)), ('01/01', (1, 1))]:
    assert parse_month_day(text) == expected
    checks += 1
for text in ['02/30', '04/31', '13/01', '00/01', '2/29',
             '02/29\n', '02/29;2026']:
    try:
        parse_month_day(text)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('expected invalid month/day rejection')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- The helper selects one exact input layout. It is not a natural-language, localized or arbitrary partial-date parser.
- No Python 3.15 run, future compatibility guarantee, annual-recurrence policy, timezone conversion or calendar mutation is included.
- No real birthday, event or production input was used. No new runtime defect or performance claim is made.
