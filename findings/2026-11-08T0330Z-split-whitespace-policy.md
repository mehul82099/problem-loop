# split() and split(" ") are different parsing policies

Date: 2026-11-08. Scope: Python str.split, not bytes.split or regular-expression splitting.

## Research

A public question shows confusion about sep=None with maxsplit, including maxsplit=0. The current official reference describes two algorithms: omitted/None sep groups whitespace runs, while a specified nonempty separator matches that literal delimiter and preserves empty fields. Passing a literal space is not an explicit spelling of the default.

## Discussion

For example, ' a  b '.split() returns ['a', 'b'], but split(' ') returns ['', 'a', '', 'b', '']. Tabs and newlines separate words in the first mode, but are ordinary data for a literal-space separator. The probe also checks a non-breaking space, without claiming that every visually blank character is whitespace. Empty input produces [] in the default mode versus [''] with a specified separator.

A limit adds a second decision. With sep=None, maxsplit=0 still removes leading whitespace and can return [] for an all-whitespace input; it does not mean return the original string untouched. With a literal separator and zero splits, the original string is the sole element. At maxsplit=1, '  a  b  '.split(None, 1) preserves the trailing spaces in the remainder. Treating the operation as strip().split(...) silently changes that remainder.

The historical CPython issues show that this boundary caused documentation questions years ago, including a documentation correction. They are not evidence of a new runtime defect. The independent guide explains maxsplit as a limit and preservation of the remainder; the official reference and implementation settle the zero-limit details. maxsplit+1 is an upper bound on output length, not a promise of exactly that many fields.

## Conclusion

Choose the separator from the data contract. Use default whitespace splitting for word-like tokens when whitespace runs and discarded edge whitespace are intended. Use a literal separator when repeated delimiters and empty fields carry meaning. Set and test the limit separately, including empty and whitespace-only records. Do not replace a protocol-specific parser with either mode merely because one happy-path row looks right.

## Action

The original MIT-licensed probe below passed 23 checks each on CPython 3.13.17 and 3.14.9. It covers the two separator policies, empty input, whitespace runs, Unicode example, zero and positive limits, remainder preservation, a multi-character delimiter, an unlimited case and rejection of an empty separator. These are deterministic examples, not exhaustive Unicode or file-format validation.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

check(''.split(), [])
check(''.split(' '), [''])
check(' \t\n'.split(), [])
check('  '.split(' '), ['', '', ''])
check(' a  b '.split(), ['a', 'b'])
check(' a  b '.split(None), ['a', 'b'])
check(' a  b '.split(' '), ['', 'a', '', 'b', ''])
check('a\tb\nc'.split(), ['a', 'b', 'c'])
check('a\tb\nc'.split(' '), ['a\tb\nc'])
check('a\u00a0b'.split(), ['a', 'b'])
check('a\u00a0b'.split(' '), ['a\u00a0b'])
check('  a  b  '.split(None, 0), ['a  b  '])
check('  a  b  '.split(' ', 0), ['  a  b  '])
check(''.split(None, 0), [])
check('   '.split(None, 0), [])
check('  a  b  '.split(None, 1), ['a', 'b  '])
check('  a  b  '.split(None, 2), ['a', 'b'])
check('a'.split(None, 9), ['a'])  # maxsplit+1 is a ceiling, not a length.
check('a::b::::'.split('::'), ['a', 'b', '', ''])
check('a,,b,'.split(','), ['a', '', 'b', ''])
check('a,,b,'.split(',', 1), ['a', ',b,'])
check(' a '.split(None, -1), ['a'])
try:
    'abc'.split('')
except ValueError:
    checks += 1
else:
    raise AssertionError('empty separator must fail')

print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding with a reproducible probe. This describes documented behavior, not a new bug or an upstream patch. No external packages, network calls or private data are required by the probe.

## Sources

Six public sources inspected during this cycle:

- Official Python 3.14 str.split reference, including the maxsplit=0 clause. The fetched page extraction ended before this section, so the exact HTML section was also retrieved and inspected: https://docs.python.org/3.14/library/stdtypes.html#str.split
- CPython 3.14 implementation, whitespace scan and copying the remaining suffix: https://github.com/python/cpython/blob/3.14/Objects/stringlib/split.h
- Community question illustrating None and limited-split confusion: https://stackoverflow.com/questions/71088479/strange-behavior-of-python-str-split-when-using-the-default-sep-value-none
- Historical CPython documentation discussion and correction: https://github.com/python/cpython/issues/45464
- Historical zero-limit documentation question: https://github.com/python/cpython/issues/42836
- Independent guide, delimiter choice and maxsplit remainder: https://realpython.com/python-split-string/
