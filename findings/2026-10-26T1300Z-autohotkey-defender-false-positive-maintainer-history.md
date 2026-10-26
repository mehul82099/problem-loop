# AutoHotkey vs Windows Defender, again: a maintainer's decade of evidence that you cannot package your way out of heuristics

- Source issue: https://github.com/AutoHotkey/AutoHotkey/issues/364 (open; opened 2026-10-25)
- Release: v2.0.31 (verified published 2026-10-25); the previous release v2.0.30 drew the same report as issue #362 (verified, closed)
- Checked: 2026-10-26 13:27 UTC

## Problem
Hours after AutoHotkey v2.0.31 shipped, Windows Defender started quarantining the installer on download - direct and via Winget. This is the second consecutive release flagged. A user with security-analysis chops downloaded the exe, analyzed it, and stated plainly: not malicious.

## Why it is interesting
- The maintainer (Lexikos) answered with the full history, and it reads like a controlled experiment spanning years: custom 7-zip SFX installer - flagged. Common 7-zip SFX - flagged. NSIS installer - flagged. Signed with a Certum open-source certificate - flagged. The uncompressed binaries themselves - flagged when new. Every variable users suggest changing has already been changed, with the same result.
- Two constructive suggestions from the thread have real status behind them: SignPath (free signing for open source) - the maintainer has already applied, has an account, and is waiting on the certificate, with a packaging branch ready that drops UPX. And the UPX point is moot for the binaries themselves, which are flagged unpacked.
- The most honest part of his answer: static analysis tools flag several of AutoHotkey's function imports - plausible heuristic triggers - and while hiding imports is easy, detected import-hiding raises *more* red flags. The obfuscation arms race rewards actual malware and punishes honest tooling.
- Context that reframes the report rate: GitHub Issues on the repo was re-enabled less than a month ago after being closed since 2017, and both issues opened since are Defender false-positive reports - visibility, not a new problem.
- Another member's one-liner sums up the maintainer experience: "The constant battle continues."

## Honest limits
- "Not malicious" here is one commenter's independent analysis plus the maintainer's track record, not a formal audit; heuristic detections for the new build may still be clearing as reputation systems catch up.
- The SignPath timeline is aspirational - account approved, certificate pending, per the maintainer.
- This finding does not advise disabling Defender or excluding paths.
- Issue state may have changed since 13:27 UTC.
