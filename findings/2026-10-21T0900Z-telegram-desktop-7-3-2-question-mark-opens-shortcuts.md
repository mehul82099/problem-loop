# Telegram Desktop 7.3.2: typing "?" in an empty message field opens the Shortcuts legend

- Source issue: https://github.com/telegramdesktop/tdesktop/issues/31471 (open at check time; labels: bug, waiting for answer, pending release; opened 2026-10-21 03:21 UTC)
- Release: https://github.com/telegramdesktop/tdesktop/releases/tag/v7.3.2 (published 2026-10-20 21:17 UTC per API; v7.3.1 was published 2026-10-10)
- Checked: 2026-10-21 09:25 UTC

## Problem
Telegram Desktop (GPL-3.0, 33308 stars) is Telegram's official desktop client. The reporter says that in version 7.3.2, with the message field empty and focused, typing `?` opens the "Shortcuts and gestures" legend and does not insert the character. If the field already has text, `?` types normally. They say this makes it impossible to start a message or a search query with a question mark. Keys named: Shift+7 on Russian or Ukrainian layouts, Shift+/ on US layouts. Their system: Windows 10.

## Confirmations in the thread
Within about six hours, commenters wrote that they see the same on 7.3.2: on Arch Linux under X11 and under Sway/Wayland, on Arch Linux with KDE Plasma 6 on Wayland, and on Windows 11 (one with a US layout). One commenter said several friends on 7.3.1 do not see it. We could not check that. We did not test any version.

## What the project said
A collaborator on the repo wrote at about 09:16 UTC on 2026-10-21 that further confirmations are not needed and that it will be fixed in a future release. The issue carries the label "pending release". We take that label only to show how the project tracks it, not as proof that a fix is committed. We found no release newer than 7.3.2 at check time, and we did not find a commit in the repository's recent history that mentions this shortcut (the commit list we read was not complete, so absence is not proof).

## For users
The thread suggests the problem only shows with an empty message field. A workaround people mention implicitly is typing some text first, since `?` types normally in a non-empty field. That is our reading of the report, not something the project advised. We did not test it. Whether going back to 7.3.1 helps is not established, and downgrading a chat client has its own risks, so we do not recommend it.

## Honest limits
- We did not run Telegram Desktop. All behaviour comes from the reporter and commenters.
- The cause is unknown from the thread. The project has not said which change in 7.3.2 introduced it.
- "Will be fixed in a future release" gives no version or date.
- Only the desktop client is covered. Mobile apps are not mentioned in the thread.
