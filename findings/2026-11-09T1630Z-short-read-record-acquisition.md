# A short byte read is not a complete-record boundary

Date: 2026-11-09. Evidence-backed Python read-contract finding, not a new networking defect.

## Research

Python's versioned socket references describe recv's size as a maximum, not a promise to fill it. The socket HOWTO says callers must account for partial transfers and choose an application message format. The io reference similarly permits short raw reads, while higher-level buffered interfaces have different retry behavior. Do not generalize one low-level contract to every object with a read method.

A July 2013 public receive question reports increasing a receive buffer without obtaining a whole message. Its accepted answer describes explicit framing and repeated receives; another answer incorrectly treats any short result as the end. The official contract and a later answer distinguish a short nonempty result from EOF. An independent buffering lesson explains a second policy choice: over-read into a persistent buffer and retain the next record's bytes. The toy here instead requests only the missing byte count, so it does not over-read.

## Discussion

A stand-in blocking reader contains abcdef in pieces a, bc and def. Its first read(6) returns a. Five more bytes still remain. Returning fewer bytes than requested is therefore not evidence of the end of this record or stream. No live network is needed to test the caller's assumption deterministically.

The helper's narrow callback contract is explicit: a positive request returns plain bytes no longer than requested, with an empty bytes result meaning final EOF. It retries short nonempty results until the requested count is reached. It raises IncompleteRead with the consumed prefix and requested count on early EOF. A zero request makes no callback call and returns empty bytes, so that result is not evidence of EOF.

| Boundary | Chosen toy behavior |
| --- | --- |
| Short nonempty chunk | Continue for remaining bytes |
| Final EOF before count | Raise, preserving partial bytes in exception |
| Exact count reached | Return it; leave later bytes in reader |
| Zero requested | Return empty without touching reader |
| None, text or oversized callback result | Reject contract violation |

Failure is consuming, not transactional. An incomplete-record exception does not rewind the reader, and blindly retrying the whole request can lose framing. Other callback exceptions propagate; this helper does not preserve accumulated bytes on every failure or resume nonblocking operations.

## Conclusion

Separate byte acquisition from record parsing. Decide the protocol's length, delimiter or connection-end policy; then handle short reads under the actual interface contract. Bigger buffers do not create message boundaries. If a reader deliberately fetches beyond the current record, it needs persistent leftover storage, which this exact-request helper avoids rather than implements.

The 0..256 limit is only a teaching bound, not a recommended protocol limit. It limits returned data in this example, not how long a callback can block. There is no timeout, cancellation, authentication or generic transport-safety guarantee. Use the real transport's lifecycle and deadline facilities when integrating an application.

The earlier struct-frame finding mentions reads not aligning with messages but only parses an already-complete buffer. This increment acknowledges that overlap and adds tested acquisition behavior, fragmentation, consuming EOF and zero-request semantics. It does not add another binary-format parser.

## Action

Original code under this repository's MIT license. Deterministic in-memory stand-in and BytesIO only. No sockets, files, threads or external input. Run without Python optimization so assertions remain enabled.

