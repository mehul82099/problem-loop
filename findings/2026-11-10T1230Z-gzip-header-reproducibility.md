# Equal decompressed content does not imply equal gzip artifacts

Date: 2026-11-10. A tested gzip-header policy, not a new compression defect.

## Research

The Python gzip references distinguish payload compression from header metadata. With fileobj supplied, GzipFile's filename parameter controls an optional original-name field. An empty filename omits that field. An explicit mtime=0 removes creation-time dependence. RFC 1952 defines the FNAME flag and says MTIME=0 means no timestamp is available.

A public question asks why compressing the same file changes its checksum; its answer separates original filename and timestamp. The corresponding documentation-feature tracker is closed, not an unresolved runtime defect. The independent reproducible-gzip guide also limits its reproducibility scope to the same Python/zlib environment instead of promising permanent hashes across compressor upgrades.

The version distinction matters: gzip.compress defaults mtime to None in 3.13 and to 0 starting in 3.14. GzipFile still defaults mtime to None in both tested versions. A rule about one API or one version must not silently become a claim about all gzip output.

## Discussion

The probe creates members with identical payloads but two explicit timestamps or two header names. The gzip bytes differ while all three decompress to the same source bytes. No clock delay is needed to isolate these two metadata changes. Setting mtime alone cannot remove a filename that was separately included.

The bounded pack helper supplies an empty header filename, zero timestamp and explicit compression level. Repeated calls produce identical bytes within each tested process/environment. It also overrides a synthetic destination stream's discernible name to show that explicit filename='' prevents that name entering the header. Everything is in BytesIO; no file path is opened.

These are two different equality questions: exact gzip-artifact equality includes metadata and compressor choices; decompressed-content equality ignores the tested header differences. A whole-file hash is useful only after deciding which equality the application means. No digest or gzip trailer here authenticates a producer.

## Conclusion

For a reproducible gzip artifact, make filename, mtime and compression level explicit, and define the compressor/runtime scope. Verify exact bytes and the decompressed payload separately. For payload identity alone, do not interpret an artifact-byte difference as proof that the original content changed.

The earlier zlib-member finding treats decompression completion and trailing members; the copyfileobj and archive findings treat other I/O boundaries. A full targeted repository search found no prior gzip-header reproducibility treatment. This increment is limited to header metadata and API-version defaults, not a replacement compression library or a new defect report.

## Action

Original MIT-licensed diagnostic. It passed 7,654 checks on actual CPython 3.13.17 and 7,655 on CPython 3.14.9, both using zlib runtime 1.3.2. The one-check difference is the additional 3.14 default-zero-header assertion. There are 1,092 payload/level cases: 364 payloads of lengths 0 through 5 over three byte values, at three explicit compression levels. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import gzip
import inspect
import itertools
import json
import platform
import zlib
from io import BytesIO
checks = cases = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def pack(payload, name='', stamp=0, level=9):
    raw = BytesIO()
    with gzip.GzipFile(filename=name, mode='wb', fileobj=raw,
                       mtime=stamp, compresslevel=level) as stream:
        stream.write(payload)
    return raw.getvalue()

def stamp(data):
    # Header inspection only for the members produced by this probe.
    return int.from_bytes(data[4:8], 'little')

for length in range(6):
    for values in itertools.product((0, 65, 255), repeat=length):
        payload = bytes(values)
        for level in (1, 6, 9):
            a = pack(payload, level=level)
            b = pack(payload, level=level)
            check(a == b)
            check(a[:3] == b'\x1f\x8b\x08')
            check(a[3] & 8 == 0)
            check(stamp(a) == 0)
            check(gzip.decompress(a) == payload)
            direct = gzip.compress(payload, compresslevel=level, mtime=0)
            check(gzip.decompress(direct) == payload)
            check(direct[3] & 8 == 0 and stamp(direct) == 0)
            cases += 1

payload = b'fixed local payload\n'
a = pack(payload, name='a.txt', stamp=123456)
b = pack(payload, name='a.txt', stamp=123457)
c = pack(payload, name='b.txt', stamp=123456)
check(a != b and a != c)
check(gzip.decompress(a) == gzip.decompress(b) == gzip.decompress(c) == payload)
check(stamp(a) == 123456 and stamp(b) == 123457)
check(a[3] & 8 != 0)
check(a[10:a.index(b'\0', 10)] == b'a.txt')
check(c[10:c.index(b'\0', 10)] == b'b.txt')
# An empty header filename overrides a discernible destination name.
raw = BytesIO()
raw.name = 'destination.txt.gz'
with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0,
                   compresslevel=9) as stream:
    stream.write(payload)
check(raw.getvalue()[3] & 8 == 0)
check(gzip.decompress(raw.getvalue()) == payload)
# Observe version-specific defaults without a wall-clock delay or patching time.
expected = None if platform.python_version_tuple()[:2] == ('3', '13') else 0
check(inspect.signature(gzip.compress).parameters['mtime'].default == expected)
check(inspect.signature(gzip.GzipFile).parameters['mtime'].default is None)
if expected == 0:
    check(stamp(gzip.compress(payload, compresslevel=9)) == 0)
print(json.dumps({'python': platform.python_version(), 'zlib_runtime': zlib.ZLIB_RUNTIME_VERSION,
                  'checks': checks, 'payload_level_cases': cases,
                  'compress_mtime_default': expected, 'status': 'passed'}))
```

## Publisher and limits

The grid checks repeated local artifact equality, fixed header signature/time/name omission and round-trip payload equality through GzipFile and compress. Named cases inspect timestamp and name differences, explicit empty-name override and exact signature defaults on the two versions. Header offsets apply only to the simple members this probe creates, not arbitrary gzip members with optional fields.

The helper uses no filesystem, network, private data, shell or third-party package. It does not guarantee equality across Python/zlib versions, operating systems, write chunking strategies or different APIs. It is not a general gzip validator, archive extractor, atomic file publisher, signature system, corruption/adversarial-input test, resource bound or performance benchmark. Large payloads, multiple members, custom file-like behavior and out-of-range timestamps are untested. Current versioned docs name newer patch releases than the binaries tested; that source contract is distinct from exact binary identity. Repository CI is separate from local results.

## Sources

All six public sources fetched and relevant sections inspected this cycle:

- Python 3.13 gzip reference: GzipFile name/time controls and compress's None default. https://docs.python.org/3.13/library/gzip.html
- Python 3.14 gzip reference: compress's changed default versus GzipFile's unchanged default. Its newer timestamp-range handling is not tested or generalized to the named binaries. https://docs.python.org/3.14/library/gzip.html
- Closed documentation-feature issue 82906, original discussion of a gzip -n equivalent. Proposed API examples in the thread are not asserted as existing methods. https://github.com/python/cpython/issues/82906
- Public checksum/header question, September 8, 2014. Historical code is not copied as the helper. https://stackoverflow.com/questions/25728472/python-gzip-omit-the-original-filename-and-timestamp
- Independent guide, October 23, 2026, controlling headers and limiting reproducibility to the same environment. Its filesystem workflow is not used or tested here. https://www.bobobk.com/en/python-reproducible-gzip.html
- RFC 1952, May 1996, section 2.3.1: FNAME and MTIME field definitions. https://www.rfc-editor.org/rfc/rfc1952
