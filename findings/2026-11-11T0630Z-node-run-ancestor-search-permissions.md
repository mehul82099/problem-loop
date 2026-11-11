# node --run can abort before a script when an ancestor node_modules cannot be searched

Date: 2026-11-11 (IST). Independent reproduction of public issue 67269, not an original defect discovery.

## Research

[Node issue 67269](https://github.com/nodejs/node/issues/67269) reports an uncaught filesystem exception on a development build on macOS. The [proposed fix 67270](https://github.com/nodejs/node/pull/67270) was still **Open** on the live PR page at inspection. An open patch is not a shipped fix.

The [v22.23.4 CLI reference](https://nodejs.org/download/release/v22.23.4/docs/api/cli.html) says --run traverses ancestors and prepends their node_modules/.bin directories when they are directories. The [exact tagged implementation](https://github.com/nodejs/node/blob/v22.23.4/src/node_task_runner.cc), lines 219-266 inspected, calls the throwing is_directory overload while building that path, before the script is launched. The [C++ filesystem reference](https://en.cppreference.com/w/cpp/filesystem/is_directory) distinguishes throwing overloads from the error_code overload. The [Python subprocess reference](https://docs.python.org/3.14/library/subprocess.html) explains negative return codes for signal termination on POSIX.

## Discussion

A directory being readable and being searchable are different permissions. The local matrix names exact modes instead of calling all failures unreadable-directory failures: 0400 is owner-readable but has no search bit. Both 0000 and 0400 on node_modules caused SIGABRT before the fixed script marker was printed. Search-only 0100 and read/write/search 0700 succeeded when .bin was absent.

This also reproduced when the inaccessible node_modules was one directory above a project with its own valid package.json. The installed implementation continues building ancestor PATH entries rather than stopping as soon as it finds that package file. A valid local script is therefore not enough to avoid the ancestor filesystem probe.

## Conclusion

On the tested runtime, investigate search permissions on node_modules in both the project and its ancestors when --run aborts before script output. Do not conclude that the script itself crashed. Missing node_modules and a missing .bin are successful controls here; missing paths alone do not explain the abort.

This is diagnosis, not a recommendation to loosen permissions or change package managers. No existing directory permissions are changed by this diagnostic, and no patch or version upgrade is claimed tested. The original issue's deleted-current-directory case is not executed here.

## Action

**38 assertions passed across 10 child processes** on **Node v22.23.4, Linux**, with **CPython 3.10.12**, running as non-root uid 1001. The same fixed `echo fixture-ok` package script is used throughout. Four permission-denied cases terminated with Python returncode **-6 (SIGABRT)**, no script marker, and filesystem_error/Permission denied diagnostics. Six controls exited 0 and printed the marker.

| Placement of node_modules | Mode | Expected and observed |
| --- | --- | --- |
| project | 0000 | SIGABRT, marker absent |
| project | 0400 | SIGABRT, marker absent |
| project | 0100 | exit 0, marker printed |
| project | 0700 | exit 0, marker printed |
| one ancestor | 0000 | SIGABRT, marker absent |
| one ancestor | 0400 | SIGABRT, marker absent |
| one ancestor | 0100 | exit 0, marker printed |
| one ancestor | 0700 | exit 0, marker printed |
| missing node_modules | n/a | exit 0, marker printed |
| existing node_modules/.bin | normal created mode | exit 0, marker printed |

Run the original MIT diagnostic below with `python run-permissions.py`. It requires a non-root POSIX user and Node on PATH. It creates only unique temporary fixtures, restores its own directory modes in finally, and cleans them up. Every Node child has a four-second timeout; core dumps are disabled in those children with RLIMIT_CORE. It does not install packages, read private projects, contact a server, or execute code supplied by an external report. The fixed echo command assumes the POSIX shell used by --run.

```python
# Original diagnostic, MIT licensed. POSIX only; synthetic temporary files.
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import tempfile
import sys

if os.name != 'posix' or os.geteuid() == 0:
    raise SystemExit('Requires a non-root POSIX user; no results asserted.')
node = shutil.which('node')
if not node:
    raise SystemExit('Node executable required.')
version = subprocess.run([node, '--version'], check=True, text=True, capture_output=True).stdout.strip()

def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

results = []
checks = 0
for placement in ('project', 'ancestor'):
    for mode in (0o000, 0o400, 0o100, 0o700):
        with tempfile.TemporaryDirectory(prefix='node-run-perms-') as tmp:
            root = Path(tmp)
            project = root / 'project'
            project.mkdir()
            (project / 'package.json').write_text(json.dumps({'scripts': {'hi': 'echo fixture-ok'}}))
            modules = (project if placement == 'project' else root) / 'node_modules'
            modules.mkdir()
            modules.chmod(mode)
            try:
                r = subprocess.run([node, '--run', 'hi'], cwd=project,
                                   capture_output=True, text=True, timeout=4,
                                   preexec_fn=no_core)
            finally:
                modules.chmod(0o700)
            denied = mode in (0o000, 0o400)
            assert r.returncode == (-signal.SIGABRT if denied else 0), (placement, mode, r)
            assert r.stdout.strip() == ('' if denied else 'fixture-ok')
            assert ('Permission denied' in r.stderr) == denied
            assert ('filesystem_error' in r.stderr) == denied
            checks += 4
            results.append({'placement': placement, 'mode': oct(mode),
                            'returncode': r.returncode, 'marker': r.stdout.strip(),
                            'permission_denied': denied})
# Ordinary missing node_modules, then an existing .bin, both execute the script.
for present in (False, True):
    with tempfile.TemporaryDirectory(prefix='node-run-control-') as tmp:
        root = Path(tmp)
        (root / 'package.json').write_text(json.dumps({'scripts': {'hi': 'echo fixture-ok'}}))
        if present:
            (root / 'node_modules' / '.bin').mkdir(parents=True)
        r = subprocess.run([node, '--run', 'hi'], cwd=root, capture_output=True,
                           text=True, timeout=4, preexec_fn=no_core)
        assert r.returncode == 0
        assert r.stdout.strip() == 'fixture-ok'
        assert r.stderr == ''
        checks += 3
        results.append({'control': 'present-bin' if present else 'missing-modules', 'returncode': r.returncode})
print(json.dumps({'node': version, 'python': sys.version.split()[0],
                  'platform': sys.platform, 'euid': os.geteuid(),
                  'checks': checks, 'children': len(results), 'results': results}, indent=2))
```

## Publisher and limits

Only the stated installed Linux/Node build was reproduced. Filesystem exception text, permissions and signal behavior can differ by platform/build. The diagnostic deliberately asserts observed behavior and will fail, rather than label a fixed runtime as reproduced. It does not cover ACLs, root execution, Windows, npm run, deleted working directories or arbitrary script execution. Python's -6 returncode is reported directly; a shell's conventional 134 representation was not used as local evidence.
