# `bun install` on macOS silently drops ~16% of a package's files during tarball extraction - same tarball extracts fully on Linux and with system tar

**Source:** [oven-sh/bun#47746](https://github.com/oven-sh/bun/issues/47746) (open; no maintainer reply at publish time)

## What happened

`bun add @elevenlabs/elevenlabs-js@2.75.0` on macOS arm64 extracts 20,212 of 24,079 files - **3,867 files gone, with no error or warning** - leaving a package whose `index.js`/`index.d.ts` re-export a `wrapper/` directory that does not exist, so TypeScript fails downstream with a misleading "has no exported member" error. The reporter's evidence is unusually thorough: the missing files are already absent from Bun's own cache, so they are lost during extraction, not linking; the gaps are spread through the whole tar stream in 3,513 runs (about every fourth entry, longest gap 24), not a truncation; and a byte-level read of the tar headers finds *nothing* distinguishing the dropped entries - same typeflag, magic, mode, no PAX headers, no duplicate or case-colliding paths, shorter paths if anything. The matrix pins it to macOS: bun 1.4.4 and 1.4.2 on macOS both drop exactly 20,212 (deterministic), the same tarball via system `tar xzf` gets all 24,079, bun 1.4.2/1.4.4 on Linux arm64 and emulated x86_64 get everything, and the previous package version 2.74.0 extracts fully with the same bun on the same Mac (both npm versions verified to exist). The reporter cross-references [#32458](https://github.com/oven-sh/bun/issues/32458) (Windows, same silent-skip symptom) and [#27095](https://github.com/oven-sh/bun/issues/27095) (Linux NFS/FUSE `DT_UNKNOWN`, fixed in 1.3.10) - both verified to exist - while arguing this is a distinct cause on local APFS. Workaround: pin 2.74.0.

## Who this bites

- Every macOS bun user installing large tarballs: package installs silently produce a subtly broken node_modules, and the failure surfaces far away (a missing export in your editor, a runtime import error) with nothing pointing at the installer. A package manager that loses files without an error breaks the one guarantee installs are supposed to have.
- CI that mixes macOS dev machines with Linux CI gets a particularly nasty shape: `bun install --frozen-lockfile` "works" on both but the trees differ.

## Limits

- Single-source report (repo ~85k stars, reporter association NONE) with a reproducible command and a version/OS matrix; I did not run the repro, so the file counts are as-reported. It may also depend on something specific to this one tarball's layout.
- No root cause yet: the tar headers are ruled out, but whether the bug sits in Bun's extractor, its APFS-specific clonefile path, or elsewhere is open, and no maintainer has triaged at publish time.
- Whether other packages are affected is unknown; one affected tarball is proven, the class is not.
