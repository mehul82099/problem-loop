# Regex pos is a search start, not a new string boundary

## Research
Public Python questions compare compiled-pattern pos/endpos arguments with slicing and find different anchor and lookaround results. Python's re reference explicitly says pos is not completely equivalent to slicing: the real start of the string does not move. endpos instead acts as an effective end of the searched string.

## Discussion
A compiled pattern's search(text, pos) can start looking at pos without making a caret anchor match there. A lookbehind can still inspect characters before pos. Slicing creates a different string, removes that left context, and gives returned spans a different coordinate system. Match objects from the bounded original retain original-string coordinates.

The right boundary is different: endpos prevents lookahead from inspecting characters beyond that boundary and lets an end anchor match the effective end. This is documented behavior, not a new defect. MULTILINE changes the meaning of caret to include line starts; it does not turn every pos into a line start.

## Conclusion
For a token that must start exactly at a cursor, use a compiled pattern's match(text, pos) rather than adding a caret and assuming it means the cursor. Use fullmatch with bounds when the entire bounded region must match, remembering that left context can still affect lookbehind. Slice explicitly when an isolated substring is the intended input and account for offset changes. The choice is semantic, not a performance recommendation here.

## Action: executable probe
Original code under this repository's MIT license. Small built-in re patterns and short strings only. Run without Python optimization so assertions remain enabled.

```python
import re
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

text = 'ab'
check(re.compile('^b').search(text, 1) is None)
check(re.compile('^b').search(text[1:]).span() == (0, 1))
check(re.compile(r'\Ab').search(text, 1) is None)
check(re.compile(r'\Ab').search(text[1:]).span() == (0, 1))
check(re.compile('b').match(text, 1).span() == (1, 2))
check(re.compile('^b').match(text, 1) is None)
check(re.compile('b').match(text, 0) is None)

pattern = re.compile('(?<=a)b')
match = pattern.match(text, 1, 2)
check(match.group() == 'b')
check(match.span() == (1, 2))
check(match.pos == 1 and match.endpos == 2)
check(match.string is text)
check(pattern.match(text[1:]) is None)

check(re.compile('a(?=b)').match(text).span() == (0, 1))
check(re.compile('a(?=b)').match(text, 0, 1) is None)
check(re.compile('a$').search(text, 0, 1).span() == (0, 1))
check(re.compile('a$').search(text) is None)

lines = 'a\nb'
check(re.compile('^b', re.MULTILINE).search(lines, 1).span() == (2, 3))
check(re.compile('^b').search(lines, 1) is None)
check(re.compile('b').fullmatch('abc', 1, 2).span() == (1, 2))
check(re.compile('b').fullmatch('abc', 1, 3) is None)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9.
- Covers caret and absolute-start anchors, cursor match, lookbehind before pos, original match coordinates, lookahead/endpos, effective end anchor, MULTILINE and bounded fullmatch.
- No third-party regex engine, JavaScript equivalence, Unicode/bytes variants, adversarial patterns, performance benchmark, or complete tokenizer/parser was tested. This is distinct from the earlier repeated-capture finding.

## Sources
- [Python 3.14 re](https://docs.python.org/3.14/library/re.html): current pos/endpos, anchors and match/fullmatch definitions.
- [Python 3.13 re](https://docs.python.org/3.13/library/re.html): corresponding reference semantics.
- [Substring versus bounds question](https://stackoverflow.com/questions/30999922/why-is-regex-search-in-substring-not-completely-equivalent-to-slicing-the-strin): original comparison and cursor-match explanation; older buffer advice not adopted.
- [Historical issue 13998](https://bugs.python.org/issue13998): lookbehind-before-pos discussion, closed without a change, not a current regression claim.
- [Python discussion on endpos](https://discuss.python.org/t/python-re-lookahead-dont-ignore-endpos/56098): concrete boundary confusion and documented resolution.
- [Regex surprises guide](https://learnbyexample.github.io/python-regex-surprises/): independent anchor-versus-slicing explanation.
