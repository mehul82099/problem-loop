# int conversion is not a narrow decimal-field grammar

Date: 2026-11-09. Evidence-backed Python finding, not a new conversion defect.

## Research

The Python int reference permits surrounding whitespace, an adjacent sign, single underscores between digits, leading zeros in base 10, and Unicode decimal digits. These are useful conversion features, but a successful conversion does not prove that a text field contains only ASCII digits. PEP 515 explicitly extended number-from-string constructors to support underscores. A public documentation clarification distinguishes int's accepted inputs from Python source-code integer literals.

## Discussion

`int(' 12 ')`, `int('+12')`, `int('1_2')`, Arabic-Indic digits and fullwidth digits can all produce 12. Switching to base 0 is not a stricter decimal parser: it admits base prefixes and changes leading-zero handling. For example, base 10 accepts `010`, base 0 rejects it, and base 0 accepts `0x10` as hexadecimal. All-zero text remains a special accepted case in base 0.

Whether these spellings should be accepted is an application decision. A user-facing localized number input may want Unicode decimal digits. A machine field specified as ASCII unsigned decimal may not. Do not silently trim, remove underscores or infer a base before checking a field whose spelling matters.

## Conclusion

| Required contract | Policy | Boundary |
| --- | --- | --- |
| General decimal conversion | `int(text, 10)` | Accepts more than ASCII digits |
| Python-style base detection | `int(text, 0)` | Prefix and leading-zero rules differ from decimal |
| Narrow ASCII unsigned field | Check full spelling and size before conversion | Choose sign, zero, width and range rules explicitly |
| Numeric object conversion | `int(value)` | Booleans and floats are not text-field validation |

The helper below deliberately defines a toy grammar: 1 through 6 ASCII digits, no signs or surrounding whitespace, leading zeros allowed. Six is a local policy choice, not a universal protocol limit. It returns a number, so `0012` and `12` become the same value; retain the original text separately if formatting or identity matters. A six-digit grammar does not establish a domain range such as a valid port, date or account ID.

## Action: small parser and diagnostic

Standard-library-only original code, covered by the repository MIT license. It rejects oversized input before int conversion and never changes the process-wide integer-string conversion limit.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def expect(exc, action):
    global checks
    try:
        action()
    except exc:
        checks += 1
    else:
        raise AssertionError(f'expected {exc.__name__}')

def ascii_uint(text):
    """Toy field policy: 1..6 ASCII decimal digits, leading zeros allowed."""
    if not isinstance(text, str):
        raise TypeError('field must be text')
    if not 1 <= len(text) <= 6 or any(c < '0' or c > '9' for c in text):
        raise ValueError('expected 1..6 ASCII decimal digits')
    return int(text, 10)

for text, value in [(' 12 ', 12), ('+12', 12), ('-0', 0),
                    ('1_2', 12), ('١٢', 12), ('１２', 12), ('0012', 12)]:
    check(int(text, 10) == value)
for text in (' 12 ', '+12', '-0', '1_2', '١٢', '１２'):
    expect(ValueError, lambda text=text: ascii_uint(text))
check(int('010', 10) == 10)
expect(ValueError, lambda: int('010', 0))
check(int('0x10', 0) == 16)
expect(ValueError, lambda: int('0x10', 10))
check(int('000', 0) == 0)
expect(ValueError, lambda: int('+ 12'))
for text, value in [('0', 0), ('000', 0), ('0012', 12), ('999999', 999999)]:
    check(ascii_uint(text) == value)
for text in ('', '1234567', '12\n', '12.0', '1e2', '0x10', '1 2', '²'):
    expect(ValueError, lambda text=text: ascii_uint(text))
for value in (True, 12, 12.9, b'12', None):
    expect(TypeError, lambda value=value: ascii_uint(value))
# Numeric conversion is intentionally distinct from text-field validation.
check(int(True) == 1)
check(int(12.9) == 12)
# Every ASCII code point is checked in a one-character field.
for n in range(128):
    text = chr(n)
    if '0' <= text <= '9':
        check(ascii_uint(text) == n - ord('0'))
    else:
        expect(ValueError, lambda text=text: ascii_uint(text))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **166 checks passed per build**. Cases cover whitespace, signs, underscores, selected Unicode digits, base prefixes, leading zeros, empty/oversized/non-text input, invalid decimal spellings and every one-character ASCII input. The examples do not test all Unicode digits or all Python implementations.

This is a bounded field-policy helper, not a general numeric parser or a security boundary for an unspecified protocol. Repository CI is separate from local checks.

## Publisher and sources

Published deliverable: this finding and runnable helper/probe. Six relevant source pages were read. Current Python reference owns the conversion contract; historic forum implementation comparisons are not treated as current cross-implementation results.

1. [Python 3.14 int reference](https://docs.python.org/3.14/library/functions.html#int), primary documentation: signs, whitespace, underscores, Unicode decimal digits and base rules.
2. [PEP 515](https://peps.python.org/pep-0515/), primary design: underscore grouping in constructors as well as literals.
3. [CPython documentation clarification PR 100436](https://github.com/python/cpython/pull/100436), public project discussion: constructor inputs differ from literal grammar, including leading zeros and Unicode digits. No changes to that repository are made here.
4. [Python 3.14 lexical analysis](https://docs.python.org/3.14/reference/lexical_analysis.html#integer-literals), primary language reference: source-literal grammar is a different contract from conversion input.
5. [Discussion of a space after an int sign](https://discuss.python.org/t/bug-in-int-42/26360), community discussion, 2023: sign adjacency matters. Its old alternative-interpreter observations were not reproduced here.
6. [Converting a Python string to int](https://realpython.com/convert-python-string-to-int/), independent tutorial, 2019: distinguishes parse failure from successfully choosing the wrong intended base. This finding adds an explicit narrow grammar rather than claiming conversion is defective.
