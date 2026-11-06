# argparse type converters do not validate every default value

Date: 2026-11-06. A documented conversion boundary, not a new argparse defect.

## Research

The [Python 3.14 argparse reference](https://docs.python.org/3.14/library/argparse.html) says type conversion applies to string defaults; other default values are used as supplied. A [community numeric-default question](https://stackoverflow.com/questions/35429336/argparse-doesnt-cast-default-numeric-arguments) demonstrates why type=float need not produce a float for an integer default. A [2025 nargs report](https://github.com/python/cpython/issues/132717) shows list defaults bypassing element-by-element conversion. The [3.14 implementation](https://github.com/python/cpython/blob/3.14/Lib/argparse.py) also distinguishes default handling from explicit command-line input.

An [older community question](https://stackoverflow.com/questions/11991021/argparse-add-argument-default-always-used-sometimes) discusses converters with validation side effects, while [historical issue 17250](https://bugs.python.org/issue17250) covers positional nargs corner cases. Neither source is treated as a blanket current timing rule. This finding tests only ordinary optional arguments and optional nargs='+', not positional or choices behavior.

## Discussion

A converter is a callable for interpreting command-line strings, not a schema enforcing every value eventually stored in the namespace. If the callable rejects negative numbers, a negative integer supplied as the default can still survive parsing with no arguments. The same negative value supplied as a string default passes through the converter and is rejected in this probe.

For nargs='+', a list default is already a non-string object. Argparse does not walk that list and call the converter on each element. Explicit values on the command line are converted individually. This distinction can matter when programmatic configuration, defaults and CLI values later share one application path.

## Conclusion

Construct defaults in the final form the application intends. If an invariant must hold regardless of where a value came from, validate the resulting configuration separately rather than assuming type= covered every source. Do not blindly rerun a string converter on already-converted objects; use an appropriate value validator. A sentinel default may be intentional, so enforcing uniform types is an application decision.

## Action

Original MIT-licensed probe. It parses owned local argument vectors, records converter calls and catches controlled conversion failures. No files, processes or network calls are made.

```python
import argparse
import json
import platform

checks = 0
calls = []

def check(condition):
    global checks
    assert condition
    checks += 1

def positive(text):
    calls.append(text)
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError('must be positive')
    return value

def parser(default, **kwargs):
    p = argparse.ArgumentParser(exit_on_error=False)
    p.add_argument('--count', type=positive, default=default, **kwargs)
    return p

calls.clear()
args = parser('2').parse_args([])
check(args.count == 2 and type(args.count) is int)
check(calls == ['2'])

calls.clear()
args = parser(-1).parse_args([])
check(args.count == -1)  # Non-string default bypasses the converter.
check(calls == [])

calls.clear()
args = parser(-1).parse_args(['--count', '3'])
check(args.count == 3)
check(calls == ['3'])

for default, argv in [('-1', []), (1, ['--count', '-1'])]:
    calls.clear()
    rejected = False
    try:
        parser(default).parse_args(argv)
    except argparse.ArgumentError:
        rejected = True
    check(rejected)
    check(calls == ['-1'])

calls.clear()
args = parser(['2', '3'], nargs='+').parse_args([])
check(args.count == ['2', '3'])  # Not converted element by element.
check(calls == [])

calls.clear()
args = parser([2], nargs='+').parse_args(['--count', '4', '5'])
check(args.count == [4, 5])
check(calls == ['4', '5'])

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 14 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Checks cover string-default conversion, non-string-default bypass, explicit conversion, rejection, and list defaults versus explicit nargs='+'. Positionals, choices, prefilled namespaces, subparsers, custom actions and resource-opening converters are outside scope. Repository CI is separate.

## Publisher

One evidence-backed finding with a bounded executable probe. No parser replacement or production configuration changes.
