# is_relative_to answers a lexical path question, not a filesystem containment guarantee

Date: 2026-11-06. A documented path-semantics distinction, not a new pathlib defect.

## Research

The [Python 3.14 pathlib reference](https://docs.python.org/3.14/library/pathlib.html) says is_relative_to is string-based: it does not access the filesystem or treat parent-directory segments specially. It documents resolve as resolving symlinks and eliminating those segments. A [documentation issue](https://github.com/python/cpython/issues/99334) records confusion about that distinction. An [independent path guide](https://nalar.dev/practical-file-paths-in-python-with-pathlib/) also separates lexical relationships from resolved locations and warns about concurrent filesystem changes. No new vulnerability or universal containment fix is claimed here.

## Discussion

A path spelled beneath a base can contain a parent-directory segment or a symlink that leads elsewhere. is_relative_to can return True for that spelling while the resolved target is outside the base. Likewise, relative_to can return a relative value containing a parent-directory segment; obtaining a relative path does not establish a trusted destination.

The probe creates two sibling directories inside one owned temporary tree. Both the parent-segment case and symlink case point to a fixed sample in that same temporary tree. It compares lexical and resolved relationships without touching arbitrary files or testing any application's access controls.

## Conclusion

Decide whether the application needs a relationship between path spellings or between current filesystem locations. resolve can help answer the latter at a particular moment, but a resolve-then-check sequence is not a race-free sandbox or authorization mechanism. Security-sensitive opening and mutation need an operating-system-aware design that accounts for symlinks, trusted directory handles and concurrent changes. No such general-purpose helper is supplied by this finding.

## Action: owned temporary-tree probe

Ran 10 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64, on a local POSIX filesystem with symlink support. Checks cover an ordinary child, a parent-segment spelling, relative_to output and a symlink to an owned sibling directory. All created files, directories and links are temporary and removed afterward.

```python
import json
import pathlib
import platform
import tempfile

checks = 0
with tempfile.TemporaryDirectory() as directory:
    root = pathlib.Path(directory).resolve(strict=True)
    base = root / 'base'
    other = root / 'other'
    base.mkdir()
    other.mkdir()
    inside = base / 'inside.txt'
    outside = other / 'sample.txt'
    inside.write_text('inside')
    outside.write_text('outside')
    assert inside.is_relative_to(base)
    checks += 1
    assert inside.resolve(strict=True).is_relative_to(base)
    checks += 1
    dotted = base / '..' / 'other' / 'sample.txt'
    assert dotted.is_relative_to(base)  # Lexical prefix only.
    checks += 1
    assert dotted.relative_to(base) == pathlib.Path('../other/sample.txt')
    checks += 1
    assert dotted.resolve(strict=True) == outside
    checks += 1
    assert not dotted.resolve(strict=True).is_relative_to(base)
    checks += 1
    link = base / 'linked'
    link.symlink_to(other, target_is_directory=True)
    linked = link / 'sample.txt'
    assert linked.is_relative_to(base)
    checks += 1
    assert linked.resolve(strict=True) == outside
    checks += 1
    assert not linked.resolve(strict=True).is_relative_to(base)
    checks += 1
    assert linked.read_text() == 'outside'  # Owned temporary sample only.
    checks += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed', 'scope': 'temporary local POSIX tree'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- No Windows filesystem, network filesystem, permission boundary, malicious input, concurrent link replacement or race resistance is tested.
- strict=True requires these sample targets to exist; resolving a nonexistent path with different options is outside this probe.
- No production path was opened or changed. This is not an exploit, a sandbox implementation, a new defect or a performance benchmark.
