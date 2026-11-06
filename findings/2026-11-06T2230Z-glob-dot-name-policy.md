# A glob-to-pathlib refactor can change dot-name selection

## Research
The current pathlib documentation explicitly lists differences from the glob module: dot-prefixed names are not special to Path.glob, and its `**` components are recursive. Public questions and Ruff's migration rule both flag the mismatch. Replacing glob.glob with Path.glob is not a semantics-preserving change based on the pattern string alone.

## Discussion
For this fixture, `glob.glob('*.txt')` omits a dot-prefixed file while `Path.glob('*.txt')` includes it. Recursive patterns also differ at dot-prefixed directory segments. On these supported builds, include_hidden=True lets glob wildcards match dot-prefixed names, including a plain `*.txt` pattern, not only recursive directories.

Here "hidden" refers to dot-prefixed path segments, not Windows hidden attributes or a privacy classification. Current Python 3.14 glob wording describes wildcard matching of dot-prefixed segments; a public 2026 documentation issue reports older narrower wording about `**` and hidden directories. This finding does not repeat that older wording as the current contract. Older community claims that glob cannot include all dotfiles also predate the include_hidden option added in Python 3.11.

## Conclusion
Preserve an explicit selection policy when changing path APIs. Use include_hidden=True if glob should include dot-names, or explicitly filter relative path segments after pathlib enumeration if the intended result excludes all dot-name segments. That result filter still traverses dot-directories; it is not traversal pruning, an access boundary or a safe-upload rule. Keep separate checks for file type, symlinks, permissions and concurrent filesystem changes where those matter.

## Action: executable fixture probe
Original code under this repository's MIT license. Creates six plain text files only inside a new TemporaryDirectory, then removes that fixture. Results are normalized to relative names and sets, so no filesystem ordering claim is made. Run without Python optimization so assertions remain enabled.

```python
from glob import glob
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    names = {'visible.txt', '.hidden.txt', 'sub/normal.txt',
             'sub/.private.txt', '.cache/nested.txt', '.cache/.inner.txt'}
    for name in names:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('fixture', encoding='utf-8')

    def module(pattern, **kwargs):
        return set(glob(pattern, root_dir=root, **kwargs))

    def paths(pattern):
        return {p.relative_to(root).as_posix() for p in root.glob(pattern)}

    check(module('*.txt') == {'visible.txt'})
    check(paths('*.txt') == {'visible.txt', '.hidden.txt'})
    check(module('*.txt', include_hidden=True) == paths('*.txt'))
    check(module('.*.txt') == {'.hidden.txt'})
    check(module('**/*.txt', recursive=True) == {'visible.txt', 'sub/normal.txt'})
    check(paths('**/*.txt') == names)
    check(module('**/*.txt', recursive=True, include_hidden=True) == names)
    check({p.relative_to(root).as_posix() for p in root.rglob('*.txt')} == names)
    check(module('.cache/*.txt') == {'.cache/nested.txt'})
    check(paths('.cache/*.txt') == {'.cache/nested.txt', '.cache/.inner.txt'})
    check(module('.cache/*.txt', include_hidden=True) == paths('.cache/*.txt'))

    # This is a relative dot-name policy, not an OS hidden-attribute test.
    selected = [p for p in root.rglob('*.txt')
                if not any(part.startswith('.') for part in p.relative_to(root).parts)]
    check({p.relative_to(root).as_posix() for p in selected}
          == {'visible.txt', 'sub/normal.txt'})
    check(all(p.is_file() for p in selected))
    check(module('*') == {'visible.txt', 'sub'})  # Not file-only.
    check(paths('*') == {'visible.txt', '.hidden.txt', 'sub', '.cache'})
    check(module('missing*.txt') == set())
    check(paths('missing*.txt') == set())
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 17 checks passed on CPython 3.13.17 and 3.14.9 on Linux.
- Checks direct/recursive matching, explicitly dot-prefixed patterns, include_hidden on plain and recursive wildcards, rglob, relative-segment filtering, directory results and no matches.
- This fixture has no symlinks, inaccessible directories, OS hidden attributes, race conditions, unusual encodings or case collisions. No Windows behavior, archive/export/upload workflow, traversal pruning or security boundary was tested. Path return types/prefixes are normalized only for this comparison; other API differences remain.

## Sources
- [Python 3.14 pathlib](https://docs.python.org/3.14/library/pathlib.html): comparison to glob and recursive matching contract.
- [Python 3.14 glob](https://docs.python.org/3.14/library/glob.html): default dot-name handling, root_dir, recursive and include_hidden; version 3.11 addition.
- [Ruff PTH207](https://docs.astral.sh/ruff/rules/glob/): migration guidance warns the APIs are not exact equivalents; its short hidden-directory wording is not treated as an exhaustive flag specification.
- [Why do glob and pathlib differ?](https://stackoverflow.com/questions/49862648/why-do-glob-glob-and-pathlib-path-glob-treat-hidden-files-differently): public expectation mismatch.
- [Include hidden files and folders](https://stackoverflow.com/questions/49047402/python-glob-include-hidden-files-and-folders): older and newer answers; no obsolete impossibility claim adopted.
- [CPython issue 148765](https://github.com/python/cpython/issues/148765): historical include_hidden documentation wording concern, not evidence of a runtime defect or a pending fix here.
