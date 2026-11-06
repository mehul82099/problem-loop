# SpooledTemporaryFile size thresholds do not prevent fileno-triggered rollover

Date: 2026-11-06. A documented storage transition, not a new tempfile defect.

## Research

The [Python 3.14 tempfile reference](https://docs.python.org/3.14/library/tempfile.html) documents two rollover triggers: exceeding max_size and calling fileno. It also documents explicit rollover. The [io reference](https://docs.python.org/3.14/library/io.html) defines fileno as returning an underlying file descriptor. A request for that descriptor is not a passive storage inspection for a spooled file.

A [2019 community question](https://stackoverflow.com/questions/59393486/what-exactly-is-pythons-spooledtemporaryfile) asks whether all spooled data eventually reaches disk. A [2015 units question](https://stackoverflow.com/questions/29393847/spooledtemporaryfile-units-of-maximum-in-memory-size) shows threshold confusion. An [independent September 2026 guide](https://nalar.dev/buffer-temporary-data-in-python-with-spooledtemporaryfile/) explains why downstream fileno calls can move small payloads to temporary-file storage, and why max_size is not a payload limit. A [separate historical issue about max_size=0](https://github.com/python/cpython/issues/78627) records ambiguity; this finding deliberately uses positive thresholds and makes no claim to settle that issue.

## Discussion

A library accepting a file-like object may ask for fileno even when the payload is tiny. With SpooledTemporaryFile, that call forces rollover below the configured size threshold. Do not call fileno merely to check whether the spool already has a descriptor: the check changes the storage state.

The size threshold is a rollover policy, not a hard input cap. This probe writes nine bytes to a spool with an eight-byte threshold. The write succeeds, rollover occurs, and the bytes remain readable. It also checks that fileno on a three-byte spool preserves its logical position and contents.

## Conclusion

Choose storage based on downstream requirements as well as expected payload size. If a real descriptor is always needed, consider TemporaryFile directly. If no descriptor is needed and data is known to be small, BytesIO may be simpler. Enforce application payload limits separately. No total-RAM guarantee, physical disk-write claim, disk-capacity test or performance result follows from this probe; temporary-file storage may itself be backed by memory on some systems.

## Action

Original MIT-licensed probe. It writes only nine bytes and three bytes to owned temporary files and closes both. A test subclass counts invocations of the documented public rollover method; this is instrumentation for the named builds, not an application storage-detection API. No private attributes are read.

```python
import json
import os
import platform
from tempfile import SpooledTemporaryFile

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

class ObservedSpool(SpooledTemporaryFile):
    # Test instrumentation only: count calls to the public rollover method.
    def __init__(self, **kwargs):
        self.rollover_calls = 0
        super().__init__(**kwargs)

    def rollover(self):
        self.rollover_calls += 1
        return super().rollover()

with ObservedSpool(max_size=8, mode='w+b') as spool:
    check(spool.rollover_calls == 0)
    check(spool.write(b'12345678') == 8)
    check(spool.rollover_calls == 0)  # Equal to threshold, not greater.
    check(spool.write(b'9') == 1)
    check(spool.rollover_calls == 1)
    check(spool.tell() == 9)
    spool.seek(0)
    check(spool.read() == b'123456789')  # Threshold is not a payload cap.
check(spool.closed)

with ObservedSpool(max_size=1024, mode='w+b') as spool:
    spool.write(b'abc')
    check(spool.rollover_calls == 0)
    before = spool.tell()
    fd = spool.fileno()  # Public descriptor request forces rollover.
    check(spool.rollover_calls == 1)
    check(isinstance(fd, int) and os.fstat(fd).st_size == 3)
    check(spool.tell() == before)
    spool.seek(0)
    check(spool.read() == b'abc')
check(spool.closed)

print(json.dumps({'python': platform.python_version(),
                  'checks': checks, 'result': 'passed'}))
```

## Validation

Passed 14 checks each on CPython 3.13.17 and 3.14.9 in this Linux environment. Checks cover equal-versus-exceeded positive thresholds, accepted oversized payload, descriptor availability after fileno, preserved position/content, and close on context exit. Zero thresholds, text mode, truncate, I/O failures, process memory and other platforms are not tested. Repository CI is separate.

## Publisher

One evidence-backed finding and bounded probe. No runtime patch or production storage changes.
