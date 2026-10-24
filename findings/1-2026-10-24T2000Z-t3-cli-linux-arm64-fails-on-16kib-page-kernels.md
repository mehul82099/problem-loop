# T3's linux-arm64 CLI cannot even start on 16 KiB-page kernels (Raspberry Pi 5, Asahi Linux) - and it is on the stable channel too

- Source issue: https://github.com/pingdotgg/t3code/issues/23433 (open at check time; opened 2026-10-22 07:26 UTC; active thread)
- Fix PR: https://github.com/pingdotgg/t3code/pull/23443 (open, unmerged: "restore ARM64 CLI support on larger-page kernels")
- Project: https://github.com/pingdotgg/t3code (MIT, about 30k stars; stable v0.1.2 released 2026-10-22)
- Checked: 2026-10-24 20:20 UTC

## Problem
The linux-arm64 build of the t3 CLI exits 139 (SIGSEGV from a failed execve - the kernel returns EINVAL and the launcher swallows it, so via npx it just prints nothing) on any arm64 host with 16 KiB memory pages. That covers the Raspberry Pi 5's default kernel and Asahi Linux on Apple Silicon - and it is not just nightly: the stable v0.1.2 release fails the same way, while v0.1.1 works. Still present in the newest nightly at check time.

## Root cause (reporter's binary analysis, detailed and consistent)
The reporter compared readelf output between the last working and first broken builds: two LOAD segments added to the binary during Node's SEA (single-executable) injection are aligned to 4 KiB (0x1000); a 16 KiB-page kernel cannot map them. The earlier build had every LOAD segment 64 KiB-aligned. A later commenter pinpoints the same two segments as the ones LIEF adds during injection, and shows the PHDR segment overlapping a 16 KiB page with .bss. The analysis is theirs (multiple users independently reproduced the readelf signature on later nightlies), but it is specific, checkable, and uncontested in the thread.

## What the thread says
- Confirmations across Pi 5 (rpi-2712 kernel), Asahi on M1/M5, and a Docker sandbox on Apple Silicon - stable, preview, and nightly channels all affected.
- Two local workarounds were posted (one rewriting ELF virtual addresses, one extracting the embedded JS bundle and running it with system Node). Both are user-contributed binary surgery; we are deliberately not relaying the steps - wait for the official fix unless you know exactly what you are doing.
- The reporter asks the right process question: a pipeline test should catch this mechanically (exec the built binary on a 16 KiB-page host, or assert LOAD alignment).
- The fix PR (#23443) exists but is unmerged at check time.

## What we checked
- The issue, the open fix PR, and the v0.1.2 stable release date exist as described.
- The readelf evidence and repros are the commenters'; we did not run the binary.

## What this does not tell you
- When the fix lands; until then, linux-arm64 users on 16 KiB kernels stay on v0.1.1 (the thread's consistent report: 0.1.1 works).
- Whether the x86_64 build or other SEA-packaged CLIs from the same toolchain share the alignment bug is not addressed in the thread.

## Honest limits
- We read the issue and the PR listing. Nothing was executed.
- Issue state may have changed since 20:20 UTC.
