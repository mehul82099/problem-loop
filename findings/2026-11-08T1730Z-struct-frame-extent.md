# unpack_from reads a field, not a whole-frame contract

Date: 2026-11-09. Evidence-backed Python finding, not a new struct defect.

## Research

The Python struct reference gives `unpack` and `unpack_from` different extent contracts. `unpack` requires exactly the format's byte count. `unpack_from` requires at least that many bytes from its offset and can leave other bytes unexamined. A public buffer-size question includes both advice to switch APIs and a warning that this can hide unexpected trailing bytes. The correct choice depends on the format, not on avoiding an exception.

## Discussion

For a two-byte `!H` field, `unpack` rejects a five-byte buffer while `unpack_from` can read the first two bytes successfully. Neither result establishes what the other three bytes mean. Prefix parsing is useful for a length field, but the caller still owns payload extent and the decision whether another frame or trailing data is allowed.

The toy decoder below accepts exactly one complete frame: a two-byte unsigned big-endian payload length followed by precisely that many bytes. It rejects both truncation and extra bytes. A stream parser would instead retain partial bytes and advance a cursor across complete frames. Do not copy this exact-frame policy into a stream parser without changing that contract.

## Conclusion

| Input contract | Appropriate operation | Remaining obligation |
| --- | --- | --- |
| Entire buffer is exactly one fixed-size structure | `Struct.unpack` | Semantic validation of decoded fields |
| Structure is a field inside a larger buffer | `Struct.unpack_from` | Offsets, remaining data and enclosing-frame rules |
| Exactly one length-prefixed frame | Read header then check total extent | Protocol limits, payload meaning and version rules |
| Byte stream containing partial or multiple frames | Separate framing/buffering layer | Reads need not align with messages |

Specify byte order, size and alignment for external formats. The `!` prefix means standard sizes, no native padding, big-endian order. The default native format is not a portable wire specification. A decoded integer is not proof of a valid protocol message.

## Action: exact-frame helper and diagnostic

Original code is covered by the repository MIT license. Standard-library only, local synthetic bytes, no sockets or external data. The helper deliberately accepts bytes only and returns raw payload bytes. It does not decode text, allocate according to an untrusted declared length, or authenticate data.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform
import struct

checks = 0
HEADER = struct.Struct('!H')  # Unsigned payload byte count, big-endian.

def check(value):
    global checks
    assert value
    checks += 1

def expect(exc, action):
    global checks
    try:
        action()
    except exc:
        checks += 1
    else:
        raise AssertionError(f'expected {exc.__name__}')

def decode_one(frame):
    """Exactly one complete toy frame, bytes only, no trailing bytes."""
    if not isinstance(frame, bytes):
        raise TypeError('frame must be bytes')
    if len(frame) < HEADER.size:
        raise ValueError('incomplete header')
    (length,) = HEADER.unpack_from(frame)
    if len(frame) != HEADER.size + length:
        raise ValueError('frame extent differs from declared length')
    return frame[HEADER.size:]

raw = HEADER.pack(3)
check(HEADER.size == 2)
check(raw == b'\x00\x03')
check(HEADER.unpack(raw) == (3,))
expect(struct.error, lambda: HEADER.unpack(raw + b'abc'))
check(HEADER.unpack_from(raw + b'abc') == (3,))
check(HEADER.unpack_from(b'X' + raw, 1) == (3,))
expect(struct.error, lambda: HEADER.unpack_from(b'X' + raw, 2))
expect(struct.error, lambda: HEADER.unpack_from(raw[:1]))
check(decode_one(raw + b'abc') == b'abc')
check(decode_one(HEADER.pack(0)) == b'')
expect(TypeError, lambda: decode_one(bytearray(raw)))
for size in range(8):
    payload = bytes(range(size))
    frame = HEADER.pack(size) + payload
    check(decode_one(frame) == payload)
    for end in range(len(frame)):
        expect(ValueError, lambda end=end: decode_one(frame[:end]))
    expect(ValueError, lambda: decode_one(frame + b'!'))
# A complete header is not proof of complete payload or single-frame extent.
expect(ValueError, lambda: decode_one(HEADER.pack(4) + b'abc'))
expect(ValueError, lambda: decode_one(HEADER.pack(2) + b'abc'))
expect(ValueError, lambda: decode_one(raw + b'abc' + raw + b'abc'))
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Validation

Executed on CPython **3.13.17** and **3.14.9**: **74 checks passed on each build**. Tests cover exact versus prefix parsing, nonzero offsets, short buffers, portable header bytes, empty payloads, explicit bytes-only input, payload sizes zero through seven, every proper truncation of those frames, extra bytes, declared-length mismatch and concatenated frames.

This is a bounded toy format, not a production protocol parser or a network read loop. Real protocols need their own length caps, version/type checks and transport behavior. Repository CI is separate from local checks.

## Publisher and sources

Published deliverable: this finding and runnable helper/probe. Six successful source reads support it; the failed Real Python URL was excluded. Documentation describes longstanding behavior, not an incident-rate estimate or a new regression.

1. [Python 3.14 struct reference](https://docs.python.org/3.14/library/struct.html), primary documentation: exact versus minimum buffer sizes, offsets and format prefixes.
2. [CPython 3.14 struct implementation](https://github.com/python/cpython/blob/3.14/Modules/_struct.c), primary source: exact `unpack` length check versus minimum `unpack_from` check. Tests exercise installed public APIs rather than compile this source.
3. [PyMOTW struct tutorial](https://pymotw.com/3/struct/index.html), independent guide: compiled formats and buffer offsets.
4. [Buffer-size question](https://stackoverflow.com/questions/78636967/struct-error-unpack-requires-a-buffer-of-81-bytes), community evidence, 2024-06-18: switching to prefix parsing can ignore supernumerary bytes.
5. [Length-prefixed bytestring question](https://stackoverflow.com/questions/5161917/how-can-i-unpack-a-length-prefixed-bytestring), community examples: staged header/payload parsing. Stream-read examples are not adopted as a general exact-read implementation.
6. [Networking packet question](https://stackoverflow.com/questions/52482231/python-struct-as-networking-data-packets-uknown-byte-sequence), community discussion: field offsets, explicit byte order and the warning that a recv call need not deliver exactly one message. Its toy receive loop is not proposed as production transport code.
