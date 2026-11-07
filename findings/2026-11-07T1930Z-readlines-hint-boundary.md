# readlines(hint) is a batch hint, not a maximum line size

## Research
A public Python question asks why `readlines(n)` does not return n lines or behave like a strict size bound. The current io reference says reading stops after the accumulated size of returned lines exceeds the hint. It also says a hint of zero or less, or None, has no effect. A historical documentation issue specifically records confusion about zero returning the whole stream.

## Discussion
A full line can be larger than the hint. In the small probe below, `readlines(1)` returns a 33-item line from both a text and a binary in-memory stream. That does not violate the contract. Iterating line by line avoids constructing a list of all lines, but still materializes each complete line; it is not itself a maximum-line-size policy.

The units matter too. Text I/O returns characters; binary I/O returns bytes. Three characters can occupy five UTF-8 bytes in this probe. Neither a character count nor a returned payload size describes total resident memory, decoder state or underlying I/O read-ahead.

An independent tutorial describes the hint in byte terms and as limiting lines returned. Read that against the official bytes/characters contract, not as a universal byte cap for text streams. Older community answers discuss Python 2 internal buffers; their specific buffer sizes are not treated as current Python 3 guarantees.

This is documented behavior, not a new defect. The prior repository newline finding concerns decoding and normalization; this one concerns batching versus record-size limits.

## Conclusion
Choose the boundary before choosing the method:

| Need | Approach | Caveat |
| --- | --- | --- |
| Process complete lines without a whole-file list | Iterate the stream | A single line may still be large. |
| Batch complete lines approximately | `readlines(hint)` | Not a strict line count, payload cap or memory cap. |
| Reject overlong text lines | Bounded `readline(limit + 1)` and a length check | Define whether terminators count and what happens after rejection. |
| Enforce a byte-level protocol or transport limit | Apply its framing and size rules at the byte boundary | A text helper is not that parser. |

The small helper here accepts a positive integer character limit, counts any returned newline characters toward it, and rejects rather than yields an oversized fragment. It is a streaming check: earlier valid lines may already have been yielded, and the failing read has consumed part of the bad line. Do not retry from that position as if it began a fresh record. Discard the stream or use an explicitly designed recovery policy. No rollback or whole-input validation is provided.

## Action: bounded demonstration
Original code under this repository's MIT license. In-memory examples only; no large file, network input or real memory-pressure experiment. Run without `-O` so assertions remain active. The helper assumes a standard text stream and a positive integer limit, not an arbitrary custom object's read contract.

```python
import io
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def bounded_lines(stream, max_chars):
    # Text-only contract; newline characters count toward the limit.
    if max_chars < 1:
        raise ValueError('max_chars must be positive')
    while True:
        line = stream.readline(max_chars + 1)
        if not line:
            return
        if len(line) > max_chars:
            raise ValueError('line exceeds character limit')
        yield line

text = 'x' * 32 + '\nnext\n'
for factory, data, first in (
    (io.StringIO, text, 'x' * 32 + '\n'),
    (io.BytesIO, text.encode(), b'x' * 32 + b'\n'),
):
    with factory(data) as stream:
        batch = stream.readlines(1)
        check(batch == [first])
        check(len(batch[0]) == 33)
        check(stream.readline() == (b'next\n' if isinstance(data, bytes) else 'next\n'))
        check(stream.readlines(1) == [])
    with factory(data) as stream:
        fragment = stream.readline(4)
        check(len(fragment) == 4)
        check(fragment + stream.read() == data)
    for hint in (0, -1):
        with factory(data) as stream:
            check(stream.readlines(hint) == data.splitlines(keepends=True))

with io.StringIO('éé\nz\n') as stream:
    line = stream.readlines(1)[0]
    check(len(line) == 3)
    check(len(line.encode('utf-8')) == 5)
check(list(bounded_lines(io.StringIO('ab\ncd'), 3)) == ['ab\n', 'cd'])
check(list(bounded_lines(io.StringIO(''), 3)) == [])
check(list(bounded_lines(io.StringIO('\n'), 1)) == ['\n'])
stream = io.StringIO('ok\nlonger\n')
iterator = bounded_lines(stream, 3)
check(next(iterator) == 'ok\n')
caught = False
try:
    next(iterator)
except ValueError:
    caught = True
check(caught)
check(stream.tell() == 7)  # The failed read consumed a prefix of the long line.
check(stream.read() == 'er\n')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 25 checks passed on CPython 3.13.17 and 3.14.9, each supervised by a 15-second shell timeout.
- Covers complete-line overshoot, bounded-read fragments, remaining input and EOF, zero/negative hints, character versus encoded byte lengths, accepted boundary-length lines, final unterminated lines, empty/blank input and rejection after a valid prefix. The original source payload is only 38 characters.
- No specific batch size is promised for other I/O implementations. The helper does not bound total input, number of records, decoder buffers, resident memory or wall-clock time. It does not cover custom streams, nonblocking I/O, alternate newline modes, invalid encodings, byte framing or concurrent consumers.

## Sources
- [Python 3.14 io reference](https://docs.python.org/3.14/library/io.html): readlines hint, nonpositive values, text readline character bound and binary/text distinctions.
- [Python 3.14 input/output tutorial](https://docs.python.org/3.14/tutorial/inputoutput.html): iteration, read/readline/readlines and text-versus-binary units.
- [CPython 3.14 IOBase implementation](https://github.com/python/cpython/blob/3.14/Modules/_io/iobase.c): appends a line before comparing accumulated length against hint; mutable branch, subclasses can have their own implementations.
- [Historical documentation issue 43126](https://bugs.python.org/issue43126): zero-hint confusion and documentation change, not an unresolved current bug.
- [Public readlines behavior question](https://stackoverflow.com/questions/14541010/pythons-function-readlinesn-behavior): real confusion about approximate batching; old buffer numbers are not adopted.
- [Independent readlines tutorial](https://www.w3schools.com/python/ref_file_readlines.asp): common hint description; its byte-only wording is limited here by the official text-stream contract and local probe.
