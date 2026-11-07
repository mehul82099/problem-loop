# A missing symlink target does not mean the link name is free

## Research
Path.exists follows symbolic links by default. A dangling link can therefore produce exists() == False while is_symlink() == True and its directory entry remains occupied. A public question demonstrates trying to create a link at such a name and receiving FileExistsError. Current pathlib provides exists(follow_symlinks=False) to query the link entry instead of its target.

## Discussion
The probe creates a relative link to a file inside a temporary directory, removes the target and checks both questions. Default stat follows the link and raises FileNotFoundError; lstat or stat(follow_symlinks=False) reports the link's metadata. os.path.exists versus lexists offers the corresponding distinction. No link replacement or deletion outside the fixture is attempted.

Current Python 3.14 docs also say status-query helpers suppress OS errors and recommend stat when an error distinction matters. Earlier versions suppress some errors and raise others. This probe does not reproduce permission failures, so it does not generalize the ordinary missing-target tests into cross-version error-handling equivalence. A false boolean is not a complete diagnostic.

## Conclusion
Decide whether the question is about a resolved target, the link entry or an operation's success. Use the appropriate query or diagnostic call. A prior exists/lstat check does not reserve a name or remove a race before a later write; handle the intended operation's errors and use an operation with the required filesystem guarantees. The public answer's suggestion that lstat avoids check-then-act races is not adopted here. This is documented behavior, not a new defect or a secure file-creation recipe.

## Action: executable fixture probe
Original code under this repository's MIT license. Creates one file and one symlink inside a new TemporaryDirectory, removes its own target/link and cleans up the directory. Run without Python optimization so assertions remain enabled. Requires symlink support and permission to create a symlink.

```python
from pathlib import Path
from tempfile import TemporaryDirectory
from os.path import exists, lexists
from stat import S_ISLNK, S_ISREG
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    target = root / 'target.txt'
    target.write_text('fixture', encoding='utf-8')
    link = root / 'alias.txt'
    link.symlink_to('target.txt')  # Relative target, inside fixture.
    missing = root / 'missing.txt'
    check(target.exists())
    check(link.exists())
    check(link.exists(follow_symlinks=False))
    check(link.is_symlink())
    check(S_ISREG(link.stat().st_mode))
    check(S_ISLNK(link.lstat().st_mode))
    check(S_ISLNK(link.stat(follow_symlinks=False).st_mode))
    check(not missing.exists())
    check(not missing.exists(follow_symlinks=False))
    target.unlink()
    check(not link.exists())
    check(link.exists(follow_symlinks=False))
    check(link.is_symlink())
    check(not exists(link))
    check(lexists(link))
    check(S_ISLNK(link.lstat().st_mode))
    try:
        link.stat()
    except FileNotFoundError:
        target_missing = True
    else:
        target_missing = False
    check(target_missing)
    try:
        link.symlink_to('another.txt')
    except FileExistsError:
        entry_occupied = True
    else:
        entry_occupied = False
    check(entry_occupied)
    check(link.readlink() == Path('target.txt'))
    link.unlink()  # Remove fixture link, not a target.
    check(not link.exists(follow_symlinks=False))
    check(not link.is_symlink())
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 20 checks passed on CPython 3.13.17 and 3.14.9 on Linux.
- Covers existing target/link, missing path, target removal, follow versus no-follow status, lstat file type, exists/lexists, occupied-name creation failure, readlink and fixture cleanup.
- exists(follow_symlinks=...) was added in Python 3.12; stat's flag was added in 3.10. No fallback for older runtimes is supplied.
- No Windows junctions/reparse points, permissions, symlink loops, intermediate-directory links, concurrent renames, sandbox escape, file-descriptor creation protocol or production filesystem was tested. No race-free or security-boundary claim is made.

## Sources
- [Python 3.14 pathlib](https://docs.python.org/3.14/library/pathlib.html): exists/stat/lstat/is_symlink contracts, version additions and 3.14 status-error change.
- [Python 3.14 os.path](https://docs.python.org/3.14/library/os.path.html): exists versus lexists and permission caveat.
- [Python 3.14 os](https://docs.python.org/3.14/library/os.html): underlying symlink/stat operations and platform limits.
- [Broken-link exists question](https://stackoverflow.com/questions/75444181/pathlib-path-exists-returns-false-for-broken-symlink): concrete occupied-name confusion, February 14, 2023; older-version and race-avoidance claims in answers not adopted.
- [CPython PR 29655](https://github.com/python/cpython/pull/29655): historical addition of exists follow_symlinks, merged in 2023; not a current pending fix.
- [CPython PR 18864](https://github.com/python/cpython/pull/18864): historical stat follow_symlinks addition; not a tested-runtime identity.
