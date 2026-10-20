# PowerShell 7.6.6: startup crash from the update notification on some UI languages (PowerShell/PowerShell#28131)

- Source issue: https://github.com/PowerShell/PowerShell/issues/28131 "PowerShell can crash on startup when displaying the update notification under zh-Hans due to negative PadRight width". Opened 2026-09-30, open, label "Needs-Triage", 22 reactions on the post, last updated 2026-10-20. A second open issue on the same crash: https://github.com/PowerShell/PowerShell/issues/28235 (opened 2026-10-20, I read only its title).
- Releases, from the GitHub API on 2026-10-20: v7.6.7 published 2026-10-13, v7.6.6 on 2026-09-08, v7.7.0-preview.5 on 2026-09-23.
- Source code at the v7.6.7 tag, read via the GitHub API: https://github.com/PowerShell/PowerShell/blob/v7.6.7/src/Microsoft.PowerShell.ConsoleHost/host/msh/UpdatesNotification.cs
- Docs, read 2026-10-20: https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_update_notifications

## What people report
Starting on 2026-10-20 (local morning in Asia), many users of PowerShell 7.6.6 with a Chinese, Japanese or Korean UI language report that `pwsh` dies at startup right after the banner with: `Process terminated. totalWidth ('-17') must be a non-negative value`. The stack trace in the reports points to `UpdatesNotification.ShowUpdateNotification` and `String.PadRight`. Reported numbers differ by language (-17, -10, -11, -23). At least seven separate comments show it, from Windows Terminal on Windows 11.

## Why it appears to start now
- The docs say PowerShell shows the update notification only when the newer release is more than 7 days old. The code at v7.6.7 has `NotificationDelayDays = 7`. 7.6.7 came out on 2026-10-13, so the notice first became eligible on 2026-10-20 at 00:00 UTC. A commenter who says he measured this ties the burst of reports to that time (08:00 in China).
- The code pads the second and third lines of the notice using the length of the first line, on the assumption that the first line is the longest. The v7.6.7 source still has both `PadRight` lines with no check for a negative width, as far as I read it (lines 134 and 136 of that file). In several translated messages the first line is shorter, so the width goes negative and `PadRight` throws. The original reporter showed the zh-Hans arithmetic: 37 minus 57 plus 3 is -17.
- A commenter (not a project member as far as the GitHub label shows) says translated message files first shipped in the 7.6 line with 7.6.6, so earlier 7.6 versions used the English text and never hit it. He says he ran the 7.6.6 translated templates through the same calculation and 9 of 13 languages go negative (cs, de, fr, it, ja, ko, ru, zh-Hans, zh-Hant). I did not verify his count.

## Workaround reports and what I could check
- Two commenters report that setting the environment variable `POWERSHELL_UPDATECHECK` to `Off` lets PowerShell start. The docs I read confirm that `Off` turns off the update notification feature. I did not test that it avoids this crash.
- One commenter wrote that updating to 7.6.7 "seems be ok". That is not explained, and the 7.6.7 source still has the same lines, so I would not rely on it. A likely reason is that 7.6.7 has no newer release to announce, so no notice is built, but that is my guess, not something the thread states.
- I did not find a fix pull request or a maintainer reply in the comments I read. A contributor offered to work on it on 2026-10-14.

## What can be said
- This is a live problem as of 2026-10-20, caused by a notification-formatting bug. It can stop the shell from starting for users of some UI languages, not an attack and not a problem with scripts.
- Setting an environment variable is a change to your machine's setup. Check the Microsoft doc above before using it, and treat the commenters' reports as unconfirmed.

## Honest limits
- I did not run PowerShell and did not reproduce the crash.
- I read the issue text, the reports and the two long diagnostic comments, plus the v7.6.7 source lines around the padding code.
- The language count and the explanation of why 7.6.6 differs come from commenters.
