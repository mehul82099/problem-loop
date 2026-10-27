# The patch release that shipped the broken build it was supposed to replace

- Source issue: https://github.com/rmcrackan/Libation/issues/2118 (open; opened 2026-10-27)
- Verified: releases v14.2.3 (2026-10-26), v14.2.4 (2026-10-27); prior fix PR #2116 (merged)
- Project: rmcrackan/Libation (~6.4k stars; open-source Audible library manager)
- Checked: 2026-10-27 15:00 UTC

## Problem
Libation 14.2.3 crashed instantly on launch for macOS Apple Silicon users (fixed in PR #2116). The maintainers shipped 14.2.4 within hours - the release notes say it "Fix macOS launch crash from SkiaSharp mismatch." Users downloaded it, and it crashed exactly the same way. The smoking gun is in the reporter's log: the package labeled 14.2.4 reports assembly version 14.2.3.0. The fix release's macOS arm64 build appears to contain the previous, still-broken binaries. Maintainer wtanksleyjr confirms in the thread: "It's a build error, you can wait for the patched version or downgrade to 14.2.2."

## Why it is interesting
- A tidy parable about patch releases under pressure. The crash was diagnosed (SkiaSharp version mismatch), the fix was merged, the release was cut - and the artifact that shipped was not the artifact that was built. Everything about the process looked right except the one thing that mattered: what bytes actually went into the dmg.
- The users did the QA. The reporter attached a crash log, a second commenter corroborated, and the assembly version string in the log turned "still crashes" from a vague complaint into a precise diagnosis: wrong binary in the package. That is a better bug report than most teams get from their own CI.
- It shows where version numbers actually live. The marketing version (14.2.4, on the release page) and the assembly version (14.2.3.0, baked into the binary) disagreed, and the binary was telling the truth. Any release pipeline that lets those two diverge has a hole in it.
- Response was fast and honest: within about twelve hours of the report, the maintainer confirmed the build error and gave a clean workaround (downgrade to 14.2.2) instead of asking users to debug a package the team already knew was wrong.

## Honest limits
- The "wrong binary in the package" reading rests on the reporter's log line (assembly 14.2.3.0 in the 14.2.4 download) plus the maintainer's "build error" confirmation; the release artifact itself was not independently inspected byte-for-byte.
- Whether other 14.2.4 artifacts (x64 dmg, Linux, Windows) are affected is not established; reports so far are macOS arm64.
- Reporter's environment is macOS 27.0.1; OS-specific factors beyond the packaging error are not ruled out.
- Issue state may have changed since 15:00 UTC.
