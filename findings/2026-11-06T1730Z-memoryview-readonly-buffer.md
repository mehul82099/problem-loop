# A read-only memoryview is not an immutable buffer snapshot

## Research
Python documents memoryview.toreadonly as returning a read-only version while leaving the original view unchanged. Its own example writes through the original view and reads the changed value through the read-only one. The important boundary is permission through this view, not immutability of the underlying buffer.

## Discussion
A read-only view over a bytearray rejects item assignment through that view. The bytearray and any writable view can still change the same bytes, and the read-only view sees those changes. Its obj attribute also exposes the underlying object. Treating this as a barrier against untrusted Python code would be a stronger claim than the interface supplies.

For a stable byte value, copying to bytes detaches the snapshot from later bytearray edits. That costs a copy; this probe makes no performance claim. A view also has a lifetime: while views export a bytearray buffer, resizing can raise BufferError even if one view is read-only. Releasing the original view does not release the separate read-only view. Release each view when done, or use context management where it fits.

## Conclusion
Choose explicitly between a live read-only view and a copied immutable byte snapshot. The former restricts writes through one handle while reflecting updates; the latter preserves the copied value. Neither is a concurrency or transaction policy. This is documented behavior, not a new defect or an isolation mechanism.

## Action: executable probe
Original code under this repository's MIT license. One small bytearray, two views and a bytes copy. Run without Python optimization so assertions remain enabled.

```python
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def raises(kind, operation):
    try:
        operation()
    except kind:
        return True
    return False

buffer = bytearray(b'abc')
writable = memoryview(buffer)
readonly = writable.toreadonly()
check(readonly is not writable)
check(readonly.readonly)
check(not writable.readonly)
check(readonly.obj is buffer)
check(bytes(readonly) == b'abc')
check(raises(TypeError, lambda: readonly.__setitem__(0, 120)))
snapshot = bytes(readonly)
buffer[0] = ord('x')
check(bytes(readonly) == b'xbc')
check(snapshot == b'abc')
writable[1] = ord('y')
check(bytes(readonly) == b'xyc')
check(buffer == bytearray(b'xyc'))
check(raises(BufferError, lambda: buffer.extend(b'd')))
writable.release()
check(bytes(readonly) == b'xyc')
check(raises(BufferError, lambda: buffer.extend(b'd')))
readonly.release()
buffer.extend(b'd')
check(buffer == bytearray(b'xycd'))
check(raises(ValueError, lambda: bytes(readonly)))
with memoryview(snapshot) as view:
    check(view.readonly)
    check(bytes(view) == b'abc')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 17 checks passed on CPython 3.13.17 and 3.14.9.
- Tests separate view identity/flags, exposed backing object, rejected write, visible alias edits, stable bytes snapshot, bytearray resize restrictions, separate release lifetimes, released-view failure and a bytes-backed view control.
- No custom buffer exporter, C API, mmap, multidimensional/non-contiguous layout, threads, concurrent mutation, performance or external consumer was tested. No security-boundary, atomic snapshot under concurrent writes or general buffer policy is claimed.
- Distinct from the earlier mappingproxy live mapping and frozen-dataclass findings: this concerns buffer exports and view lifetime.

## Sources
- [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html): toreadonly example, obj, bytes conversion and release contract.
- [CPython issue 77357](https://github.com/python/cpython/issues/77357): historical introduction of toreadonly, not a current defect report.
- [WebDevData reference](https://www.webdevdata.net/reference/python/functions/memoryview-toreadonly): live-buffer and copied-value distinction. Broad untrusted-sharing language is not adopted.
- [Runebook explanation](https://runebook.dev/en/docs/python/library/stdtypes/memoryview.toreadonly): original view and backing-buffer behavior. Some unrelated examples/claims are inaccurate; primary docs govern here.
- [Real Python memoryview reference](https://realpython.com/ref/builtin-functions/memoryview/): bytes/bytearray view examples; performance claims not tested.
- [Vox1 lesson](https://vox1.ai/trees/python/memoryview-toreadonly-01a0f561-a847-7b1b-9472-6e0e738854f5): independent original-view mutation example, not an isolation guarantee.
