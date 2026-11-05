# A successful fromisoformat parse is not a narrow wire-format check

Date: 2026-11-05. A parser-versus-application-contract distinction, not a new datetime defect.

## Research

The [datetime reference](https://docs.python.org/3/library/datetime.html) documents acceptance beyond one fixed timestamp layout: basic date forms, date-only input, an alternative single-character date/time separator and UTC Z examples. It records a broader accepted set starting in Python 3.11. A [conversion tutorial](https://note.nkmk.me/en/python-datetime-isoformat-fromisoformat/) describes basic forms and Z support, while a [historical developer question](https://stackoverflow.com/questions/75867446/documentation-example-for-datetime-fromisoformat-raises-invalid-isoformat-string) shows confusion caused by reading examples for a different Python version. That is historical context, not a current regression claim.

## Discussion

An API that requires exactly ASCII `YYYY-MM-DDTHH:MM:SSZ` should not use successful fromisoformat parsing as its entire input contract. Several documented inputs that parse correctly are outside that narrower shape, including basic dates, a space separator, an explicit +00:00 offset and fractional seconds. Their acceptance is not a parser defect.

The example below defines its own whole-second UTC grammar with hour 00-23 and minute/second 00-59, uses fullmatch to reject extra text, then parses to validate the remaining calendar date. This rejects leap seconds and 24:00 by policy. It is intentionally narrower than ISO 8601 and is not presented as a complete RFC 3339 validator. Do not replace an existing protocol's rules with this example without checking that protocol.

## Conclusion

Separate accepted text shape, date/time meaning and application policy. Choose those rules first, validate the required shape, and use a date parser for calendar semantics. Test accepted and rejected examples on the deployed Python versions instead of assuming the parser's accepted set is the application's contract.

## Action: narrow UTC whole-second contract probe

Ran 18 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover two accepted UTC dates, six broader parser inputs rejected by the example policy, invalid calendar/time cases and a trailing newline. The hour range is checked explicitly rather than delegated to parser acceptance. This probe does not test Python versions before 3.11.

```python
import json
import platform
import re
from datetime import datetime, timedelta

# Example application contract, not a full ISO 8601 or RFC 3339 validator.
UTC_SECONDS = re.compile(r'[0-9]{4}-[0-9]{2}-[0-9]{2}T(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]Z')

def parse_utc_seconds(text):
    if UTC_SECONDS.fullmatch(text) is None:
        raise ValueError('expected YYYY-MM-DDTHH:MM:SSZ in ASCII')
    return datetime.fromisoformat(text)  # Validates the remaining calendar date.

checks = 0
for text in ['2026-11-05T12:34:56Z', '2024-02-29T00:00:00Z']:
    parsed = parse_utc_seconds(text)
    assert parsed.utcoffset() == timedelta(0)
    checks += 1
# Valid broader parser inputs, deliberately outside this wire contract.
for text in ['20261105T123456Z', '2026-11-05 12:34:56Z',
             '2026-11-05X12:34:56Z', '2026-11-05',
             '2026-11-05T12:34:56+00:00',
             '2026-11-05T12:34:56.123Z']:
    datetime.fromisoformat(text)
    checks += 1
    try:
        parse_utc_seconds(text)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('expected contract rejection')
# Shape alone does not validate real dates or time ranges.
for text in ['2026-02-29T00:00:00Z', '2026-11-05T24:00:00Z',
             '2026-11-05T12:34:60Z', '2026-11-05T12:34:56Z\n']:
    try:
        parse_utc_seconds(text)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('expected invalid input rejection')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- Example contract only: no arbitrary ISO 8601 support, RFC conformance suite, leap-second model, timezone database, duration or interval parsing is included.
- Returning an aware UTC datetime does not establish freshness, authorization, event ordering or the correctness of an external timestamp.
- No production validation policy was changed. No new defect, security guarantee or performance claim is made.
