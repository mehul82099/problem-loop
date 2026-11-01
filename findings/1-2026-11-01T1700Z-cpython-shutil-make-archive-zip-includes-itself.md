# `shutil.make_archive('backup', 'zip')` adds the zip it's writing to itself - and a symlink can make it grow until the disk is full

**Source:** [python/cpython#161112](https://github.com/python/cpython/issues/161112) (open, CPython core dev gpshead, MEMBER verified; fix PR [#161113](https://github.com/python/cpython/pull/161113) open and unmerged; same fix landed in zipapp via gh-104527, verified closed)

## What happened

With the `"zip"` format, `shutil.make_archive()` walks the tree and writes every regular file it finds - including the archive itself, when the output path sits inside the directory being archived (the natural `make_archive('backup', 'zip')` in the current directory). `_make_zipfile()` has no self-skip; the tar formats already skip their archive via `TarFile.add()`, and zipapp got the same fix in gh-104527. The reporter's four-line repro shows `test.zip` containing a truncated copy of itself as its first member. The worse shape: if a **symlink** in the tree points at the archive and is reached after some data has been flushed, the archiver chases its own output - the file grows until the disk fills or the OS refuses with `Errno 27 File too large`.

## Who this bites

- Anyone doing the obvious thing - `shutil.make_archive('backup', 'zip', '.')` or packaging a build directory with the output dropped inside it: the archive silently contains a truncated copy of itself, inflating size and confusing downstream consumers, with no error.
- The symlink variant turns a convenience API into a disk-fill: one malicious or accidental symlink inside a tree being archived (think: packaging a user-upload directory) and the process writes until the filesystem is full.

## Limits

- Reporter mechanism and repro only (repo ~77k stars, but association MEMBER verified); I verified the linked PR and the zipapp precedent but did not run the repro.
- Demonstrated on Linux/main; the disk-fill variant depends on symlink resolution order within the walk, so its trigger is layout-dependent.
- Fix PR is open and unmerged, so no released version contains the guard yet.
