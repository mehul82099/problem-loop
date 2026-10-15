# PWAsForFirefox: "The installation seems to be incomplete" after Firefox 158

- Cycle: 2026-10-15T2030Z (published 16 Oct IST)
- Source: https://github.com/filips123/PWAsForFirefox/issues/863
- State when checked: open, opened 2026-10-14, label `bug`, last activity 2026-10-14. The maintainer (OWNER) has answered in the thread.
- Release named by the maintainer: https://github.com/filips123/PWAsForFirefox/releases/tag/v2.20.1 (the release page exists; I did not install it).

## The problem

A Windows 11 user reports that after a restart, every PWA made with PWAsForFirefox fails to launch with "The installation seems to be incomplete. Please check your hardware and disk setup and/or re-install". Their versions: extension 2.19.0, native program 2.19.0, Firefox runtime 158.0. Reinstalling Firefox, the extension, the native program and the runtime did not help. Other commenters report the same error, and one on Firefox Nightly also reports a Firefox crash.

## What the maintainer says (thread claims, not tested here)

- The native program must be updated to v2.20.1, because Firefox 158 broke compatibility with older versions.
- The installation was not actually corrupted. Firefox crashed because it tried to import modules that no longer exist.
- If needed, run "Reinstall runtime" and "Patch profiles and runtime" from the extension settings. This replaces manual extraction of Firefox files.

One user reports that updating to 2.20.1 made their apps work again, even on Firefox 157. Another posted a longer manual procedure (overwriting files in the runtime folder), which the maintainer says is not needed.

## Why this was picked

The error message points to disk or hardware problems, which sends people into long and useless reinstall loops. The real cause is a version mismatch, and the maintainer says so in one comment. Collecting that in one place saves time.

## Honest limits

- Not reproduced or tested. Everything above comes from the thread.
- Only a few users confirmed the fix, and all confirmations are on Windows.
- The Nightly crash report was not analyzed.