```python
import io
import itertools
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class IncompleteRead(EOFError):
    def __init__(self, partial, expected):
        super().__init__('EOF before requested count')
        self.partial = partial
        self.expected = expected

def read_exact(read, n):
    """Toy blocking bytes callback: <= requested bytes; b'' means final EOF."""
    if type(n) is not int or not 0 <= n <= 256:
        raise ValueError('toy count must be a plain int in 0..256')
    result = bytearray()
    while len(result) < n:
        remaining = n - len(result)
        chunk = read(remaining)
        if type(chunk) is not bytes or len(chunk) > remaining:
            raise TypeError('reader violated blocking bytes contract')
        if not chunk:
            raise IncompleteRead(bytes(result), n)
        result.extend(chunk)
    return bytes(result)

class Fragments:
    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.calls = []

    def read(self, n):
        self.calls.append(n)
        if not self.chunks:
            return b''
        part = self.chunks[0][:n]
        rest = self.chunks[0][n:]
        if rest:
            self.chunks[0] = rest
        else:
            self.chunks.pop(0)
        return part

    def remaining(self):
        return b''.join(self.chunks)

cases = 0
for size in range(1, 9):
    payload = bytes(range(size))
    # All contiguous nonempty fragmentation patterns for this payload.
    for cuts in itertools.product((False, True), repeat=size-1):
        points = [0] + [i+1 for i, cut in enumerate(cuts) if cut] + [size]
        chunks = [payload[a:b] for a, b in zip(points, points[1:])]
        for n in range(size + 2):
            cases += 1
            reader = Fragments(chunks)
            if n <= size:
                check(read_exact(reader.read, n) == payload[:n])
                check(reader.remaining() == payload[n:])
                check(bool(reader.calls) == (n > 0))
            else:
                try:
                    read_exact(reader.read, n)
                except IncompleteRead as exc:
                    check(exc.partial == payload)
                    check(exc.expected == n)
                    check(reader.remaining() == b'')
                else:
                    raise AssertionError('partial record accepted')
            check(all(0 < request <= n for request in reader.calls))

reader = Fragments([b'a', b'bc', b'def'])
check(reader.read(6) == b'a')  # One short result is not EOF.
check(read_exact(reader.read, 5) == b'bcdef')
check(read_exact(io.BytesIO(b'abNEXT').read, 2) == b'ab')
reader = io.BytesIO(b'abNEXT')
check(read_exact(reader.read, 2) == b'ab')
check(reader.read() == b'NEXT')
for invalid in (-1, 257, True, 1.0, '2'):
    try:
        read_exact(lambda n: b'', invalid)
    except ValueError:
        check(True)
    else:
        raise AssertionError('bad count accepted')
for bad in (None, 'x', b'ab'):
    try:
        read_exact(lambda n: bad, 1)
    except TypeError:
        check(True)
    else:
        raise AssertionError('bad reader accepted')
try:
    read_exact(io.BytesIO(b'').read, 1)
except IncompleteRead as exc:
    check(exc.partial == b'' and exc.expected == 1)
else:
    raise AssertionError('empty stream accepted')
print(json.dumps({'checks': checks, 'cases': cases,
                  'python': platform.python_version(), 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**: **9,226 checks passed per build**. The 2,303 grid cases cover all contiguous nonempty fragmentations of byte payloads of lengths 1..8, requesting counts from zero through one beyond available bytes. Checks compare exact prefix results, unconsumed suffixes, no-read zero behavior, early-EOF partial evidence and request bounds. Additional cases cover one-shot short reads, BytesIO suffix retention, invalid counts/read results and initial EOF.

The stand-in deliberately returns at most the requested bytes and never yields temporary empty chunks. No real socket timing, raw OS file, datagram semantics, nonblocking None/readiness protocol, exceptions after partial progress, concurrent reader, send side, buffering-performance comparison or production protocol was tested. A callback can still block indefinitely; the fixture never does.

## Publisher

One bounded acquisition-contract increment. Full targeted repository search and nearby struct finding inspected. Shared message-boundary warning is disclosed above; no claim of newly discovered stream behavior is made.

## Sources

1. [Python 3.13 socket.recv](https://docs.python.org/3.13/library/socket.html#socket.socket.recv), primary documentation: maximum receive count and empty result. Exact method section inspected separately from the broad page.
2. [Python 3.14 socket.recv](https://docs.python.org/3.14/library/socket.html#socket.socket.recv), primary documentation: same contract.
3. [Python 3.14 io reference](https://docs.python.org/3.14/library/io.html), primary documentation: raw short reads, nonblocking None and buffered-interface differences.
4. [Python 3.14 socket HOWTO](https://docs.python.org/3.14/howto/sockets.html), official tutorial: partial transfers, framing, bounded remaining-byte requests and leftover-buffer considerations.
5. [Python Socket Receive Large Amount of Data](https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data), July 16, 2013 community question: buffer-size confusion and conflicting receive recipes. Short-read-as-EOF advice is explicitly not adopted; no source network commands were run.
6. [Keep the Leftover Bytes](https://learn.python.land/lesson/networks-with-python/bytes-arrive-in-pieces/keep-the-leftover-bytes), independent Python Land lesson: persistent buffer ownership for over-reading. Its buffered strategy is context, not code copied into the exact-request helper. No publication date shown.
