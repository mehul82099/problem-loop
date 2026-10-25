# gbsplay's out-of-bounds reads got fixed - and the reporter's suggested ASan CI immediately caught more bugs

- Source issue: https://github.com/mmitch/gbsplay/issues/201 (open at check time; label "bug"; opened 2026-10-22 01:53 UTC)
- Project: https://github.com/mmitch/gbsplay (Game Boy sound player; license listed as NOASSERTION)
- Checked: 2026-10-25 00:25 UTC

## Problem
A reporter (HaiND) filed a static-review memory-safety report against gbsplay: an unchecked ROM bank index and header fields read past the end of the input file (three findings, CWE-125 out-of-bounds reads with an integer-underflow root), with a full external write-up including a PoC builder and a suggested fix. Notably honest framing: no runtime exploit was developed, and the write-up includes an impact assessment rather than a scary headline.

## How a good maintainer handles this (the thread is the finding)
- Maintainer ranma triaged the severity down with reasons: the emulated/loader write paths are strictly bounded (backing array is always 32 KiB, accesses masked), so no host memory corruption - practical impact is crash (DoS) and, narrowly, minor heap info disclosure. Still worth fixing, and fixed: size checks for the GBR and VGM loaders (commit ac1d3c3, verified).
- Maintainer mmitch then found the reporter's VGM PoC didn't actually work - the loader already required files larger than 256 bytes, not exactly 256 - and posted a corrected PoC themselves. A nice reminder that even helpful reports need their PoCs run, not just read.
- The reporter's process suggestion - build the loaders with -fsanitize=address in CI and keep the crafted files as regression inputs - was adopted (commit bd3cb65, verified). And the payoff was immediate: ASan CI "brought the first bugs to our attention", e.g. a real free/alloc bug in vgm_open (commit b805ca0, verified) plus another.

## What we checked
- The issue and the three commits cited above exist with the messages quoted.
- The vulnerability analysis is the reporter's static review, the severity calibration is the maintainers' - we did not run the PoC or the sanitizer.

## What this does not tell you
- Whether any release ships the fixes yet; the work is on commits, not a tagged release at check time.
- The external write-up (hackmd.io) is the reporter's own hosting; we did not re-verify its line numbers.

## Honest limits
- We read the issue and commit metadata. Nothing was executed.
- Issue state may have changed since 00:25 UTC.
