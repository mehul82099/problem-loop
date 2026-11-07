# copyfileobj length is a buffer size, not a copy quota

## Research
A public Python discussion asks for a total-length copying operation distinct from shutil.copyfileobj's current behavior. The Python 3.14 reference is explicit: its length parameter is the buffer size, the source starts at its current position, and completion does not guarantee that the destination has been flushed. A separate CPython discussion describes an application that assumed written data was already visible through another reader.

## Discussion
A positive length controls each read request, not the total amount transferred. In this probe, length=1 still copies all ten source bytes. Setting the source position to three copies the remaining seven, without rewinding. A negative length removes normal chunking; it is not a request to copy zero bytes or to impose a cap. No default buffer size is relied on here.

Buffered destination state is a separate boundary. The controlled io.BufferedWriter below holds the small copied payload above an in-memory raw stream. On return from copyfileobj, that raw stream is still empty; after the caller flushes the writer, it contains the payload. This is an observation about these chosen streams, not a claim that every destination remains empty until flush. Some streams write through, and buffers can fill during copying.

These are documented contracts, not newly discovered defects. An independent copying note corroborates the read/write loop, but its historical default buffer number is not adopted as a current cross-platform constant.

## Conclusion
Name the requirement separately from the tuning knob:

| Requirement | Relevant boundary |
| --- | --- |
| Copy to EOF with bounded per-read requests | A positive length is a buffer choice, not a total quota. |
| Copy a fixed prefix or reject oversized input | Use an explicitly specified counting/framing operation, not length as a quota. |
| Start from the beginning | Position the source deliberately when it is seekable. |
| Let another consumer observe buffered output | Flush or close through the destination's supported interface. |
| Survive crashes or power loss | Flush alone does not establish durable storage. |

This finding does not supply a general limited-copy wrapper. Such a wrapper must define early EOF, short writes, over-limit detection, consumed lookahead and partial destination cleanup. Copying into a destination also does not imply truncating its old tail. Do not present transfer completion as atomic publication, rollback or durability.

## Action: deterministic stream probe
Original code under this repository's MIT license. Ten-byte in-memory input only. Six combinations test positions zero/three and lengths one/four/negative one. The trace inspects requested read sizes, not physical I/O. Run without `-O` so assertions remain active.

```python
import io
import json
import platform
import shutil

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

class Source(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.requests = []
    def read(self, size=-1):
        self.requests.append(size)
        return super().read(size)

payload = b'abcdefghij'
for start in (0, 3):
    for chunk in (1, 4, -1):
        with Source(payload) as source, io.BytesIO() as target:
            source.seek(start)
            result = shutil.copyfileobj(source, target, length=chunk)
            check(target.getvalue() == payload[start:])
            check(source.tell() == len(payload))
            check(result is None)
            check(source.requests and all(size == chunk for size in source.requests))
            check(not source.closed and not target.closed)

with Source(payload) as source, io.BytesIO() as raw:
    writer = io.BufferedWriter(raw, buffer_size=64)
    try:
        shutil.copyfileobj(source, writer, length=3)
        check(raw.getvalue() == b'')
        check(not writer.closed)
        writer.flush()
        check(raw.getvalue() == payload)
        check(not writer.closed)
    finally:
        writer.detach()  # Keep raw open for its owning context manager.

with Source(b'') as source, io.BytesIO(b'existing') as target:
    shutil.copyfileobj(source, target, length=2)
    check(target.getvalue() == b'existing')
    check(source.requests == [2])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 36 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Covers complete remaining input despite tiny positive buffers, current-position behavior, negative-size requests for this BytesIO source, None return, source/destination remaining open, explicit caller flush, and an empty source not clearing an existing destination.
- No disk, network, file metadata, actual read-ahead, memory-pressure experiment, blocking/short write, stream failure, exception cleanup, concurrent use, total-length wrapper, filesystem publication or crash-durability test was performed. A stream can have its own buffering and read/write semantics.
- A negative-size request reads the remainder for this BytesIO implementation. No exact physical I/O call count or universal custom-stream behavior is promised.

## Sources
- [Python 3.14 shutil reference](https://docs.python.org/3.14/library/shutil.html): buffer length, negative length, current position and no flush guarantee.
- [Python 3.14 io reference](https://docs.python.org/3.14/library/io.html): BytesIO, BufferedWriter, flush and detach contracts used in the fixture.
- [CPython 3.14 shutil implementation](https://github.com/python/cpython/blob/3.14/Lib/shutil.py): repeated read(length)/write loop; mutable branch.
- [Public total-length discussion](https://discuss.python.org/t/shutil-copyfileobj-with-length-similar-to-tarfile-copyfileobj/73922): request for fixed-length copying, not an approved replacement API or local test result.
- [Public flush discussion](https://github.com/python/cpython/issues/135648): application confusion about written versus flushed destination state. Commenters' performance figures are not reproduced or used here.
- [Simon Willison's copying note](https://til.simonwillison.net/python/copy-file): independent explanation of the buffered loop; historical default-size snippet not treated as a current guarantee.
