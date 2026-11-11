# A finished glob is not proof of a complete file inventory

Date: 2026-11-11 (IST). Tested documented behavior, not a new Python defect.

## Research

[CPython issue 146646](https://github.com/python/cpython/issues/146646) asked for documentation of silently ignored scan errors. It is closed, and the [documentation PR 147996](https://github.com/python/cpython/pull/147996) is merged. This is not an unresolved runtime bug or a pending fix.

Current versioned [glob documentation](https://docs.python.org/3.14/library/glob.html) and [pathlib documentation](https://docs.python.org/3.14/library/pathlib.html) explicitly say filesystem-scanning OSError exceptions are suppressed, including PermissionError. The [tagged 3.14.9 glob source](https://github.com/python/cpython/blob/v3.14.9/Lib/glob.py) wraps directory scanning in OSError handlers. A normal end of iteration therefore does not certify that all matching paths were observable.

The [os.walk reference](https://docs.python.org/3.14/library/os.html) says its default also ignores scandir errors; onerror can record them or re-raise. Path.walk has the corresponding on_error callback. Switching from glob to a default walker alone does not add error reporting.

## Discussion

This fixture compares glob, iglob, Path.glob and Path.rglob, using recursive txt patterns with no dot-names or symlinks. All four return the same partial set when one child directory has mode 0000. A separate denied-root scan and a genuinely empty directory both return an empty set. These are not equivalent inventory states, despite identical matches.

With error callbacks, os.walk and Path.walk return the accessible matches and report the inaccessible directory. An os.walk callback that re-raises stops traversal with PermissionError. The diagnostic checks that path and EACCES, not merely an error count. Restoring permissions restores the full two-file set.

## Conclusion

If omission matters, carry scan errors with the matched paths or choose an explicit fail-on-scan-error policy. Do not equate [] with a proven absence, or successful iterator exhaustion with complete coverage. Error-aware traversal is still not a snapshot: concurrent changes, symlinks, later file opens, explicit exclusions and inaccessible mounts need their own policies. A zero-error traversal is not an access-control or backup-integrity guarantee.

## Action

**55 assertions passed independently on CPython 3.13.17 and 3.14.9, Linux, as a non-root user.** The five states are readable, denied child, restored, denied root and truly empty. Each checks four glob surfaces, default os.walk, reporting os.walk, and reporting Path.walk. Denied cases also check PermissionError, EACCES, exact failed path and os.walk re-raise behavior.

| State | Matches from each glob surface and walker | Errors from each reporting walker |
| --- | --- | --- |
| readable | public/visible.txt, blocked/inside.txt | 0 |
| denied child | public/visible.txt | 1, blocked directory |
| restored | public/visible.txt, blocked/inside.txt | 0 |
| denied root | empty | 1, root directory |
| truly empty | empty | 0 |

Default os.walk has no error callback in this test, so its partial result alone carries no failure signal. Results use sets; no traversal order is assumed. Original code is MIT licensed. Run as `python glob-partial.py` without -O so assertions remain active. It creates only unique temporary fixtures, modifies only their modes, and restores modes in finally before automatic cleanup. It refuses root and non-POSIX execution rather than falsely claiming permission errors were reproduced. There is no private filesystem scan, network, dependency or existing-directory permission change.

```python
# Original diagnostic, MIT licensed. Non-root POSIX, temporary fixtures only.
import errno
import glob
import json
import os
from pathlib import Path
import platform
from tempfile import TemporaryDirectory

if os.name != 'posix' or os.geteuid() == 0:
    raise SystemExit('Requires a non-root POSIX user; no results asserted.')
checks = 0
results = []

def check(condition):
    global checks
    assert condition
    checks += 1

def scan(root, expected, failed=None):
    queries = {
        'glob': lambda: set(glob.glob('**/*.txt', root_dir=root, recursive=True)),
        'iglob': lambda: set(glob.iglob('**/*.txt', root_dir=root, recursive=True)),
        'Path.glob': lambda: {p.relative_to(root).as_posix() for p in root.glob('**/*.txt')},
        'Path.rglob': lambda: {p.relative_to(root).as_posix() for p in root.rglob('*.txt')},
    }
    for name, query in queries.items():
        actual = query()
        check(actual == expected)
    # Default walkers ignore scan errors too.
    plain = {str((Path(d) / f).relative_to(root)) for d, _, fs in os.walk(root) for f in fs if f.endswith('.txt')}
    check(plain == expected)
    errors = []
    reported = {str((Path(d) / f).relative_to(root)) for d, _, fs in os.walk(root, onerror=errors.append) for f in fs if f.endswith('.txt')}
    check(reported == expected)
    check(len(errors) == (1 if failed else 0))
    if failed:
        check(isinstance(errors[0], PermissionError))
        check(errors[0].errno == errno.EACCES)
        check(Path(errors[0].filename) == failed)
        def stop(error):
            raise error
        try:
            list(os.walk(root, onerror=stop))
        except PermissionError as error:
            check(Path(error.filename) == failed)
        else:
            raise AssertionError('error-aware walk did not fail')
    path_errors = []
    path_reported = {(d / f).relative_to(root).as_posix() for d, _, fs in root.walk(on_error=path_errors.append) for f in fs if f.endswith('.txt')}
    check(path_reported == expected)
    check(len(path_errors) == (1 if failed else 0))
    if failed:
        check(Path(path_errors[0].filename) == failed)
    return {'matches': sorted(expected), 'os_walk_errors': len(errors), 'path_walk_errors': len(path_errors)}

with TemporaryDirectory(prefix='glob-partial-') as tmp:
    root = Path(tmp)
    (root / 'public').mkdir()
    (root / 'blocked').mkdir()
    for name in ('public/visible.txt', 'blocked/inside.txt'):
        (root / name).write_text('fixture', encoding='utf-8')
    results.append({'state': 'readable', **scan(root, {'public/visible.txt', 'blocked/inside.txt'})})
    (root / 'blocked').chmod(0)
    try:
        results.append({'state': 'child-denied', **scan(root, {'public/visible.txt'}, root / 'blocked')})
    finally:
        (root / 'blocked').chmod(0o700)
    results.append({'state': 'restored', **scan(root, {'public/visible.txt', 'blocked/inside.txt'})})
    root.chmod(0)
    try:
        results.append({'state': 'root-denied', **scan(root, set(), root)})
    finally:
        root.chmod(0o700)
with TemporaryDirectory(prefix='glob-empty-') as tmp:
    results.append({'state': 'empty', **scan(Path(tmp), set())})
print(json.dumps({'python': platform.python_version(), 'platform': platform.system(), 'checks': checks, 'results': results}, indent=2))
```

## Publisher and limits

Permission behavior was tested only on the stated Linux builds with mode 0000 and plain files/directories. ACLs, root, Windows, symlinks, dot-name policy, arbitrary patterns, races, remote filesystems and read failures after traversal are not tested. The suffix filter used with walkers is specific to this txt fixture, not a replacement glob implementation. The repository's earlier dot-name finding covers selection differences, not the scan-error reporting tested here.
