# The wait cursor that locked people out: KeePassXC's macOS crash and the same-version re-spin fix

- Source issue: https://github.com/keepassxreboot/keepassxc/issues/13909 (closed as duplicate of #13822)
- Root issue: https://github.com/keepassxreboot/keepassxc/issues/13822 (closed; platform: macOS, upstream)
- Upstream Qt bug: https://qt-project.atlassian.net/browse/QTBUG-147602 (per maintainer comment)
- Project: keepassxreboot/keepassxc (~29.6k stars)
- Checked: 2026-10-28 18:20 UTC

## Problem
KeePassXC 2.8.0 started crashing on macOS the moment you typed anything into the unlock dialog and hit Enter - for a password manager, the one screen it cannot afford to fail on. Reports came in across three macOS versions (Sequoia 15.8.2, Tahoe 26.7.2, and "macOS 27.2"), all on KeePassXC 2.8.0 with Qt 6.11.1, all after OS updates. The database was fine; other apps opened it. A maintainer (phoerious, MEMBER) closed the duplicate within hours with the root cause: an upstream Qt bug (QTBUG-147602) where Qt chokes on the ICC color profile of the animated wait cursor. The crashing line is `QApplication::setOverrideCursor(QCursor(Qt::WaitCursor))` - unchanged in KeePassXC since 2022; what changed was macOS. Fixed in Qt 6.11.2 and 6.12, so KeePassXC rebuilt the DMG with a patched Qt and shipped it as the same version number with a `-1` in the filename (KeePassXC-2.8.0-1-arm64.dmg, revision 82ab2fd), linked from the official download page. The maintainer's aside is telling: "Brew is always a problem when we fix binaries."

## Why it is interesting
- Root cause is a parable about dependency surfaces. A password manager was taken down not by its crypto, not by its storage, but by the *hourglass icon* - an ICC profile parser inside Qt, triggered by an OS update, on a code path untouched for four years. Your exposure to upstream is every line they ship, not the ones you think about.
- The failure site maximizes user panic: the unlock prompt. Users could not tell whether their vault was corrupted or the app was broken (one reporter verified with Keepassium that the database was intact - the exact right diagnostic instinct, worth teaching).
- The fix distribution is quietly unusual: same version number, new binary, `-1` suffix, hot-swapped on the download page. That gets fixes out fast but defeats version comparison ("I have 2.8.0" no longer identifies which 2.8.0), and the maintainer admits it fights package managers like Homebrew. A real tension between emergency patching and release hygiene, handled in the open.
- macOS moved under Qt, not the other way around: multiple macOS versions changed their rendering path and exposed a latent Qt bug on a stable four-year-old call. "It worked before the update" can mean the platform changed, not the app.

## Honest limits
- Root cause is the maintainer's attribution to QTBUG-147602; this finding did not independently verify the Qt bug report's contents.
- Affects the official DMG builds; Homebrew users' path to the fixed binary was unclear per the thread.
- Reporter macOS version strings ("macOS 27.2") are self-reported; the exact set of affected macOS/Qt combinations is not exhaustively mapped.
- The `-1` respin means "2.8.0" is ambiguous in any downstream report; issue state may change as the fixed build propagates.
