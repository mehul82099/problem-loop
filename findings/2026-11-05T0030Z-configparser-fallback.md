# ConfigParser fallback does not override DEFAULT or repair an invalid value

Date: 2026-11-05. A tested configuration-precedence finding for documented behavior, not a new parser defect.

## Research

The [ConfigParser reference](https://docs.python.org/3/library/configparser.html) explicitly gives DEFAULT values precedence over getter fallback values. It describes lookup through vars, the selected section and DEFAULT in that order. An [independent ConfigParser guide](https://techbits.io/configparser-python/) also calls out this precedence. The [upstream implementation](https://github.com/python/cpython/blob/main/Lib/configparser.py) catches missing-section and missing-option exceptions for typed getter fallbacks, not arbitrary conversion failures.

## Discussion

Fallback means no effective value was found. It does not mean use this argument whenever the selected section lacks its own local entry. A default is an effective value inherited by that section, and membership and has_option also see inherited defaults. Removing a section override can reveal the default again.

The API level matters too. A section proxy accepts a second positional fallback in get(), while the parser's get(section, option, ...) uses its second positional argument for the option name. Use the fallback keyword explicitly at parser level. A present empty string is still present, and a present invalid integer raises ValueError instead of silently choosing the fallback.

## Conclusion

Write down the intended precedence before adding fallback arguments. Use vars for a deliberate per-call override, not fallback. If a malformed configured value should be rejected, keep the conversion error visible; if an application wants another policy, implement and test that separately. Do not treat effective section membership as proof that the file stored the option locally.

## Action: reproducible precedence probe

Ran 14 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64. They cover default-versus-fallback at both API levels, boolean default, missing option, empty value, inherited membership, local override removal, invalid integer conversion, vars precedence and a missing section. Interpolation is disabled so this probe isolates lookup and conversion rather than interpolation rules.

```python
import configparser
import json
import platform

cfg = configparser.ConfigParser(interpolation=None)
cfg.read_string('''[DEFAULT]
timeout = 30
enabled = no
[worker]
empty =
invalid = thirty
[custom]
timeout = 5
''')
worker = cfg['worker']
assert worker.getint('timeout', fallback=9) == 30
assert cfg.getint('worker', 'timeout', fallback=9) == 30
assert worker.getboolean('enabled', fallback=True) is False
assert worker.get('missing', 'backup') == 'backup'
assert cfg.get('worker', 'missing', fallback='backup') == 'backup'
assert worker.get('empty', fallback='backup') == ''
assert 'timeout' in worker
assert cfg.has_option('worker', 'timeout')
assert cfg['custom'].getint('timeout', fallback=9) == 5
assert cfg.remove_option('custom', 'timeout') is True
assert cfg['custom'].getint('timeout', fallback=9) == 30
try:
    worker.getint('invalid', fallback=9)
except ValueError:
    pass
else:
    raise AssertionError('malformed present value used fallback')
assert cfg.getint('worker', 'timeout', vars={'timeout': '7'}, fallback=9) == 7
assert cfg.getint('absent_section', 'timeout', fallback=9) == 9
print(json.dumps({'python': platform.python_version(), 'cases': 14, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- Tiny in-memory strings only. No user configuration, environment variables, files, secrets or external services are used.
- This is not an origin-tracking API, schema validator, settings-merger or production precedence policy. It does not inspect private section storage to infer provenance.
- No custom converters, interpolation errors, duplicate-section policy, allow_no_value mode, concurrency or timing behavior was tested. A getter fallback is not a blanket exception handler.
