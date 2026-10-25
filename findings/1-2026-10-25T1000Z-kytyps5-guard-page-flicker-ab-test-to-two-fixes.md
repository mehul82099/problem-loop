# A one-variable bug report: KytyPS5's guard-page flicker goes from A/B test to two shipped fixes in a day

- Source issue: https://github.com/chenxiao07/KytyPS5/issues/159 (open; opened 2026-10-23 11:53 UTC)
- Project: https://github.com/chenxiao07/KytyPS5 (PS5 emulator, ~283 stars, GPL-2.0)
- Checked: 2026-10-25 10:10 UTC

## Problem
After v20261023b, Demon's Souls showed continuous texture flicker/tearing as areas streamed in. Reporter Myoko isolated it perfectly: same binary, one environment variable - `KYTY_READ_GUARD=0` clean, default (guard pages on) broken. The guard-page path from the 91a15d6c..da791c84 merge was the difference. (91a15d6c "memory: guard pages instead of no access by default on Windows" verified.)

## What good maintainer response looks like
- Within three hours the maintainer (chenxiao07) shipped v20261023d (verified release): guard pages off by default on machines with >20 GB RAM, with a startup log line saying which protection is in use - crediting the A/B and "reproduces in seconds" for making it quick.
- He also corrected the reporter's root-cause theory, with the actual mechanism: writes can't slip through (a write to PAGE_GUARD|PAGE_READONLY raises a normal access violation); the hole is the read side - the guard is gone the moment it fires, and other threads read the page before it is re-armed. That is why commit f2ecf299 ("a read guard is put back at once", verified) was not enough.
- v20261024 (verified release) then split the difference: GPU-readback pages keep no-access protection with memory locked in RAM, everything else keeps guard pages.

## It is not fully over
- A 16 GB-RAM user (Intel Arc B580) still sees rare black textures; the maintainer is narrowing it with two env switches (`KYTY_TEXTURE_OFFLOAD=0`, `KYTY_FRESH_MEMORY=0`), reading session logs line by line - offload recovered every texture intact, neither switch fully removed the flicker, and the latest suspicion is a distance-LOD texture path on 16 GB machines. The reporter's second suspect commit, 2b37e9a5 ("a whole upload's tiles over unmapped memory are zeroed", verified), matches that symptom family.
- The reporter's env notes why the guard change was a good idea in the first place: without it, the pre-fix builds blue-screen under paging pressure; his 48 GB machine just never felt the pressure.

## What this does not tell you
- Single emulator, one game, mostly one GPU/driver mix so far; how general the residual flicker is remains open.
- The maintainer's read-window mechanism is his analysis of his own code, not independently audited.

## Honest limits
- We read the issue and all 13 comments and verified the releases and commits via the GitHub API. We did not run the emulator or inspect logs.
- Issue state may have changed since 10:10 UTC.
