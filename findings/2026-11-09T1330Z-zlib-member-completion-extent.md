# Decompressed bytes are not proof of a complete, exact input member

Date: 2026-11-09. Evidence-backed Python zlib contract finding, not a new decoder defect.

## Research

Python's versioned zlib references distinguish three decompressor states. eof records reaching the compressed stream's end. unused_data holds bytes after that end. unconsumed_tail holds input not processed because an output limit was reached. Those states answer different questions.

A historical Python issue reports apparently valid output from a stream that never reached Z_STREAM_END. A public partial-file question demonstrates that decompressobj can recover output from incomplete input. That recovery can be useful, but it does not establish complete stream validation. The upstream zlib manual separately describes output progress and successful stream end. Its currently fetched manual is labelled 1.4; the actual runtime used here is 1.3.2, so no new-version features are assumed.

## Discussion

The bounded probe generates four ordinary zlib-wrapped members. Removing just the final trailer byte still lets a decompressor object return the entire original payload on both tested builds. eof remains false. Even flushing that object and receiving no more output does not turn this incomplete member into a complete one.

Conversely, appending arbitrary tail bytes or a second complete zlib member allows one-shot zlib.decompress to return the first payload without rejecting the tail on these builds. A decompressor object exposes that tail through unused_data. The input protocol must decide whether extra members or other bytes are allowed; neither silently dropping them nor automatically processing them is a universal policy.

| Observation | What it establishes here | What it does not establish |
| --- | --- | --- |
| Some or all expected output returned | Decompression made progress | End marker/trailer has arrived |
| eof true | First compressed member reached its end | No extra bytes follow |
| unused_data nonempty | Bytes remain after the first member | Whether the enclosing protocol permits them |
| unconsumed_tail nonempty under max_length | Input remains to process after output limiting | A completed member or a forbidden trailing record |

## Conclusion

Track stream completion and input extent separately from output content. An application requiring exactly one complete member must check its completion and trailing-byte policy, after accounting for input still pending under output limits. Do not use output equality, empty flush output or a successful one-shot return as a substitute for that whole contract.

The probe illustrates states, not a generic decoder. It only processes tiny locally generated fixtures. Its unrestricted decompression calls are not safe resource limits for arbitrary input, and a per-call max_length is not a total output or CPU budget. No authentication, decompression-bomb resistance or production-file recovery guarantee is claimed.

## Action

Original code under this repository's MIT license. In-memory bytes only; no files or network. Run without Python optimization so assertions remain enabled.

```python
import json
import platform
import zlib

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

payloads = (b'', b'a', b'abc' * 30, bytes(range(256)))
split_cases = 0
truncated_cases = 0
for payload in payloads:
    stream = zlib.compress(payload)
    check(zlib.decompress(stream) == payload)
    # Extra bytes are not part of the first zlib member.
    for tail in (b'TAIL', zlib.compress(b'second')):
        check(zlib.decompress(stream + tail) == payload)
        d = zlib.decompressobj()
        check(d.decompress(stream + tail) == payload)
        check(d.eof)
        check(d.unused_data == tail)
        check(d.unconsumed_tail == b'')
    # Every split of this complete member succeeds in two feeds.
    for split in range(len(stream) + 1):
        split_cases += 1
        d = zlib.decompressobj()
        out = d.decompress(stream[:split])
        out += d.decompress(stream[split:])
        check(out == payload)
        check(d.eof)
        check(d.unused_data == b'')
        check(d.unconsumed_tail == b'')
    # Every strict prefix is incomplete, though streaming may yield bytes.
    for end in range(len(stream)):
        truncated_cases += 1
        prefix = stream[:end]
        d = zlib.decompressobj()
        out = d.decompress(prefix)
        check(payload.startswith(out))
        check(not d.eof)
        check(d.unused_data == b'')
        try:
            zlib.decompress(prefix)
        except zlib.error:
            check(True)
        else:
            raise AssertionError('truncated member accepted by one-shot API')
    # Removing only the last trailer byte can leave all output available.
    d = zlib.decompressobj()
    check(d.decompress(stream[:-1]) == payload)
    check(not d.eof)
    check(d.flush() == b'')
    check(not d.eof)

# Output-limited pending input is a separate state from post-member data.
payload = b'abcdefghij' * 20
stream = zlib.compress(payload)
d = zlib.decompressobj()
out = d.decompress(stream, max_length=7)
check(len(out) == 7)
check(not d.eof)
check(d.unused_data == b'')
check(bool(d.unconsumed_tail))
# Bounded fixture: stop with failure rather than loop without a bound.
for _ in range(len(payload) + 1):
    if d.eof:
        break
    out += d.decompress(d.unconsumed_tail, max_length=7)
check(d.eof)
check(out == payload)
check(d.unused_data == b'')
check(d.unconsumed_tail == b'')
print(json.dumps({'checks': checks, 'split_cases': split_cases,
                  'truncated_cases': truncated_cases,
                  'python': platform.python_version(),
                  'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION, 'status': 'passed'}))
```

### Verification and limits

Executed on CPython **3.13.17** and **3.14.9**, each reporting zlib runtime **1.3.2**: **2,468 checks passed per build**. Four payloads cover empty, one-byte, repeated text and all byte values. Every two-feed split is checked (302 cases), as is every strict compressed prefix (298 cases). Separate fixtures cover first-member tails, concatenated zlib members, full output from a missing trailer byte, flush not proving completion, and a bounded max_length drain loop.

No compressed byte representation is asserted stable across library versions. No gzip/raw-deflate format, dictionaries, malformed checksums, huge input, files, multi-member decoding implementation, asynchronous input, timing or other Python/zlib builds were tested. The old partial-file answer is motivation, not code adopted as a complete decoder.

## Publisher

One bounded finding and standalone probe. Full targeted repository search found other compression topics but no prior zlib eof/unused_data/unconsumed_tail contract finding. The earlier struct-frame finding concerns fixed binary record extent, not compressed stream completion and pending output state.

## Sources

1. [Python 3.13 zlib reference](https://docs.python.org/3.13/library/zlib.html), primary documentation: decompressor eof, unused_data, unconsumed_tail and output limits.
2. [Python 3.14 zlib reference](https://docs.python.org/3.14/library/zlib.html), primary documentation: same states and one-shot API.
3. [Python issue 8672](https://bugs.python.org/issue8672), May 2010 historical report: output recovery versus reaching Z_STREAM_END; regression-test discussion, not a claim of a current unresolved bug.
4. [How to inflate a partial zlib file](https://stackoverflow.com/questions/20620374/how-to-inflate-a-partial-zlib-file/20624942), December 16, 2013 community question/answers: partial recovery through decompressobj. Historical Python 2 code is not adopted as a modern complete decoder.
5. [zlib manual](https://www.zlib.net/manual.html), upstream documentation labelled 1.4 when fetched: inflate progress and stream-end distinction. Tested runtime is explicitly 1.3.2; no claim to have tested 1.4.
6. [CPython issue 37497](https://github.com/python/cpython/issues/37497), closed historical documentation issue: unused_data versus output-limited unconsumed_tail. Current Python references govern the tested contract.
