# getenv defaults do not parse flags or replace empty values

Date: 2026-11-08. Scope: Python os.getenv and string truth testing, not a particular .env loader or configuration framework.

## Research

A public question asks how to evaluate a boolean environment variable. The official os.getenv contract is existence-based: return the stored string when the key exists, otherwise return the supplied default. An existing empty string is still a stored value. The truth-testing reference treats nonempty strings as true, so bool('false') and bool('0') are both true.

## Discussion

Two often combined shortcuts answer different questions. getenv(name, 'fallback') distinguishes missing from empty, while getenv(name) or 'fallback' replaces both missing and empty values. Neither converts text to a boolean. A boolean default also does not impose a boolean return type: getenv(name, False) returns False for the missing case but strings for present values, including 'false'.

The independent Django guide describes why assigning raw environment strings to DEBUG can be misleading. The Python-ideas discussion explains why spelling and empty-value rules are parsing choices. A historical Click pull request shows another framework's policy discussion about empty values; it is not treated as the current behavior of Click or as a requirement for os.getenv. Community examples differ in whether unknown tokens silently mean false or raise an error. Those are different contracts, not interchangeable fixes.

The probe chooses one deliberately narrow illustrative policy: missing means false; case and surrounding whitespace are normalized; true/false are the only accepted words; empty, numeric and unknown tokens raise. A product can choose a different policy, but must test it. In particular, automatically treating a typo as false can hide configuration mistakes.

## Conclusion

Keep presence, emptiness and parsing separate. Decide the default for missing input, what an explicitly empty value means, which spellings are valid and whether malformed input is an error. Convert at the configuration boundary instead of relying on generic string truthiness. This is documented behavior, not a new getenv defect or an incident claim about an application.

## Action

The original MIT-licensed probe passed 40 checks each on CPython 3.13.17 and 3.14.9. It launches isolated children with explicitly supplied synthetic environments, never copies or prints the parent's environment, and does not modify persistent configuration. It tests missing, empty, false/0 text, true text, whitespace and the illustrative strict parser. Each child has a five-second timeout. This is not a production settings library, .env-file test, cross-platform certification or test of environment reload behavior.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform
import subprocess
import sys

# Each child receives only synthetic environment entries, not the parent's.
CHILD = '''
import json, os
name = 'PROBLEM_LOOP_FLAG'
raw = os.getenv(name)
print(json.dumps([raw, os.getenv(name, 'fallback'), bool(raw),
                  os.getenv(name) or 'fallback', os.getenv(name, False)]))
'''
checks = 0

def check(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

for raw in (None, '', 'false', '0', 'true', '  '):
    env = {} if raw is None else {'PROBLEM_LOOP_FLAG': raw}
    run = subprocess.run([sys.executable, '-I', '-c', CHILD], env=env,
                         check=True, capture_output=True, text=True, timeout=5)
    seen, defaulted, truth, coalesced, bool_default = json.loads(run.stdout)
    check(seen, raw)
    check(defaulted, 'fallback' if raw is None else raw)
    check(truth, raw is not None and raw != '')
    check(coalesced, 'fallback' if raw in (None, '') else raw)
    check(type(bool_default) is bool, raw is None)

# Example policy: None defaults off; only true/false tokens accepted.
# Empty and unknown values are errors, case/edge whitespace normalized.
def parse_flag(raw):
    if raw is None:
        return False
    token = raw.strip().casefold()
    if token == 'true':
        return True
    if token == 'false':
        return False
    raise ValueError('expected true or false')

for raw, expected in [(None, False), ('true', True), ('TRUE', True),
                      (' false ', False), ('False', False)]:
    check(parse_flag(raw), expected)
for raw in ('', ' ', '0', 'yes', 'tru'):
    try:
        parse_flag(raw)
    except ValueError:
        checks += 1
    else:
        raise AssertionError('unknown token accepted')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and reproducible diagnostic. No private environment values, real credentials, third-party packages or network calls are used by the probe. Run without optimization so assertions remain active.

## Sources

All six public sources fetched and inspected this cycle:

- Official Python 3.14 os.getenv contract: https://docs.python.org/3.14/library/os.html
- Official truth-value rules, including empty strings: https://docs.python.org/3.14/library/stdtypes.html#truth-value-testing
- Community boolean-environment question and alternative parsing policies: https://stackoverflow.com/questions/63116419/evaluate-boolean-environment-variable-in-python
- Independent Django guide, raw strings and DEBUG: https://www.djangocookbook.com/recipes/fetch-settings-from-environment-variables/
- Python-ideas discussion of parsing choices, not an accepted API change: https://mail.python.org/archives/list/python-ideas@python.org/thread/AM2UUCLNSMKAYLTRBOGAVPDRW3REKJSK/
- Historical Click empty-value discussion, not current framework verification: https://github.com/pallets/click/pull/1023
