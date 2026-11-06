# Text decoding can normalize newlines before splitlines ever sees them

Date: 2026-11-06. A documented text-I/O boundary, not a new pathlib defect.

## Research

The [Python 3.14 pathlib reference](https://docs.python.org/3.14/library/pathlib.html) says read_text parameters follow open semantics, and notes that its newline parameter was added in Python 3.13. The [open reference](https://docs.python.org/3.14/library/functions.html) and [io reference](https://docs.python.org/3.14/library/io.html) explain that newline=None translates CR, LF and CRLF input endings to LF. With newline='', universal newline recognition remains enabled, but endings are returned untranslated.

The [2023 CPython pull request adding the parameter](https://github.com/python/cpython/pull/110880) includes mixed-ending test cases and explains that read-side normalization is not restricted to Windows. A [real project's newline-preservation discussion](https://github.com/mtkennerly/poetry-dynamic-versioning/pull/157) describes asymmetric read_text/write_bytes behavior. An [independent file-I/O tutorial](https://veit.github.io/python-basics-tutorial/save-data/files-directories.html) discusses line-ending options, but its platform-specific read-normalization phrasing is not adopted: the primary docs describe universal input handling, which this Linux probe confirms.

## Discussion

If read_text already translated CRLF and bare CR to LF, splitlines(keepends=True) cannot reconstruct the original endings. Keeping the endings of the returned string is different from preserving the file's original bytes. Writing that normalized string as UTF-8 bytes does not undo the earlier translation.

This probe creates one tiny UTF-8 file with mixed endings. Default read_text returns only LF endings. Reading with newline='' retains the original endings; writing that preserved text with newline='' reproduces the exact bytes for this controlled encoding and input. The source remains unchanged throughout.

## Conclusion

Choose whether a text transformation should normalize endings or preserve them. On Python 3.13+, read_text(newline='') makes the latter intent explicit. On older versions, use Path.open with newline='' and read the stream. If exact byte identity matters beyond this controlled UTF-8 case, use binary I/O or define encoding and error handling carefully. Preserving newline characters alone is not a universal byte-round-trip guarantee.

## Action

Original MIT-licensed probe for Python 3.13+. It creates only two owned files inside a temporary directory, fixes encoding explicitly, and passes newline='' on output to avoid platform-dependent write translation. No existing documents are modified.

```python
import json
import platform
from pathlib import Path
from tempfile import TemporaryDirectory

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

raw = b'alpha\r\nbeta\rgamma\n'
with TemporaryDirectory() as directory:
    source = Path(directory) / 'source.txt'
    source.write_bytes(raw)
    normalized = source.read_text(encoding='utf-8')
    check(normalized == 'alpha\nbeta\ngamma\n')
    check(source.read_text(encoding='utf-8', newline=None) == normalized)
    preserved = source.read_text(encoding='utf-8', newline='')
    check(preserved == 'alpha\r\nbeta\rgamma\n')
    check(preserved.encode('utf-8') == raw)
    check(source.read_bytes().decode('utf-8') == preserved)
    with source.open('r', encoding='utf-8', newline='') as stream:
        check(stream.read() == preserved)
    check(''.join(normalized.splitlines(keepends=True)) != preserved)
    check(''.join(preserved.splitlines(keepends=True)) == preserved)
    output = Path(directory) / 'output.txt'
    output.write_text(preserved, encoding='utf-8', newline='')
    check(output.read_bytes() == raw)
    output.write_text(normalized, encoding='utf-8', newline='')
    check(output.read_bytes() == b'alpha\nbeta\ngamma\n')
    check(output.read_bytes() != raw)
    check(source.read_bytes() == raw)

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 12 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Checks cover default/explicit normalization, untranslated reads through both APIs, splitlines reconstruction limits, controlled byte round-trip, and unchanged source bytes. Other encodings, invalid input, BOMs, platform-specific default writes and other OSs are not tested. Repository CI is separate.

## Publisher

One evidence-backed finding with a bounded executable probe. No application formatter patch or production file conversion.
