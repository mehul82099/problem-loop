# Pattern escaping is not literal replacement handling

Date: 2026-11-09. Evidence-backed Python finding, not a new regex defect.

## Research

Python's versioned re references explicitly say not to use `re.escape` for replacement strings in `sub` or `subn`. It prepares pattern syntax. A string replacement is a different grammar: backslash escapes and group references are processed. The replacement string returned by a callable is used as replacement text instead.

A 2012 public question reports literal backslash-n becoming a newline during replacement. A 2019 independent blog describes the same issue in generated text and the unwanted extra backslashes produced by applying re.escape. CPython documentation issue 128138 discusses both doubling only backslashes and using a callable. These are longstanding contract distinctions, not evidence that the regex engine computed an incorrect result.

## Discussion

With the fixed pattern `(?P<token>X)`:

| Replacement input | String-template result for X | Literal-data result via callable |
| --- | --- | --- |
| backslash followed by 1 | X, from group 1 | backslash followed by 1 |
| backslash followed by g<token> | X, from named group | unchanged input text |
| backslash followed by n | newline character | two input characters |
| re.escape of a.b | a backslash dot b | a.b when the original value is returned |
| lone backslash or backslash-q | replacement syntax error | unchanged input text |

Raw string notation only controls Python source-literal parsing. It does not disable the later replacement-template parser. Similarly, escaping too much is not harmless here: the dot and space already need no replacement quoting, and pattern escapes for them can survive into the output.

## Conclusion

When regex matching is needed but the replacement is literal data, return that value from a callable. If a string replacement API must be used for literal text, the documented alternative is to double only backslashes. When template backreferences are intended, keep the template and test that separate contract. When the search is also just a literal substring, consider the simpler string replacement operation instead of introducing regex syntax.

This controls replacement interpretation only. It does not make an arbitrary pattern safe, bound matching time or output size, validate output for another format, or make a callback side-effect-free. No security boundary is claimed.

## Action

Original code under this repository's MIT license. Fixed nonempty in-memory pattern and bounded strings only; no files or network. Run without Python optimization so assertions remain enabled.

```python
import itertools
import json
import platform
import re

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

p = re.compile(r'(?P<token>X)')
check(p.sub(r'\1', 'X') == 'X')
check(p.sub(r'\g<token>', 'X') == 'X')
check(p.sub(r'\n', 'X') == '\n')
check(p.sub(re.escape('a.b'), 'X') == r'a\.b')
check(p.sub(re.escape('a b'), 'X') == 'a\\ b')
for template in (r'\q', '\\', r'\2'):
    try:
        p.sub(template, 'X')
    except re.PatternError:
        check(True)
    else:
        raise AssertionError('invalid replacement accepted')

alphabet = ('a', '.', ' ', '\\', '1', 'n', '<', '>', '\n', 'é')
values = ['', r'\g<token>', r'\q', r'C:\new\text', '\x00', '🙂']
values += [''.join(chars) for size in range(1, 4)
           for chars in itertools.product(alphabet, repeat=size)]
for value in values:
    # p has a nonempty, fixed literal target; no user-supplied regex.
    got, n = p.subn(lambda match: value, 'L:X|X:R')
    check(got == 'L:' + value + '|' + value + ':R')
    check(n == 2)
    escaped_backslashes = value.replace('\\', '\\\\')
    check(p.sub(escaped_backslashes, 'L:X|X:R') == got)
    check(p.subn(lambda match: value, 'L:X|X:R', count=1)
          == ('L:' + value + '|X:R', 1))
    check(p.subn(lambda match: value, 'no token') == ('no token', 0))

# Callback executes once per match and its return is not rescanned.
seen = []
def callback(match):
    seen.append(match.span())
    return r'X\1'
check(p.subn(callback, 'X X') == (r'X\1 X\1', 2))
check(seen == [(0, 1), (2, 3)])
print(json.dumps({'checks': checks, 'values': len(values),
                  'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **5,590 checks passed per build**. There are 1,116 replacement values: six explicit fixtures plus every length-1..3 string over a ten-character alphabet. The checks compare exact callable output and backslash-only escaping, two matches, count=1 and no match. Separate checks distinguish template group references, newline conversion, punctuation over-escaping, invalid templates and callback match spans. Returned text containing X is not recursively substituted.

This is not an exhaustive Unicode test or performance benchmark. No bytes patterns, zero-width patterns, arbitrary user patterns, callback exceptions, structured-format edits, files or production systems were tested. A substitution count reports match cardinality, not whether a semantic field was the right one to edit.

## Publisher

One bounded finding and standalone probe. Full targeted repository search found no previous re.escape/replacement-template finding. Existing repeated-capture, split-output and pos-boundary findings concern different regex contracts.

## Sources

1. [Python 3.13 re reference](https://docs.python.org/3.13/library/re.html), primary documentation: string versus callable repl, subn and explicit re.escape warning.
2. [Python 3.14 re reference](https://docs.python.org/3.14/library/re.html), primary documentation: same contracts and invalid ASCII-letter escapes.
3. [Python 3.14 regex HOWTO](https://docs.python.org/3.14/howto/regex.html), official tutorial: search/replace, backreferences and callable replacement.
4. [CPython issue 128138](https://github.com/python/cpython/issues/128138), documentation discussion opened December 20, 2024: backslash-only escaping versus literal callable results. No third-party test count is adopted as local verification.
5. [Python unescaping string in regex replacements](https://stackoverflow.com/questions/12127472/python-unescaping-string-in-regex-replacements), August 26, 2012 community question: newline conversion and callable answer. Raw notation alone is not used as a general replacement-data solution.
6. [Python re.sub gotcha](https://johnbokma.com/blog/2019/04/08/python-re-sub-gotcha.html), John Bokma, April 8, 2019 independent account: replacement text interpreted as escapes and pattern over-escaping causing unwanted backslashes. Historical motivation, not a current application audit.
