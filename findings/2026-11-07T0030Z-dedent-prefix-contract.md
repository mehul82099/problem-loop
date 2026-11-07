# dedent removes a shared prefix, not visual columns

## Research
textwrap.dedent removes common leading whitespace across lines. Its documentation explicitly says tabs and spaces are both whitespace but are not equal. An unindented nonblank first line can leave later indented lines unchanged. Public questions often recommend inspect.cleandoc instead, but that function has a different contract, not a universally better one.

## Discussion
A tab and eight spaces may display at the same column under one tab-stop convention, yet they do not form a common character prefix. Explicit expandtabs before dedent chooses a column convention and changes tab characters throughout the string, including interior content. A different tab size can preserve a different amount of relative indentation.

cleandoc expands tabs, treats the first line specially, removes common indentation from subsequent lines and removes empty boundary lines. dedent normally preserves boundary newlines and interior tabs. Neither is a syntax-aware formatter for configuration, code or tabular data. Selecting one because its sample output looks tidier can silently change meaningful content.

## Conclusion
For a uniformly indented literal whose relative spacing and boundary newlines matter, use dedent with a consistent whitespace prefix. For docstring cleanup, choose cleandoc when its first-line, tab-expansion and boundary-line behavior is intended. Expand tabs only under an explicit tab-size policy. This is documented longstanding behavior, not a new defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory strings only, with escaped tabs/newlines so the exact input is visible. Run without Python optimization so assertions remain enabled.

```python
from inspect import cleandoc
from textwrap import dedent
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

check(dedent('    alpha\n      beta\n') == 'alpha\n  beta\n')
check(dedent('alpha\n    beta\n') == 'alpha\n    beta\n')
check(cleandoc('alpha\n    beta\n') == 'alpha\nbeta')
check(dedent('\n    alpha\n    beta\n') == '\nalpha\nbeta\n')
check(cleandoc('\n    alpha\n    beta\n') == 'alpha\nbeta')
check(dedent('\talpha\n\tbeta\n') == 'alpha\nbeta\n')
mixed = '\talpha\n        beta\n'
check(dedent(mixed) == mixed)  # Same visual column, different prefix.
check(dedent(mixed.expandtabs(8)) == 'alpha\nbeta\n')
check(dedent(mixed.expandtabs(4)) == 'alpha\n    beta\n')
check(dedent('  \talpha\n    beta\n') == '\talpha\n  beta\n')
check(dedent('    a\tb\n    c\td\n') == 'a\tb\nc\td\n')
check(cleandoc('    a\tb\n    c\td\n') == 'a   b\nc   d')
check(dedent('    alpha\n  \t\n    beta\n') == 'alpha\n\nbeta\n')
check(dedent('alpha\n  beta  \n') == 'alpha\n  beta  \n')
check(dedent('') == '')
check(dedent('    ') == '')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 16 checks passed on CPython 3.13.17 and 3.14.9.
- Covers relative indentation, first-line effects, leading/trailing newlines, shared tabs, mixed prefixes, two expandtabs policies, interior tabs, ASCII space/tab blank lines, trailing spaces and empty input.
- Python 3.14 documents a change to normalization of whitespace-only blank lines. This probe intentionally uses only ASCII spaces/tabs for that case and does not claim identical behavior for every whitespace character across versions.
- No non-ASCII whitespace, CRLF normalization, source parser, configuration format, terminal rendering, TextWrapper options, performance or production document was tested. Exact string checks are not a visual tab-width measurement.

## Sources
- [Python 3.14 textwrap](https://docs.python.org/3.14/library/textwrap.html): dedent prefix contract, tabs/spaces distinction, whitespace-only-line note and 3.14 change. TextWrapper tab options are not dedent options.
- [Python 3.14 inspect](https://docs.python.org/3.14/library/inspect.html): cleandoc first-line, tab-expansion and boundary-line semantics.
- [PEP 257](https://peps.python.org/pep-0257/): docstring indentation conventions; not a general text-format contract.
- [Multiline string indentation question](https://stackoverflow.com/questions/1412374/how-to-remove-extra-indentation-of-python-triple-quoted-multi-line-strings): public dedent/cleandoc comparison; recommendations evaluated against current docs rather than adopted wholesale.
- [Python-list tab discussion](https://mail.python.org/pipermail/python-list/2006-December/411398.html): historical common-whitespace explanation; not evidence of a new regression.
- [CPython issue 59250](https://github.com/python/cpython/issues/59250): historical whitespace-consistency discussion; older implementation statements are not asserted as current and its non-ASCII cases are not tested here.
