# A common string prefix is not a common directory

## Research
A public Python question reports that commonprefix returns part of a directory name instead of the shared directory. The current os.path documentation says why: commonprefix compares characters, while commonpath compares path components. An independent historical post describes the same surprise. This is longstanding documented behavior, not a new defect.

## Discussion
For `/srv/reports` and `/srv/reporting`, the character prefix is `/srv/report`; the common path is `/srv`. Replacing one function with the other is a semantic change, not a safe mechanical rewrite for every use. Ruff's rule explicitly notes that intentional string-prefix uses differ from path-component uses. Its newer deprecation note concerns Python 3.15; this probe runs 3.13 and 3.14 and makes no claim about warnings on 3.15.

Component-aware does not mean filesystem-aware. commonpath can report a shared path for nonexistent names. PurePath.is_relative_to is also string-based. In an owned temporary fixture below, a directory symlink's spelling is under one directory while its resolved target is an owned sibling directory. Both names and all filesystem changes stay within that one temporary fixture. No external path is opened or inspected.

## Conclusion
Choose the question explicitly:

| Question | API | What it does not establish |
| --- | --- | --- |
| Shared characters in arbitrary strings | `commonprefix` | A complete path component or real directory. |
| Shared path components for a chosen path syntax | `commonpath` | Existence, resolved target or authorization. |
| Lexical ancestry | `PurePath.is_relative_to` | Filesystem lookup or special handling of `..`. |
| Current resolved pathname | `Path.resolve` | That a later operation sees an unchanged filesystem. |

Do not treat these comparisons as a file-access security boundary. Resolving a name and opening it later are separate operations; a mutable namespace requires a separate race-aware access design. This finding supplies no containment validator or sandbox implementation. Also choose the right syntax: os.path follows the host platform, while posixpath and ntpath can be used explicitly for their respective spellings. Mixed relative/absolute paths and different Windows drives are not one common root to silently guess.

## Action: bounded semantics probe
Original code under this repository's MIT license. The only filesystem changes are two empty directories and a directory symlink inside a TemporaryDirectory, removed with the fixture. The filesystem portion requires symlink support; it passed on the Linux environment used here. The pure Windows spelling tests use ntpath on Linux, not Windows filesystem operations. Run without `-O` so assertions remain active.

```python
import json
import ntpath
import os
import platform
import posixpath
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

check(posixpath.commonprefix(['/srv/reports', '/srv/reporting']) == '/srv/report')
check(posixpath.commonpath(['/srv/reports', '/srv/reporting']) == '/srv')
check(posixpath.commonpath(['/srv/reports/a', '/srv/reports/b']) == '/srv/reports')
check(posixpath.commonprefix([]) == '')
for paths in ([], ['/srv/reports', 'reports/a']):
    caught = False
    try:
        posixpath.commonpath(paths)
    except ValueError:
        caught = True
    check(caught)
check(ntpath.commonpath([r'C:\reports\a', r'C:\reports\b']) == r'C:\reports')
caught = False
try:
    ntpath.commonpath([r'C:\reports', r'D:\reports'])
except ValueError:
    caught = True
check(caught)
check(PurePosixPath('/srv/reports/../other').is_relative_to('/srv/reports'))
with TemporaryDirectory() as directory:
    base = Path(directory)
    reports = base / 'reports'
    sibling = base / 'reports-old'
    reports.mkdir()
    sibling.mkdir()
    check(os.path.commonprefix([str(reports), str(sibling)]) == str(reports))
    check(Path(os.path.commonpath([reports, sibling])) == base)
    missing = reports / 'absent' / 'file.txt'
    check(not missing.exists())
    check(Path(os.path.commonpath([reports, missing])) == reports)
    check(missing.is_relative_to(reports))
    check(not (reports / 'link').exists())
    (reports / 'link').symlink_to(sibling, target_is_directory=True)
    candidate = reports / 'link'
    check(candidate.is_relative_to(reports))
    check(Path(os.path.commonpath([reports, candidate])) == reports)
    resolved = candidate.resolve(strict=True)
    check(resolved == sibling)
    check(not resolved.is_relative_to(reports))
    check(candidate.is_symlink())
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9, each under a 15-second external shell timeout.
- Covers partial-component character prefixes, valid shared components, empty and mixed-form rejection, same/different Windows drives using ntpath, lexical `..` ancestry, nonexistent paths, similarly named sibling directories and a symlink whose resolved target differs from lexical ancestry.
- No file contents are read. No adversarial race, permission model, Windows filesystem, UNC path, mount point, case-folding policy, concurrent mutation, broken symlink or production application was tested. Passing these checks is not evidence of secure file access.

## Sources
- [Python 3.14 os.path reference](https://docs.python.org/3.14/library/os.path.html): character-prefix warning, commonpath contract and platform syntax.
- [Python 3.14 pathlib reference](https://docs.python.org/3.14/library/pathlib.html): string-based is_relative_to and resolve semantics.
- [CPython 3.14 posixpath implementation](https://github.com/python/cpython/blob/3.14/Lib/posixpath.py): component comparison and errors; mutable branch.
- [Public commonprefix question](https://stackoverflow.com/questions/21498939/how-to-circumvent-the-fallacy-of-pythons-os-path-commonprefix): historical real-world naming confusion. Old workarounds are not supplied as current security guidance.
- [Ned Batchelder's historical post](https://nedbatchelder.com/blog/201003/whats_the_point_of_ospathcommonprefix): independent explanation from 2010, not a current version-status source.
- [Ruff commonprefix rule](https://docs.astral.sh/ruff/rules/os-path-commonprefix/): why path replacements differ semantically from arbitrary-string prefix uses; its Python 3.15 note is outside the tested versions.
