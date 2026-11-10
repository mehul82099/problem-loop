# expandtabs advances to tab stops, not fixed-width replacements

Date: 2026-11-10. A tested text-column contract, not a new Python defect.

## Research

The versioned Python string references define expandtabs using a current column, initially zero. For positive tabsize, a tab advances to the next multiple of tabsize, including a full interval when already on a stop. Newline and carriage return reset the column; every other character increases it by one regardless of its printed representation.

The original 2013 documentation tracker is closed/fixed, with an example and wording improvement, not an outstanding off-by-one bug. A 2023 Python discussion and a public Stack Overflow question show the recurring expectation that tabsize means a fixed number of spaces per tab. The independent Finxter guide includes the correct column algorithm but also says the default means eight spaces per tab. That shorthand is not adopted here: the number inserted depends on the column.

## Discussion

At width 4, `a\tb` becomes a plus three spaces plus b, while replacing each tab with four spaces produces a different string. `abcd\tb` does insert four spaces, because a tab at column 4 advances to column 8 rather than staying put. Different positive widths can produce equal output for a particular input without implying an implementation error.

The current column is a string-processing counter, not a measured display width. The probe checks that a single CJK character before a tab counts as one, while an e followed by a combining mark counts as two. It does not measure either string in a terminal or font. Vertical tab and form feed are copied and counted, not treated as newline resets; only the named newline/carriage-return cases reset in this contract.

## Conclusion

Use expandtabs when next-stop semantics under a chosen positive width are intended. Use an explicit fixed replacement only when that different transformation is intended. Neither is a general visual alignment algorithm, and converting whitespace in code or tables needs the owning format's rules.

The prior dedent finding already explains tabs versus spaces and demonstrates two expansion widths; shorten also discusses wrapper tab options. Both were inspected for overlap. This increment does not claim to discover tab-width policy: it isolates the positive-width next-stop formula, full-stop advancement, CR/LF reset versus other controls, and character-counter versus display-width boundary with a bounded oracle grid.

## Action

The original MIT-licensed diagnostic passed 23,352 checks each on actual CPython 3.13.17 and 3.14.9. It covers 7,775 string/width cases: 1,555 strings of lengths 0 through 4 over six characters, each at five positive widths. The simple oracle implements the documented column transitions. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import itertools
import json
import platform
checks = cases = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def oracle(text, width):
    # Positive widths only. Bounded oracle, not a terminal renderer.
    column = 0
    out = []
    for char in text:
        if char == '\t':
            count = width - column % width
            out.append(' ' * count)
            column += count
        else:
            out.append(char)
            column = 0 if char in '\r\n' else column + 1
    return ''.join(out)

for length in range(5):
    for chars in itertools.product(('a', '\t', '\n', '\r', '界', '\u0301'), repeat=length):
        text = ''.join(chars)
        for width in (1, 2, 3, 4, 8):
            actual = text.expandtabs(width)
            check(actual == oracle(text, width))
            check('\t' not in actual)
            check(actual.expandtabs(width) == actual)
            cases += 1
for prefix in range(17):
    check(('a' * prefix + '\tb').expandtabs(4) ==
          'a' * prefix + ' ' * (4 - prefix % 4) + 'b')
check('a\tb'.expandtabs(4) == 'a   b')
check('a\tb'.replace('\t', ' ' * 4) == 'a    b')
check('abcd\tb'.expandtabs(4) == 'abcd    b')
check('a\rb\tc'.expandtabs(4) == 'a\rb   c')
check('a\nb\tc'.expandtabs(4) == 'a\nb   c')
check('界\tx'.expandtabs(4) == '界   x')
check('e\u0301\tx'.expandtabs(4) == 'e\u0301  x')
check('a\v\tx'.expandtabs(4) == 'a\v  x')
check('a\fb\tx'.expandtabs(4) == 'a\fb x')
check('a\tb'.expandtabs() == 'a       b')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'string_width_cases': cases, 'status': 'passed'}))
```

## Publisher and limits

Grid checks compare exact text, tab removal and idempotence after expansion. Named checks add current-column offsets 0 through 16, fixed replacement contrast, default width, full-stop advancement, controls, CJK and combining text. These are string-equality tests, not visual rendering measurements.

No terminal, font, editor, filesystem, network or private document is used. Nonpositive and extremely large widths, arbitrary integer-like objects, bytes, ANSI escape interpretation, grapheme segmentation, syntax preservation, memory bounds and performance are untested. No production incident or upstream code patch is claimed. The current versioned docs name newer patch releases than the actual binaries tested; source contract and binary identity are kept separate. Repository CI is separate from local results.

## Sources

Six public sources fetched and relevant sections inspected this cycle:

- Python 3.13 string reference, exact expandtabs method section also extracted from HTML because the broad text fetch cut it off. https://docs.python.org/3.13/library/stdtypes.html
- Python 3.14 string reference, exact method section separately inspected: tab stops, resets and printed-representation qualification. https://docs.python.org/3.14/library/stdtypes.html
- Original documentation improvement, issue 17670, closed/fixed in 2013. Historical patch discussion is not an open runtime defect. https://bugs.python.org/issue17670
- Python discussion, December 2023, direct confusion about equal output for different sizes and fixed replacement versus tab stops. https://discuss.python.org/t/report-a-possible-problem-with-string-methods/42138
- Public question, December 2015, expandtabs versus replace. Its illustrative helper is not adopted as a full current implementation. https://stackoverflow.com/questions/34546171/python-expandtabs-string-operation
- Independent guide, March 2021, column algorithm with an overbroad eight-spaces shorthand, qualified above. https://blog.finxter.com/python-string-expandtabs/
