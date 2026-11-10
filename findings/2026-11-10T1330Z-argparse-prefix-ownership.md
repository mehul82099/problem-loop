# parse_known_args can consume a downstream-looking option as an abbreviation

Date: 2026-11-10. A tested CLI option-ownership policy, not a new argparse defect.

## Research

Python's versioned argparse references explicitly warn that prefix matching also applies to parse_known_args. A unique prefix of a known long option can be recognized rather than returned in the remaining list. allow_abbrev=False disables long-option abbreviation. The historical documentation-warning issue is closed/fixed, and a later direct report of this behavior closed as not a bug.

A public question about disabling unique prefixes and an independent CLI guide corroborate this boundary. The documented purpose of partial parsing does not mean every token absent from the exact option spelling table is forwarded unchanged by default.

## Discussion

With --profile registered, parsing --prof=worker under the default policy assigns profile='worker' and returns no remaining token. In the named two-option sequence, that abbreviation even replaces an earlier --profile=fast value. With allow_abbrev=False, the exact known value stays fast and --prof=worker remains unparsed.

Adding another registered option can change the result again: --pro=x is no longer a unique prefix when both --profile and --progress exist. Partial parsing raises an ambiguity error rather than returning it as an unknown option. The probe catches the normal parser exit locally and does not compare version-specific diagnostic wording.

Disabling abbreviation is deliberately narrower than disabling parsing. Exact known options are still consumed. Normal grouped short flags such as -vv still work on the tested versions. This setting does not create a raw pass-through parser or establish which downstream process is allowed to receive the remaining arguments.

## Conclusion

For a wrapper that requires exact long-option ownership, choose allow_abbrev=False and test the remaining list as well as the namespace. Keep argument vectors structured and define collisions with exact known option names separately. If abbreviation is part of an existing user-facing CLI contract, disabling it is a compatibility change, not a universally safe drop-in fix.

The prior argparse findings cover bool conversion and non-string default conversion; neither covers option-prefix ownership. The earlier shlex finding concerns tokenizing text before argument parsing, not how already-separated tokens are assigned. Complete targeted searches and those prior scopes were inspected before this increment.

## Action

The original MIT-licensed diagnostic passed 188 checks each on actual CPython 3.13.17 and 3.14.9. It compares six proper long-option prefixes, three string values and two input forms, totaling 36 prefix/value/form cases. It checks parsed values, remaining vectors and unchanged caller input, plus exact-option precedence, unrelated unknown tokens, ambiguity and short-flag grouping. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import argparse
import contextlib
import io
import json
import platform
checks = cases = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def parser(abbrev):
    p = argparse.ArgumentParser(add_help=False, allow_abbrev=abbrev)
    p.add_argument('--profile')
    return p

for end in range(3, len('--profile')):
    prefix = '--profile'[:end]
    for value in ('fast', '', 'two words'):
        for argv in ([prefix, value], [prefix + '=' + value]):
            original = list(argv)
            known, tail = parser(True).parse_known_args(argv)
            check(known.profile == value)
            check(tail == [])
            exact, untouched = parser(False).parse_known_args(argv)
            check(exact.profile is None)
            check(untouched == original)
            check(argv == original)
            cases += 1

p = parser(False)
known, tail = p.parse_known_args(['--profile=fast', '--prof=worker'])
check(known.profile == 'fast')
check(tail == ['--prof=worker'])
known, tail = parser(True).parse_known_args(['--profile=fast', '--prof=worker'])
check(known.profile == 'worker')
check(tail == [])
known, tail = parser(False).parse_known_args(['--unrelated', 'x'])
check(known.profile is None and tail == ['--unrelated', 'x'])

# Adding another known option can make a formerly accepted prefix ambiguous.
p = parser(True)
p.add_argument('--progress')
with contextlib.redirect_stderr(io.StringIO()):
    try:
        p.parse_known_args(['--pro=x'])
    except SystemExit as error:
        check(error.code == 2)
    else:
        raise AssertionError('ambiguous prefix accepted')
# Disabling long-option abbreviation is not disabling normal short-flag groups.
p = argparse.ArgumentParser(add_help=False, allow_abbrev=False)
p.add_argument('-v', action='count', default=0)
known, tail = p.parse_known_args(['-vv', '--other'])
check(known.v == 2 and tail == ['--other'])
# Exact known arguments are still consumed; this is not a raw forwarding API.
known, tail = parser(False).parse_known_args(['--profile', 'fast', '--other'])
check(known.profile == 'fast' and tail == ['--other'])
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'prefix_value_forms': cases, 'status': 'passed'}))
```

## Publisher and limits

No process, file, shell, network or private configuration is used. This is not a forwarding wrapper, schema validator, security boundary, arbitrary-parser guarantee or performance benchmark. Positionals, subparsers, intermixed parsing, custom actions/types, from-file arguments, custom prefix characters and most short-option edge cases are untested. The remaining list is observed only, never executed or sent anywhere. Current versioned documentation pages identify newer patch releases than the tested binaries; contract evidence is not exact binary identity. Repository CI is separate from local runs.

## Sources

All six public sources inspected this cycle. The two official broad fetches timed out, so their exact sections were retrieved and inspected directly from HTML instead:

- Python 3.13 argparse: allow_abbrev, partial parsing warning and prefix matching. https://docs.python.org/3.13/library/argparse.html
- Python 3.14 argparse: corresponding current sections. https://docs.python.org/3.14/library/argparse.html
- Original direct report, closed as not a bug in 2023. https://github.com/python/cpython/issues/101915
- Historical documentation warning, issue 19814, closed/fixed in 2013. https://bugs.python.org/issue19814
- Public question about disabling unique-prefix matching. Historical pre-3.5 limitations are not asserted for the tested versions. https://stackoverflow.com/questions/33900846/disable-unique-prefix-matches-for-argparse-and-optparse
- Independent CLI guide, explicit forwarding boundary section. Its broader application recommendations are not tested here. https://cmdmemo.com/python/argparse-command-line-interfaces/
