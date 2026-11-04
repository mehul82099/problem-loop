# argparse boolean options: `--cache False` can enable the feature

Date: 2026-11-04. A tested CLI design finding, not a new CPython defect.

## Research

The [argparse reference](https://docs.python.org/3/library/argparse.html) explicitly discourages `type=bool`: the converter calls `bool()` on the argument string, so non-empty strings become true. Python's [truth-value rules](https://docs.python.org/3.14/library/stdtypes.html) explain why the string `"False"` is truthy. An empty string is false, but that does not make `bool` a parser for textual boolean values.

This has confused real developers for years. [Python issue 26994](https://bugs.python.org/issue26994) includes a report of debugging the behavior in an internal script; it closed as a duplicate. [CPython issue 81745](https://github.com/python/cpython/issues/81745) records discussion of preserving the callable contract of `type`. The [community question](https://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse) contains several alternatives, but their accepted strings and defaults vary. This finding uses an explicit policy instead of treating those recipes as interchangeable.

## Discussion

`type=bool` means "apply bool to this string", not "validate the spelling of a boolean". Replacing it with `BooleanOptionalAction` changes the command-line interface: `--cache` and `--no-cache` consume no value. Existing shell scripts that pass `--cache False` must be migrated, or the parser must retain a value-taking option with an explicit converter.

Do not combine `action="store_true"` with `type=bool`. [Python issue 24754](https://bugs.python.org/issue24754), closed as not a bug, explains that a zero-argument action has no argument string to convert. The official argparse reference documents the flag alternatives.

## Conclusion

Use separate positive/negative flags for a new interface. Set a default deliberately: this example uses `None` to distinguish omission from an explicit false value, useful when a later configuration layer supplies the default. If preserving a value-taking interface, define the accepted spellings and reject unknown values. The converter below is case-insensitive, accepts only true/false, 1/0, on/off, and deliberately rejects whitespace-padded strings, empty strings and other words.

Both positive and negative flags are allowed together in this example; the last occurrence wins. Applications that need contradictory flags to be an error must implement that policy separately. No claim is made that one flag form is a drop-in replacement for the other.

## Action: executable regression probe

Executed on Linux x86_64 with CPython **3.13.17** and **3.14.9**. Each interpreter passed 18 cases: four legacy string conversions, five flag/default/order cases, six explicit value conversions, and three rejected inputs. That is 36 case executions across the two interpreters, not 36 separate test functions.

Observed legacy results for `--cache VALUE` with `type=bool`:

| VALUE | Parsed result |
|---|---|
| `False` | `True` |
| `0` | `True` |
| `off` | `True` |
| empty string | `False` |

The corrected flag parser returned `None` for omission, `True` for `--cache`, and `False` for `--no-cache`. It rejected `--cache False` with exit code 2. The explicit value parser returned false for `False`, `0`, and `OFF`, and rejected `maybe` and the empty string with exit code 2.

Save as `probe.py` and run with each supported interpreter. The probe has no network calls or filesystem writes.

```python
import argparse
import contextlib
import io
import json
import platform

legacy = argparse.ArgumentParser()
legacy.add_argument('--cache', type=bool)
observed = {s: legacy.parse_args(['--cache', s]).cache
            for s in ('False', '0', 'off', '')}
assert observed == {'False': True, '0': True, 'off': True, '': False}

flags = argparse.ArgumentParser()
flags.add_argument('--cache', action=argparse.BooleanOptionalAction, default=None)
flag_cases = [([], None), (['--cache'], True), (['--no-cache'], False),
              (['--cache', '--no-cache'], False),
              (['--no-cache', '--cache'], True)]
for argv, expected in flag_cases:
    assert flags.parse_args(argv).cache is expected

def text_bool(value):
    lowered = value.lower()
    if lowered in ('true', '1', 'on'):
        return True
    if lowered in ('false', '0', 'off'):
        return False
    raise argparse.ArgumentTypeError('expected true/false, 1/0, or on/off')

values = argparse.ArgumentParser()
values.add_argument('--cache', type=text_bool)
value_cases = [('TRUE', True), ('1', True), ('on', True),
               ('False', False), ('0', False), ('OFF', False)]
for text, expected in value_cases:
    assert values.parse_args(['--cache', text]).cache is expected

def rejects(parser, argv):
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            parser.parse_args(argv)
        except SystemExit as error:
            assert error.code == 2
        else:
            raise AssertionError('invalid input was accepted')

rejects(flags, ['--cache', 'False'])
rejects(values, ['--cache', 'maybe'])
rejects(values, ['--cache', ''])
print(json.dumps({'python': platform.python_version(), 'case_count': 18,
                  'legacy': observed, 'result': 'passed'}, sort_keys=True))
```

## Publisher checks and limits

- Original finding and example code are under this repository's MIT license. Upstream sources retain their own authorship.
- This confirms parser-level behavior on the two named interpreters. No real application's cache, configuration precedence, shell quoting, or deployment was exercised.
- The probe supplies an explicit argument list, so the empty-string case does not establish how every shell transports an empty argument.
- This is longstanding documented behavior, not an unpatched security issue or a claim of production impact. The practical contribution is a small repeatable regression check and a clear choice between two incompatible CLI contracts.
