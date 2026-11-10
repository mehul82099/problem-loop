# splitlines chooses more record boundaries than an LF delimiter

Date: 2026-11-10. Tested Python line-boundary policy, not a new string defect.

## Research

Python's versioned string references list eleven boundary sequences for str.splitlines: LF, CR, CRLF, vertical tab, form feed, three information separators, NEL, line separator and paragraph separator. They explicitly distinguish the empty/terminal-boundary behavior from split with a delimiter. The binary sequence reference uses universal-newline splitting instead. An original 2019 question asks for only universal newlines, a 2018 Python forum thread discusses file-line differences, and a 2025 independent note reports the same surprise. Historical tracker 12855 records documentation work, not a current runtime failure.

The broad documentation fetch omitted these later method sections. The exact str.splitlines and bytes.splitlines HTML sections were separately inspected for both versions before drawing these conclusions.

## Discussion

`'a\v b'.splitlines()` produces two strings; the bytes form keeps that vertical tab in one result. A tab is different again: `'a\tb'` remains one line. Do not infer line boundaries from "all whitespace" or from ASCII-looking text alone. Decoding and then choosing a Unicode line API can change record segmentation, not merely the element type.

Empty input gives `[]` with splitlines, but `['']` with split('\n'). A final LF terminates the last line without adding an extra empty line. Two final LFs still represent an intervening empty line. CRLF is one boundary, not two. keepends=True preserves each selected boundary in its result; joining those results reconstructs the exact already-available string in this probe.

| Intended format | Explicit choice | Boundary |
| --- | --- | --- |
| Unicode text lines under Python's listed rules | str.splitlines | Splits on more than CR/LF/CRLF |
| Exact LF-delimited fields | split('\n') | Retains terminal empty field and leaves CR/data intact |
| Binary universal-newline records | bytes.splitlines | Does not apply all Unicode string boundaries |

These choices are not substitutes for a protocol parser. For quoted CSV, for example, physical line splitting alone does not define records. Do not encode arbitrary text solely to change line semantics without a deliberate encoding/error policy.

## Conclusion

Define boundary recognition, empty input and terminal delimiters together. keepends preserves boundaries that the selected API recognizes; it does not decide which characters should count as data in an application.

The earlier text-newline finding explains normalization before splitlines, the split finding covers whitespace versus literal delimiters, and readlines-hint uses splitlines as an oracle only on a limited CR/LF sample. Those overlaps are acknowledged. This increment tests the string/binary boundary set and terminal-field policy directly. It does not claim all readlines and splitlines calls are interchangeable or recover original file bytes after decoding.

## Action

Original standard-library-only diagnostic under this repository's MIT license. Actual CPython 3.13.17 and 3.14.9 each passed 6,853 checks over 1,365 toy strings plus selected documented-boundary examples. The exhaustive grid uses `a`, CR, LF and vertical tab at lengths 0..5. A simple explicit scanner gives CRLF priority and suppresses a terminal extra field; both stripped and kept boundaries are checked. Each documented single-character boundary also has a direct example.

The bytes oracle masks vertical tab to an otherwise absent non-boundary byte for this tiny alphabet, then restores it. Latin-1 is used only as a one-to-one mapping for these sample code points, not an encoding recommendation. No full Unicode scan or file I/O. Run without optimization so assertions remain active.

```python
from itertools import product
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

# Scanner with explicit CRLF priority and the documented str boundaries.
BOUNDARIES = '\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029'
def scan(text, keepends=False):
    result = []
    start = i = 0
    while i < len(text):
        if text[i] not in BOUNDARIES:
            i += 1
            continue
        end = i + (2 if text[i:i+2] == '\r\n' else 1)
        result.append(text[start:end if keepends else i])
        start = i = end
    if start < len(text):
        result.append(text[start:])
    return result

check(''.splitlines() == [])
check(''.split('\n') == [''])
check('a\n'.splitlines() == ['a'])
check('a\n'.split('\n') == ['a', ''])
check('a\n\n'.splitlines() == ['a', ''])
check('a\v b'.splitlines() == ['a', ' b'])
check(b'a\v b'.splitlines() == [b'a\v b'])
check('a\tb'.splitlines() == ['a\tb'])
for boundary in BOUNDARIES:
    check(('a' + boundary + 'b').splitlines() == ['a', 'b'])
    check(('a' + boundary).splitlines(True) == ['a' + boundary])

cases = 0
for size in range(6):
    for chars in product('a\r\n\v', repeat=size):
        text = ''.join(chars)
        check(text.splitlines() == scan(text))
        check(text.splitlines(True) == scan(text, True))
        check(''.join(text.splitlines(True)) == text)
        # Latin-1 identity encoding here: bytes only split CR, LF and CRLF.
        raw = text.encode('latin1')
        expected_bytes = [part.encode('latin1') for part in scan(text.replace('\v', '\x00'))]
        expected_bytes = [part.replace(b'\x00', b'\v') for part in expected_bytes]
        check(raw.splitlines() == expected_bytes)
        check(b''.join(raw.splitlines(True)) == raw)
        cases += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'toy_strings': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Exact published bytes are compared with the tested draft; committed code is extracted and rerun on both named builds.
- Synthetic in-memory strings and bytes only. No user documents, files, network, encoding detection or streaming/chunk-boundary parser.
- This is not Unicode line-layout conformance, visual wrapping, a CSV reader, protocol validation or a resource-bound guarantee. No normalization/decoding round-trip claim beyond the tested in-memory joins.
- Historical proposals and reported application concerns are not evidence of an unresolved current vulnerability; none is asserted here.

## Sources

1. Python 3.13 string/binary reference, exact method sections inspected: https://docs.python.org/3.13/library/stdtypes.html#str.splitlines
2. Python 3.14 string/binary reference, exact method sections inspected: https://docs.python.org/3.14/library/stdtypes.html#str.splitlines
3. Historical documentation issue 12855: https://bugs.python.org/issue12855
4. Independent October 8, 2025 note on extra splitlines boundaries: https://yossarian.net/til/post/python-s-splitlines-does-a-lot-more-than-just-newlines/
5. Original August 22, 2019 universal-newline-only question: https://stackoverflow.com/questions/57600719/split-a-unicode-string-only-at-universal-newlines-n-r-r-n
6. Python forum October 2018 line-boundary discussion: https://discuss.python.org/t/changing-str-splitlines-to-match-file-readlines/174
