# CPython: _pyio.BufferedRandom.truncate() keeps the read buffer, so later reads return data no longer in the file

**Source:** [python/cpython#161271](https://github.com/python/cpython/issues/161271) - opened 2026-11-03 by tsayin4 (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

`_io.BufferedRandom.truncate()` flushes **and rewinds** the raw stream before truncating (`buffered_flush_and_rewind_unlocked()` in `Modules/_io/bufferedio.c`), which drops the read-ahead buffer. The pure-Python mirror `_pyio.BufferedRandom.truncate()` does not: its comment says "Use seek to flush the read buffer", but nothing seeks, so reads after `truncate()` hand out bytes that are no longer in the file. The reporter's reproducer:

```python
import io, _pyio, os
for mod in (io, _pyio):
    with open("x", "wb") as f:
        f.write(b"abcdef")
    with mod.open("x", "r+b") as f:
        f.read(1)
        f.truncate(0)
        print(mod.__name__, f.read(), os.path.getsize("x"))
```

prints `io b'' 0` but `_pyio b'bcdef' 0` - the file is empty, yet `read()` returns 5 bytes. The divergence also appears with a bare `truncate()`, any truncation point below the read-ahead position, `r+b`/`w+b`/`a+b` modes, and a `BufferedRandom` built directly on a `BytesIO`, per the reporter. Tested on 3.11 and 3.13; the affected code is unchanged on `main`. The reporter links PR gh-161273 as a fix.

## Verification (checked during this finding)

- **Reproduced the divergence** by running the reporter's exact script under Python 3.10.12: `io` returned `b''` with file size 0; `_pyio` returned `b'bcdef' with the file at 0 bytes. Same behavior the reporter shows.
- Source anchors on `main`: `Lib/_pyio.py` line 1470 is `BufferedRandom.truncate` (class `BufferedRandom` starts at line 1433), and line 1473 carries the comment "# Use seek to flush the read buffer." with the body calling `BufferedWriter.truncate(self, pos)` - no seek, as described.
- `buffered_flush_and_rewind_unlocked` exists in `Modules/_io/bufferedio.c` (line 908) and is called from the truncate path (line 945).
- Linked PR gh-161273 exists, is open, titled "Drop the read buffer in `_pyio.BufferedRandom.truncate()`".

## Limits

- Reproduction here covered the reporter's script on Python 3.10.12 only; the other modes and the `BytesIO` construction were not exercised.
- Maintainer position is in flux: a CPython contributor (cmaloney, association CONTRIBUTOR) commented that `_pyio` changes are on hold until steering-council#372 (whether `_pyio` should be removed) is decided, and the reporter agreed the issue may close if `_pyio` is on the way out. The bug is real, but its fix path depends on a governance decision about the module's future.
- `_pyio` is the fallback implementation most production code never uses (the C `_io` is default), so practical impact is limited to environments that import `_pyio` directly, test suites that compare the two implementations, and ports without the C extension.
- The proposed PR was not reviewed or run here.

## Sources

- Issue: <https://github.com/python/cpython/issues/161271>
- `Lib/_pyio.py` on main: <https://github.com/python/cpython/blob/main/Lib/_pyio.py>
- `Modules/_io/bufferedio.c` on main: <https://github.com/python/cpython/blob/main/Modules/_io/bufferedio.c>
- Linked PR: <https://github.com/python/cpython/pull/161273>
- Steering council question: <https://github.com/python/steering-council/issues/372>
