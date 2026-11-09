# Reading an INI file is not validation of its interpolation

Date: 2026-11-10. Tested ConfigParser evaluation policy, not a new parser defect.

## Research

Python's versioned references say BasicInterpolation is the default, interpolation is performed on demand, and `%%` represents a literal percent under that policy. An original January 2013 question reports percent-containing values failing on retrieval. A 2023 Flit pull request and an older Twine issue show the same problem in package-upload settings. These are historical reports, not claims that either project is still affected. PyMOTW independently demonstrates interpolation, escaping, raw reads and disabling interpolation.

Some community text calls this environment-variable substitution. That is not the default BasicInterpolation contract: it resolves values from configuration lookup, not automatic access to the process environment. This probe does not read environment variables or real credentials.

## Discussion

`read_string()` can accept `value = 80%`, while a later ordinary `get()` raises InterpolationSyntaxError. Existence checks are not expansion checks. A missing `%(name)s` reference instead raises InterpolationMissingOptionError; a self-reference reaches InterpolationDepthError. A getter fallback does not replace these present-but-invalid values.

| Intended format | Deliberate choice | Consequence |
| --- | --- | --- |
| Literal settings | `ConfigParser(interpolation=None)` | Percent data stays literal; intentional references no longer expand |
| BasicInterpolation format | Store literal percent as `%%` | Normal retrieval unescapes it to `%` |
| One raw retrieval | `get(..., raw=True)` | Bypasses interpolation for that read, not future reads |

For example, `%(root)s/out` resolves under the default policy but stays a placeholder when interpolation is disabled. Raw retrieval of `80%%` returns both percent signs, while ordinary retrieval returns one. Do not blindly double percent signs in an already-escaped file or turn off expansion without checking consumers.

API entry points also differ. For this tested parser, `set(..., '80%')` rejects invalid syntax immediately, whereas `read_string()` defers that failure to retrieval. A successful parse alone is therefore not a promise that all configured values are usable. INI comments, whitespace, delimiters and option-name rules still apply when interpolation is off; it is not a byte-preserving arbitrary-text format.

## Conclusion

Choose literal data or interpolated templates as part of the configuration contract. Validate required values through the same retrieval path the application will use. Report option names and error types rather than dumping settings that may contain secrets. Disabling interpolation is neither credential storage protection nor a general security sandbox.

The earlier ConfigParser fallback finding already covers DEFAULT lookup and conversion failures and explicitly disables interpolation. This increment acknowledges the fallback overlap but adds lazy percent expansion, distinct interpolation failures, raw-versus-normal retrieval, mutation-time validation and escaped write/read checks. No precedence novelty is claimed.

## Action

Original standard-library-only probe under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 6,582 checks across 1,093 exhaustive toy strings plus selected failure/reference cases. The toy alphabet is `a%$`, lengths 0..6. Every string is checked with interpolation disabled, per-read raw access, one deliberate percent-escaping pass, and an in-memory write/read round trip. Run without optimization so assertions remain active.

```python
import configparser as cp
import io
import itertools
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def raises(kind, action):
    try:
        action()
    except kind:
        check(True)
    else:
        raise AssertionError('expected ' + kind.__name__)

def parse(value, *, literal=False):
    cfg = cp.ConfigParser(interpolation=None) if literal else cp.ConfigParser()
    cfg.read_string('[demo]\nvalue = ' + value + '\n')
    return cfg

# Reading text stores a value; expansion can fail later.
for text in ('80%', '%20', '%x', '%(missing)s'):
    cfg = parse(text)
    check(cfg.has_option('demo', 'value'))
    check(cfg.get('demo', 'value', raw=True) == text)
    expected = cp.InterpolationMissingOptionError if text == '%(missing)s' else cp.InterpolationSyntaxError
    raises(expected, lambda: cfg.get('demo', 'value', fallback='backup'))
    check(parse(text, literal=True).get('demo', 'value') == text)

cfg = cp.ConfigParser()
cfg.read_string('[demo]\nroot = /toy\npath = %(root)s/out\nescaped = 80%%\nloop = %(loop)s\n')
check(cfg.get('demo', 'path') == '/toy/out')
check(cfg.get('demo', 'path', raw=True) == '%(root)s/out')
check(cfg.get('demo', 'path') == '/toy/out')  # raw did not change policy
check(cfg.get('demo', 'escaped') == '80%')
check(cfg.get('demo', 'escaped', raw=True) == '80%%')
raises(cp.InterpolationDepthError, lambda: cfg.get('demo', 'loop', fallback='backup'))
# set validates syntax earlier than read_string for this API/configuration.
raises(ValueError, lambda: cfg.set('demo', 'bad', '80%'))
check(not cfg.has_option('demo', 'bad'))

# Exhaustive toy values, no comments, leading/trailing whitespace or newlines.
cases = 0
for size in range(7):
    for chars in itertools.product('a%$', repeat=size):
        text = ''.join(chars)
        literal = parse(text, literal=True)
        check(literal.get('demo', 'value') == text)
        check(parse(text).get('demo', 'value', raw=True) == text)
        escaped = text.replace('%', '%%')
        basic = parse(escaped)
        check(basic.get('demo', 'value') == text)
        check(basic.get('demo', 'value', raw=True) == escaped)
        output = io.StringIO()
        basic.write(output)
        reread = cp.ConfigParser()
        reread.read_string(output.getvalue())
        check(reread.get('demo', 'value') == text)
        check(reread.get('demo', 'value', raw=True) == escaped)
        cases += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'toy_values': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Tested draft is compared with published bytes; committed code is extracted and rerun on both named builds.
- No files, environment values, accounts, network requests or real credentials are used by the probe. All INI documents are synthetic; StringIO is memory only.
- No ExtendedInterpolation, custom handlers, concurrency, resource limits or arbitrary-input safety is promised. The probe is not a production configuration validator.
- Round-trip checks cover only the bounded toy values, not preservation of formatting, comments or arbitrary INI text. Existing escape policy must be known before a migration.

## Sources

1. Python 3.13 ConfigParser reference, on-demand expansion and raw reads: https://docs.python.org/3.13/library/configparser.html
2. Python 3.14 ConfigParser reference, same applicable contracts: https://docs.python.org/3.14/library/configparser.html
3. Original January 15, 2013 percent-value report and constructor/escaping discussion: https://stackoverflow.com/questions/14340366/configparser-and-string-with/28874886
4. Flit historical pull request (August 2023), percent-containing upload setting and interpolation=None discussion: https://github.com/pypa/flit/pull/652/
5. Twine historical issue, percent-containing .pypirc values: https://github.com/pypa/twine/issues/186
6. PyMOTW independent guide, escaping, raw retrieval and disabling interpolation: https://pymotw.com/3/configparser/
