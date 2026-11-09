# shorten normalizes whitespace before applying wrapper options

Date: 2026-11-10. Evidence-backed Python text-policy finding, not a new textwrap defect.

## Research

Python's versioned textwrap references state that shorten collapses whitespace before passing text to TextWrapper. Changing replace_whitespace, expand_tabs, drop_whitespace or tabsize does not undo that preprocessing. A public question about preserving line breaks and a separate textwrap guide discuss wrapper-level whitespace options. Those are useful wrapping references, not proof that the same flags preserve original whitespace in shorten. A community API reference and an independent shorten guide directly document the collapse step.

## Discussion

`shorten('  alpha\n\tbeta  ', 80, replace_whitespace=False)` returns `alpha beta`: the input was already normalized before the wrapper saw it. A large enough width therefore does not imply byte-for-byte preservation. Empty and whitespace-only inputs can normalize to an empty string.

Shortening also budgets the placeholder. With width 10 and placeholder `...`, `alpha beta gamma` becomes `alpha...`, not ten characters of the source followed by three extra characters. The sample long unbroken word at width 5 produces only the placeholder. This function is not an exact-prefix slicer.

| Intended result | Choice to define | Boundary |
| --- | --- | --- |
| One normalized text preview | shorten with width and placeholder policy | Original spacing and line breaks are discarded |
| Preserve paragraphs while wrapping | Define paragraph splitting and wrapper policy separately | Wrapper flags are not shorten preprocessing flags |
| Exact source prefix | Define explicit slicing/ellipsis policy | Still not a terminal-cell or grapheme-width calculation |

Do not use normalized preview text as the authoritative source for code, tables, records or whitespace-sensitive content. For a UI, decide whether line breaks, indentation and non-breaking spaces carry meaning before selecting the preview policy.

## Conclusion

Choose normalization and truncation separately. A no-op-looking width setting can still change content, and disabling one lower-level whitespace flag does not disable earlier normalization. Test short inputs as well as long ones, including the chosen placeholder's width.

The earlier dedent finding covers common indentation prefixes and tabs versus spaces; the split finding already covers whitespace tokenization. Those overlaps are acknowledged. This increment adds shorten's wrapper-option boundary, placeholder budgeting and invariants across bounded strings/widths. It does not claim a new discovery about whitespace splitting.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 97,659 checks over 3,906 toy strings and 15,624 width cases, plus selected boundary cases. Alphabet `ab` plus space, tab and newline, lengths 0..5; widths 3, 4, 6 and 9 with a three-character placeholder. All four selected whitespace-flag combinations agree with the default in that domain. One non-breaking-space sample is separate, not an exhaustive Unicode claim.

The oracle for normalization is explicit whitespace split/join. It is not an independent implementation of TextWrapper's truncation algorithm; the grid checks preprocessing equivalence and bounded output length, not every word-breaking policy. Run without optimization so assertions remain active.

```python
from itertools import product
from textwrap import shorten
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(shorten('  alpha\n\tbeta  ', 80, replace_whitespace=False) == 'alpha beta')
check(shorten('alpha beta gamma', 10, placeholder='...') == 'alpha...')
check(shorten('alpha', 10, placeholder='...') == 'alpha')
check(shorten('unbrokenlongword', 5, placeholder='...') == '...')
check(shorten(' \t\n', 8) == '')
check(shorten('a\u00a0b', 8) == 'a b')
for width in (0, -1):
    try:
        shorten('alpha', width, placeholder='...')
    except ValueError:
        check(True)
    else:
        raise AssertionError('nonpositive width accepted')
try:
    shorten('alpha', 2, placeholder='...')
except ValueError:
    check(True)
else:
    raise AssertionError('oversized placeholder accepted')

cases = 0
flags = (
    {'replace_whitespace': False},
    {'expand_tabs': False, 'tabsize': 1},
    {'drop_whitespace': False},
    {'replace_whitespace': False, 'expand_tabs': False,
     'drop_whitespace': False, 'tabsize': 3},
)
for size in range(6):
    for chars in product('ab \t\n', repeat=size):
        text = ''.join(chars)
        normalized = ' '.join(text.split())
        check(shorten(text, 30, placeholder='...') == normalized)
        for width in (3, 4, 6, 9):
            result = shorten(text, width, placeholder='...')
            check(len(result) <= width)
            check(result == shorten(normalized, width, placeholder='...'))
            for options in flags:
                check(shorten(text, width, placeholder='...', **options) == result)
            cases += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'strings': 3906, 'width_cases': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Exact published bytes are compared with the tested draft; committed code is extracted and rerun on both named builds.
- Synthetic in-memory strings only. No user documents, files or network. No performance, resource-bound or production formatter guarantee.
- No custom indentation, sentence-end fixing, hyphen policy, grapheme segmentation, terminal display width or exhaustive Unicode whitespace behavior tested. Python string length is not proof of visual width.
- The line-break question concerns wrapper behavior, not an original shorten-specific bug report. All linked content keeps its own authorship; code here is original.

## Sources

1. Python 3.13 textwrap reference, normalize-before-wrapper contract: https://docs.python.org/3.13/library/textwrap.html
2. Python 3.14 textwrap reference, same applicable contract: https://docs.python.org/3.14/library/textwrap.html
3. Community question about preserving line breaks in wrapping, not a shorten-specific report: https://stackoverflow.com/questions/1166317/python-textwrap-library-how-to-preserve-line-breaks
4. Community shorten API reference and examples: https://pydocs.org/textwrap/shorten
5. Independent textwrap guide (February 7, 2024), wrapper whitespace caveats: https://martinheinz.dev/blog/108
6. Independent shorten guide, preprocessing and ignored whitespace flags: https://docs-python.ru/standart-library/modul-textwrap-python/funktsija-shorten-modulja-textwrap/
