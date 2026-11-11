# follow_symlinks=False does not mean replace a destination symlink

Date: 2026-11-11 (IST). Tested shutil copy semantics, not a new vulnerability or defect discovery.

## Research

[CPython issue 78555](https://github.com/python/cpython/issues/78555) records confusion about follow_symlinks applying to a source while writes still follow a destination link. Its historical discussion is context, not evidence of an approved replacement API. The [versioned shutil reference](https://docs.python.org/3.14/library/shutil.html) says that when follow_symlinks is false **and src is a symbolic link**, a new symbolic link is created. That is narrower than a promise not to follow any link in either path.

The [exact tagged shutil implementation](https://github.com/python/cpython/blob/v3.14.9/Lib/shutil.py) first checks whether source and destination are the same file, then either creates a source link or opens the destination for writing. The [os.path samefile reference](https://docs.python.org/3.14/library/os.path.html) defines file identity using device/inode information. The [pathlib reference](https://docs.python.org/3.14/library/pathlib.html) distinguishes is_symlink/readlink observations from target reads. [Historical issue 39670](https://github.com/python/cpython/issues/39670) concerned copying over a hard/symbolic alias of the source; this report tests the present SameFileError guard rather than claiming that old data-destruction bug still exists.

## Discussion

On the tested Linux builds, copying a regular source to an existing destination symlink with follow_symlinks=False keeps the link and overwrites its target. A dangling destination link also remains a link and its missing target is created. Setting follow_symlinks=True gives the same byte-copy destination behavior.

When the source itself is a symlink and follow_symlinks=False, the operation takes a different branch: it creates a new symlink only if the destination entry is absent. An existing or dangling destination link is an occupied name, causing FileExistsError, with its old target unchanged. When follow_symlinks=True, the source target's bytes are copied through the destination link instead.

The matrix exercises copyfile, copy and copy2; their observed byte/link results agree in these cases. It does not assert equal metadata behavior. A destination alias of the source is a separate case: both hard-link and symlink aliases raise SameFileError in the copyfile controls under both flag values, leaving source bytes unchanged.

## Conclusion

Choose separately whether to copy source bytes or a source link, and whether to write through a destination link or replace a directory entry. This flag only resolves the tested source choice. Do not treat follow_symlinks=False as a destination-link replacement operation, a race-free write protocol or a filesystem containment boundary. This report supplies no general safe-replacement helper and recommends no check-then-copy workaround for untrusted directories.

## Action

**189 assertions passed independently on CPython 3.13.17 and 3.14.9, Linux**. Thirty-six matrix cases cross three copy functions, two flag values, regular/link source and absent/existing-link/dangling-link destinations. Four extra copyfile alias controls cross hard/symbolic alias and both flags. The probe checks original source bytes, final link identity/readlink, target bytes or absence, and expected errors.

| Source | Flag | Absent destination | Existing destination link | Dangling destination link |
| --- | --- | --- | --- | --- |
| regular | either | new regular file | link stays, target bytes replaced | link stays, target file created |
| symlink | true | new regular file | link stays, target bytes replaced | link stays, target file created |
| symlink | false | new symlink to source's stored target text | FileExistsError, old target unchanged | FileExistsError, target stays absent |

Run original MIT code below as `python copy-destination-links.py` without -O so assertions remain enabled. It creates and removes only unique temporary fixtures; all source, destination and link targets stay inside each fixture. No private files, network, dependency install or existing-directory changes. It refuses non-POSIX execution rather than claiming portable link behavior.

```python
# Original diagnostic, MIT licensed. POSIX, synthetic temporary files only.
import json
import os
from pathlib import Path
import platform
import shutil
from tempfile import TemporaryDirectory

if os.name != 'posix':
    raise SystemExit('POSIX symlink fixture required; no results asserted.')
checks = 0
results = []

def check(value):
    global checks
    assert value
    checks += 1

for copier in (shutil.copyfile, shutil.copy, shutil.copy2):
    for follow in (False, True):
        for source_link in (False, True):
            for destination_kind in ('missing', 'existing-link', 'dangling-link'):
                with TemporaryDirectory(prefix='copy-link-') as tmp:
                    root = Path(tmp)
                    original = root / 'original'
                    original.write_bytes(b'new-content')
                    src = root / 'src-link' if source_link else original
                    if source_link:
                        src.symlink_to('original')
                    dst = root / 'destination'
                    target = root / 'target'
                    if destination_kind == 'existing-link':
                        target.write_bytes(b'old-content')
                        dst.symlink_to('target')
                    elif destination_kind == 'dangling-link':
                        dst.symlink_to('target')
                    link_copy = source_link and not follow
                    occupied = destination_kind != 'missing'
                    expected_error = link_copy and occupied
                    error = None
                    try:
                        copier(src, dst, follow_symlinks=follow)
                    except FileExistsError:
                        error = 'FileExistsError'
                    check((error is not None) == expected_error)
                    check(original.read_bytes() == b'new-content')
                    if expected_error:
                        check(dst.is_symlink() and os.readlink(dst) == 'target')
                        check(target.exists() == (destination_kind == 'existing-link'))
                        if target.exists():
                            check(target.read_bytes() == b'old-content')
                    elif link_copy:
                        check(dst.is_symlink() and os.readlink(dst) == 'original')
                        check(dst.read_bytes() == b'new-content')
                        check(not target.exists())
                    elif occupied:
                        check(dst.is_symlink() and os.readlink(dst) == 'target')
                        check(target.read_bytes() == b'new-content')
                        check(dst.read_bytes() == b'new-content')
                    else:
                        check(not dst.is_symlink())
                        check(dst.read_bytes() == b'new-content')
                        check(not target.exists())
                    results.append({'copier': copier.__name__, 'follow': follow,
                                    'source_link': source_link, 'destination': destination_kind,
                                    'result': error or ('new-source-link' if link_copy else 'copied-bytes')})
# Same-file guard applies to both hard-link and symbolic-link aliases of source.
for alias_kind in ('hard-link', 'symlink'):
    for follow in (False, True):
        with TemporaryDirectory(prefix='copy-same-') as tmp:
            root = Path(tmp)
            src, dst = root / 'src', root / 'dst'
            src.write_bytes(b'unchanged')
            if alias_kind == 'hard-link':
                os.link(src, dst)
            else:
                dst.symlink_to('src')
            try:
                shutil.copyfile(src, dst, follow_symlinks=follow)
            except shutil.SameFileError:
                check(True)
            else:
                raise AssertionError('same-file alias accepted')
            check(src.read_bytes() == b'unchanged')
            check(dst.read_bytes() == b'unchanged')
print(json.dumps({'python': platform.python_version(), 'platform': platform.system(),
                  'checks': checks, 'matrix_cases': len(results), 'alias_controls': 4,
                  'results': results}, indent=2))
```

## Publisher and limits

No Windows, ACL, special-file, directory-destination, intermediate symlink, concurrent rename, metadata preservation, atomicity or durability claim. An absent destination is distinct from a dangling link entry; that distinction is observed here, not assumed from exists() alone. The earlier repository findings on link-vs-target existence and copy metadata have been read; this increment addresses the source/destination flag split during actual copies, which those probes did not test.
