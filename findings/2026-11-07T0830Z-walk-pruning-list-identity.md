# os.walk pruning needs an in-place edit before top-down traversal resumes

## Research
Python documents dirnames as a control point for os.walk when topdown=True. Editing that list in place determines which subdirectories are visited after the current yield. Rebinding the local variable to a filtered list does not edit the list retained by the walker. Public questions repeatedly show the resulting surprise: the displayed filtered names look right, but traversal still reaches excluded trees.

## Discussion
The probe compares rebinding, slice assignment, clearing the shared list, deleting only the local name and editing filenames. Only the in-place directory-list edits prune this top-down walk. In bottom-up mode those descendants have already been visited when their parent is yielded, so the same edits do not prune them. Removing a name from dirnames does not delete the corresponding directory or file.

A separate deterministic list example shows why removing names while iterating that same list can skip an adjacent candidate. Build a filtered list first, then assign it to the original list's full slice. This combines safe filtering with the identity that the walker needs. The test compares sets of visited paths rather than relying on filesystem enumeration order.

## Conclusion
Use topdown=True and dirs[:] = filtered_names to prune future recursion. Filtering printed results or replacing the local variable is not the same operation. Excluding a subtree is not a filesystem security boundary: the parent has already been enumerated, filesystem state can change, errors need an explicit policy and symlink behavior needs separate review. This is documented traversal behavior, not a new defect or a permission-control tool.

## Action: executable probe
Original code under this repository's MIT license. Creates and cleans up a small isolated temporary tree. Traversal changes no files; fixture setup/cleanup does. Run without Python optimization so assertions remain enabled.

```python
import json
import os
import platform
from pathlib import Path
from tempfile import TemporaryDirectory

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

with TemporaryDirectory(prefix='walk-contract-') as tmp:
    base = Path(tmp)
    for name in ('keep/leaf', 'skip/inside', 'skip2/inside'):
        (base / name).mkdir(parents=True)
    (base / 'root.txt').write_text('root', encoding='utf-8')
    (base / 'skip/secret.txt').write_text('fixture', encoding='utf-8')

    def visit(mode, topdown=True):
        seen = []
        for root, dirs, files in os.walk(base, topdown=topdown):
            relative = Path(root).relative_to(base).as_posix()
            seen.append(relative)
            if relative == '.':
                if mode == 'rebind':
                    dirs = [d for d in dirs if not d.startswith('skip')]
                elif mode == 'slice':
                    dirs[:] = [d for d in dirs if not d.startswith('skip')]
                elif mode == 'clear':
                    dirs.clear()
                elif mode == 'delete-name':
                    del dirs
                elif mode == 'filter-files':
                    files[:] = []
        return set(seen)

    all_paths = {'.', 'keep', 'keep/leaf', 'skip', 'skip/inside',
                 'skip2', 'skip2/inside'}
    check(visit('none') == all_paths)
    check(visit('rebind') == all_paths)
    check(visit('slice') == {'.', 'keep', 'keep/leaf'})
    check(visit('clear') == {'.'})
    check(visit('delete-name') == all_paths)
    check(visit('filter-files') == all_paths)
    check(visit('slice', topdown=False) == all_paths)
    check(visit('clear', topdown=False) == all_paths)

    walker = os.walk(base, topdown=True)
    root, dirs, files = next(walker)
    check(Path(root) == base)
    check(set(dirs) == {'keep', 'skip', 'skip2'})
    check(files == ['root.txt'])
    shared = dirs
    dirs = ['keep']
    check(dirs is not shared)
    check(set(shared) == {'keep', 'skip', 'skip2'})
    shared[:] = ['keep']
    check(list(shared) == ['keep'])
    remaining = {Path(r).relative_to(base).as_posix() for r, _, _ in walker}
    check(remaining == {'keep', 'keep/leaf'})
    check((base / 'skip/secret.txt').read_text(encoding='utf-8') == 'fixture')
    check((base / 'skip2/inside').is_dir())

    # A deterministic list example, independent of directory enumeration order.
    names = ['skip', 'skip2', 'keep']
    for name in names:
        if name.startswith('skip'):
            names.remove(name)
    check(names == ['skip2', 'keep'])
    names[:] = [n for n in names if not n.startswith('skip')]
    check(names == ['keep'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Covers unfiltered traversal, rebinding, in-place filtering, clearing, deleting the local name, filenames-only filtering, ineffective bottom-up edits, the retained shared list, unchanged fixture contents/directories and adjacent-item removal during list iteration.
- No symlinks, permission errors, concurrent directory changes, Windows filesystem, mounted network storage, ordering guarantee, timing benchmark or production ignore-rule engine was tested. The skip prefix is a synthetic fixture rule, not gitignore semantics.

## Sources
- [Python 3.14 os.walk](https://docs.python.org/3.14/library/os.html): top-down in-place control, bottom-up limitation, enumeration/error/symlink caveats.
- [CPython os.py, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/os.py): implementation context for yielding a shared directory list; not the exact identity of the tested builds.
- [Excluding directories in os.walk](https://stackoverflow.com/questions/19859840/excluding-directories-in-os-walk): public pruning question and slice-assignment answer.
- [CPython issue 111321](https://github.com/python/cpython/issues/111321): report about removing from dirnames during iteration and skipping adjacent candidates; cited as a report, not a verified claim about current Django code.
- [Manipulating Python os.walk recursion](https://www.ostricher.com/2014/12/manipulating-python-os-walk-recursion/): December 15, 2014 independent explanation and comment clarifying rebinding. Its example using del dirnames does not clear the retained list; do not copy that example as a pruning fix.
- [Limit nested directories traversed by os.walk](https://stackoverflow.com/questions/17493271/limit-the-number-of-nested-directories-traversed-by-os-walk): July 5, 2013 public depth-limit discussion explaining the difference between deleting a slice and replacing a reference.
