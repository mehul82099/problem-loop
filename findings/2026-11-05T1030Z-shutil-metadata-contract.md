# Copying file bytes is not the same as preserving file metadata

Date: 2026-11-05. A documented shutil API distinction, not a new filesystem defect.

## Research

The [shutil reference](https://docs.python.org/3/library/shutil.html) defines copyfile as copying contents without metadata, copy as copying data plus permission mode, and copy2 as additionally attempting metadata preservation. Its module-level warning says even the higher-level functions cannot copy all metadata. A [developer question](https://stackoverflow.com/questions/17685217/keeping-file-attributes-on-a-copy) asks about retaining attributes, and a [historical tracker issue](https://bugs.python.org/issue1559684) led to clearer documentation about copyfile's content-only scope. That old Windows report is context, not a reproduction or current Windows capability claim here.

## Discussion

A byte-for-byte match does not establish that permissions or timestamps match. The difference is visible even without administrator access: start with a local source mode of 0640 and an existing destination mode of 0600. In this probe, copyfile replaces the destination bytes while retaining its mode; copy also applies the source mode. Only copy2 preserves the source modification timestamp in the tested cases.

Those observations are scoped to ordinary files on this local Linux filesystem. They are not proof of ownership, ACL, extended-attribute, creation-time or backup fidelity. The reference's best-effort metadata language matters: copy2 is not a promise that every property is preserved. Platform-specific implementation details and support can differ.

## Conclusion

Choose the copy operation from the required properties, then verify those properties explicitly. Use content checks for content, mode checks for permission mode and timestamp checks when the application depends on timestamps. For a backup or replication tool, define the additional metadata contract and supported platforms separately instead of treating successful copy2 completion as full-fidelity verification.

## Action: temporary-file property probe

Ran 12 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64, using local POSIX regular files. The probe compares bytes, permission mode and modification time across copyfile, copy and copy2, plus the source properties. Destinations are created in a temporary directory only. It does not change real user files or require elevated permissions.

```python
import json
import os
import pathlib
import platform
import shutil
import stat
import tempfile

if os.name != 'posix':
    raise SystemExit('This mode-bit probe is scoped to POSIX.')
checks = 0
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory)
    src = root / 'source'
    src.write_bytes(b'example\x00payload\n')
    src.chmod(0o640)
    os.utime(src, ns=(946684800000000000, 946684800000000000))
    source_mtime = src.stat().st_mtime_ns
    source_mode = stat.S_IMODE(src.stat().st_mode)
    for name, copier in [('copyfile', shutil.copyfile),
                          ('copy', shutil.copy), ('copy2', shutil.copy2)]:
        dst = root / name
        dst.write_bytes(b'old')
        dst.chmod(0o600)
        os.utime(dst, ns=(978307200000000000, 978307200000000000))
        copier(src, dst)
        assert dst.read_bytes() == b'example\x00payload\n'
        checks += 1
        mode = stat.S_IMODE(dst.stat().st_mode)
        assert mode == (0o600 if name == 'copyfile' else source_mode)
        checks += 1
        if name == 'copy2':
            assert dst.stat().st_mtime_ns == source_mtime
        else:
            assert dst.stat().st_mtime_ns != source_mtime
        checks += 1
    assert src.read_bytes() == b'example\x00payload\n'
    checks += 1
    assert stat.S_IMODE(src.stat().st_mode) == source_mode
    checks += 1
    assert src.stat().st_mtime_ns == source_mtime
    checks += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed', 'scope': 'local POSIX regular files'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- Existing destinations make the mode distinction explicit. New-file permissions, umask, symlinks, directories and special files are not tested.
- Exact timestamp equality was observed on this filesystem, not established for every filesystem or timestamp resolution. Access time is not asserted because reading can change it.
- No owner/group, ACL, xattr, resource-fork, alternate-stream, Windows/macOS, atomicity or durability validation is included. No full-backup implementation, new defect or performance result is claimed.
