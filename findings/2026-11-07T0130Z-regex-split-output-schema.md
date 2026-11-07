# Capturing groups change the output schema of re.split

## Research
Python's re.split includes captured separator groups in its result. Adding parentheses for pattern structure can therefore change a field-only list into a mixture of fields, captured delimiters and, for a group that did not participate, None. Public questions also show maxsplit being mistaken for a limit on the number of returned elements.

## Discussion
Use noncapturing groups when parentheses are only for grouping. Named groups still capture, and nested capturing groups can repeat the same separator text in the output. With alternatives, some group slots may be None. maxsplit limits separator matches used to split, not the number of elements after captures are inserted.

Boundary matches and adjacent delimiters can produce empty fields. Filtering falsey elements removes empty fields and unmatched-group markers but does not remove nonempty captured separators. It is a change to the result's meaning, not a safe generic cleanup step. Likewise, changing a separator from a single comma to a run of commas merges delimiter runs and loses the intervening empty fields.

## Conclusion
Treat captures in a split pattern as part of its public output contract. For field-only output, keep structural parentheses noncapturing and decide explicitly whether boundary and adjacent empty fields should remain. When delimiters must be retained, consume the documented capture slots rather than assuming all elements are fields or that maxsplit caps list length. This is documented behavior, not a new regex defect or a general parser.

## Action: executable probe
Original code under this repository's MIT license. In-memory strings only. Run without Python optimization so assertions remain enabled.

```python
import json
import platform
import re

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

text = 'a,b;c'
check(re.split(r'[,;]', text) == ['a', 'b', 'c'])
check(re.split(r'([,;])', text) == ['a', ',', 'b', ';', 'c'])
check(re.split(r'(?:[,;])', text) == ['a', 'b', 'c'])
check(re.split(r'(?P<sep>[,;])', text) == ['a', ',', 'b', ';', 'c'])
check(re.split(r'((,))', 'a,b') == ['a', ',', ',', 'b'])
check(re.split(r'(,)|;', text) == ['a', ',', 'b', None, 'c'])
check(re.split(r'(,)|(;)', text) == ['a', ',', None, 'b', None, ';', 'c'])
check(re.split(r'([,;])', text, maxsplit=1) == ['a', ',', 'b;c'])
check(re.split(r'((,))', 'a,b,c', maxsplit=1) == ['a', ',', ',', 'b,c'])
check(re.split(r'[,;]', ',a;') == ['', 'a', ''])
check(re.split(r'([,;])', ',a;') == ['', ',', 'a', ';', ''])
check(re.split(r',', 'a,,b') == ['a', '', 'b'])
check(re.split(r',+', 'a,,b') == ['a', 'b'])
check(re.split(r',', '') == [''])
check(re.split(r',', 'abc') == ['abc'])
check(re.compile(r'([,;])').split(text) == re.split(r'([,;])', text))
# Dropping falsey elements changes the field/schema information.
raw = re.split(r'(,)|;', ',a;')
check(raw == ['', ',', 'a', None, ''])
check(list(filter(None, raw)) == [',', 'a'])  # Still includes a separator.
check(re.split(r'(?:,|;)', ',a;') == ['', 'a', ''])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Covers capturing/noncapturing/named/nested groups, unmatched alternatives, maxsplit, boundary empties, adjacent delimiters, repeated delimiter runs, empty/no-match input, compiled patterns and the limits of falsey filtering.
- No zero-width separator patterns, bytes, flags, Unicode boundary semantics, quoted/escaped CSV fields, other regex engines, performance or production tokenizer were tested. Use a format-aware parser for structured formats; this probe does not supply one.

## Sources
- [Python 3.14 re](https://docs.python.org/3.14/library/re.html): split captures, boundary empties, maxsplit and compiled Pattern.split.
- [Python 3.14 regex HOWTO](https://docs.python.org/3.14/howto/regex.html): grouping and splitting guidance.
- [maxsplit question](https://stackoverflow.com/questions/64170487/python-re-split-with-maxsplit-argument): public mismatch between split count and result length.
- [Keeping separators question](https://stackoverflow.com/questions/2136556/in-python-how-do-i-split-a-string-and-keep-the-separators): intentional capture use; generic filtering suggestions not adopted.
- [Extraneous matches question](https://stackoverflow.com/questions/16488850/python-regex-extraneous-matchings): None for nonparticipating groups and empty results; old Python 2 syntax not used.
- [Finxter empty-result guide](https://blog.finxter.com/python-regex-split-without-empty-string/): example filtering approaches; loss of empty fields and None is explicitly qualified rather than recommended generally.
