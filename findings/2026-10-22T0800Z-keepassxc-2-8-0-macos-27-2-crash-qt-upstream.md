# KeePassXC 2.8.0 on macOS 27.2: crash on start, a maintainer points to the same Qt bug seen in OBS

- Source issue: https://github.com/keepassxreboot/keepassxc/issues/13822 (open at check time; labels: platform: macOS, upstream, crash; opened 2026-10-22 00:02 UTC; 6 comments)
- Qt bug named by a maintainer: https://qt-project.atlassian.net/browse/QTBUG-147602 (our fetch of this page returned no content, so we could not read it)
- Related pull request mentioned by a commenter: https://github.com/keepassxreboot/keepassxc/pull/13821 (open; title "Fix macOS Qt plugin deployment")
- Same stack in another app, covered in an earlier finding: https://github.com/obsproject/obs-studio/issues/14061
- Project: https://github.com/keepassxreboot/keepassxc (29,362 stars per the API). Release 2.8.0 was published 2026-10-21 21:57 UTC (not a pre-release)
- Checked: 2026-10-22 08:40 UTC

## Problem
The reporter says that after updating to KeePassXC 2.8.0 on macOS 27.2 (build 26B118, Apple Silicon), the app crashes when they enter the password to open an existing database. The pasted crash report shows an `EXC_BREAKPOINT` on the main thread, with a stack running `QImage::toCGImage()` (in Qt 6.11.1) into `CGImageCreate` and `CGColorSpaceGetType`.

## What the maintainers said
- A member first wrote that the crash occurs in Apple code.
- Later a member wrote that it looks like an upstream Qt bug, QTBUG-147602, and that all KeePassXC does is call `QApplication::setOverrideCursor(QCursor(Qt::WaitCursor))`, a line they say has not changed since 2022. They said the issue is "fixed in Qt 6.11.2 and Qt 6.12 apparently", which is hedged in their own words, and that the only way to fix it is to build new DMGs with a patched Qt version.
- The member also said the open pull request #13821, which a commenter had linked, only concerns Qt plugins not being deployed in the DMG, so it is probably unrelated.
- The issue carries the `upstream` label. We saw no fix PR or new release at check time.

## Link to the OBS finding
The stack in this report has the same frames as the OBS Studio crash on macOS 27.2 in our earlier finding, and both list Qt 6.11.1. Two unrelated projects hitting the same stack is consistent with a shared Qt cause, but we have not confirmed that. We only checked in an earlier hour that the qtbase commit named there is contained in the `v6.11.2` tag.

## What this does not tell you
- No fixed KeePassXC build exists as far as we saw. We do not advise any workaround for opening a password database. Users with a database they need should make sure they have a backup copy and, if they can, use a version on a different machine, and check the project's issue for updates. This is general caution, not project advice.
- A separate comment about an Ubuntu 22.04 AppImage failure is a different problem, per a maintainer, and is not covered here.

## Honest limits
- We did not run KeePassXC or macOS 27.2. We did not read the Qt tracker page. The cause is the maintainers' and commenters' account.
- State may have changed since 08:40 UTC.
