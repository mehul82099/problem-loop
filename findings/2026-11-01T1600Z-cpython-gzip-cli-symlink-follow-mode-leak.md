# `python -m gzip` follows a symlink at the output name and clobbers its target - and turns a `0600` input into a world-readable output

**Source:** [python/cpython#161088](https://github.com/python/cpython/issues/161088) (open, filed by CPython core dev gpshead with fix PR [#161089](https://github.com/python/cpython/pull/161089) open and unmerged; verified)

## What happened

`python -m gzip` derives the output name from the input name and opens it with plain `"wb"`. Two consequences, both diverging from what gzip(1) does: (1) an existing **symlink** at the output name is followed, so the symlink's *target* gets overwritten while the symlink survives - the reporter's demo has a `report` symlink to a file named `target`, and decompressing `report.gz` leaves `target` holding the new payload; gzip(1) unlinks the old name and creates the output exclusively. (2) The output is created with the **default mode**, so compressing a `0600` private file yields a `0644` (umask-dependent) `.gz` - gzip(1) copies the input's permission bits. Both behaviors reproduce on CPython main with a few lines; the reporter's fix PR makes the CLI replace its output like gzip(1) does.

## Who this bites

- Anyone using the `python -m gzip` CLI in scripts or build pipelines on shared or attacker-influenceable filesystems: a pre-planted symlink at the predictable output name (`<input>.gz`, or the stripped name for `-d`) redirects the write into a file the user never meant to touch - config files, authorized_keys-style targets, build artifacts. It's the classic clobber-via-symlink shape, in a stdlib CLI people reach for as "the Python way" to gzip in a pinch.
- The mode leak is the quieter half: compressing secrets-bearing files (key exports, dumps) silently strips their restrictive permissions, and nothing in the output warns.

## Limits

- Reporter mechanism and demo only (repo ~77k stars, though the reporter is a core dev and association MEMBER is verified); I verified the linked PR is open and unmerged but did not run the repro.
- Demonstrated on Linux; symlink semantics on Windows differ and are not covered by the report.
- Not a network-exploitable vulnerability - it needs a local or write-access attacker to plant the symlink, or an unlucky pre-existing link - so impact is environment-dependent; the fix PR is not yet merged.
