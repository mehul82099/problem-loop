# pathlib replaces the last suffix, not a compound filename extension

Date: 2026-11-05. A documented filename-policy distinction, not a new pathlib defect.

## Research

The [pathlib reference](https://docs.python.org/3/library/pathlib.html) defines suffix as the final dot-separated portion and stem as the name without that suffix. with_suffix replaces that final suffix. A [Python Help discussion](https://discuss.python.org/t/correct-way-to-remove-all-file-extensions-from-a-path-with-pathlib/6711) asks how to remove multiple extensions and warns that dots may be part of the intended filename. A [developer question](https://stackoverflow.com/questions/31890341/clean-way-to-get-the-true-stem-of-a-path-object) similarly asks for a "true" stem. Neither implies that all dotted segments are disposable file extensions.

## Discussion

For `release.v1.tar.gz`, stem is `release.v1.tar`, and with_suffix('.zip') produces `release.v1.tar.zip`. The suffixes list includes `.v1` as well as `.tar` and `.gz`; it is a syntactic decomposition, not file-format detection. Blindly stripping every suffix would also discard the version segment.

If the application specifically wants to replace an exact `.tar.gz` ending, encode that policy on the final name and use with_name to retain the parent. The helper below accepts only that case-sensitive ending and a nonempty basename. It preserves earlier dots. It deliberately rejects uppercase variants rather than guessing a case-normalization policy.

## Conclusion

Decide which exact filename endings belong to the application's format policy before transforming names. Use with_suffix for the final suffix, and an explicit compound-ending rule when the format calls for one. Do not treat a computed output path as proof of file contents or as a completed archive conversion.

## Action: pure-path compound-ending probe

Ran 22 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Both PurePosixPath and PureWindowsPath string semantics are checked. The helper returns a new pure path value only. It does not read, write, rename, compress or convert a file.

```python
import json
import platform
from pathlib import PurePosixPath, PureWindowsPath

# Deliberately narrow, case-sensitive filename policy, not format detection.
def tar_gz_to_zip(path):
    if not path.name.endswith('.tar.gz'):
        raise ValueError('expected an exact .tar.gz filename ending')
    base = path.name.removesuffix('.tar.gz')
    if not base:
        raise ValueError('expected a nonempty basename')
    return path.with_name(base + '.zip')

checks = 0
for cls, directory in [(PurePosixPath, '/tmp/dotted.dir'),
                       (PureWindowsPath, 'C:/dotted.dir')]:
    p = cls(directory) / 'release.v1.tar.gz'
    assert p.suffix == '.gz'
    assert p.suffixes == ['.v1', '.tar', '.gz']
    assert p.stem == 'release.v1.tar'
    assert p.with_suffix('.zip').name == 'release.v1.tar.zip'
    assert p.with_suffix('').name == 'release.v1.tar'
    converted = tar_gz_to_zip(p)
    assert converted.name == 'release.v1.zip'
    assert converted.parent == p.parent
    assert p.name == 'release.v1.tar.gz'  # Pure path value unchanged.
    checks += 8
    for name in ['report.v1.txt', 'archive.TAR.GZ', '.tar.gz']:
        try:
            tar_gz_to_zip(cls(directory) / name)
        except ValueError:
            checks += 1
        else:
            raise AssertionError('expected policy rejection')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed', 'scope': 'pure path strings only'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- The helper demonstrates one filename policy, not a general extension parser. It does not validate archive bytes, path safety, collisions or filesystem support.
- PureWindowsPath checks are string-level tests on Linux, not Windows filesystem validation.
- Trailing-dot version changes are covered by the repository's earlier pathlib finding and are not part of this increment. No actual rename, archive conversion, new defect or performance claim is made.
