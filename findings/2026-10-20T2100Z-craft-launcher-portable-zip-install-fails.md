# Craft Launcher: portable ZIP installs fail with "does not contain the expected executable at its root"

- Source issue: https://github.com/storytold/craft-launcher/issues/574 (open at check time; label: priority: medium; opened 2026-10-18)
- Releases (API): v0.6.0 published 2026-10-20 15:56 UTC, v0.5.1 published 2026-10-18 04:01 UTC
- Checked: 2026-10-20 21:10 UTC

## Problem
The reporter chose the "portable" install type in the Craft Launcher (Windows) with a custom folder. The launcher downloads the ZIP, then fails with: "The portable ZIP does not contain the expected executable at its root". The reporter says the ZIP holds a folder, and the files are inside that folder, so the launcher may not find the .exe at the ZIP root.

## What commenters report
- One commenter (launcher v0.5.1, Windows x64) says two apps (PhotoCraft 0.10.0, FilmCraft 0.9.0) both fail, on a mapped network drive and on a local NTFS folder, with identical log lines. They say the official portable archive they inspected has the executable inside an extra top-level folder. They tried a repackaged ZIP, but the launcher replaced their edited cached archive with the original, so that idea is untested.
- Other commenters say it happens for every app they tried, and one needs portable installs because they lack admin rights on their machine.
- A contributor on 2026-10-20 copied details from a possibly duplicate report (#646: Windows 10 Pro 22H2, launcher 0.5.1 MSI, every install or update fails about a second after download). #646 also asks for a per-user MSI option to avoid the admin prompt. We only saw the contributor's summary here.
- One commenter says that after updating the launcher to 0.6.0 on 2026-10-20 the problem still showed. Another says the maintainers do not treat it as high priority and guesses it will be fixed in the next version. That is a commenter's opinion, not a maintainer statement. Their estimate of how many users are affected has no source and we did not check it.

## Cross-references verified by API
- #646 (possible duplicate): closed, opened 2026-10-19.
- #598: closed, opened 2026-10-18, title "Portable instalation error".
- #423: open, about portable ZIP delta reuse when entry names embed the version.
- #343: open, feature request to choose where portable apps install.
- #316: closed, feature request to install portable versions under the launcher.
- The bot comment on #574 lists #423, #343 and #316 as "possibly related". Whether they share a cause is not established.

## Honest limits
- We did not run the launcher or inspect any app ZIP. The "extra folder" cause is the reporters' guess. No maintainer comment on #574 explains the cause.
- v0.6.0 is reported by one commenter as still failing. We did not test it, and we did not read the release notes.
- #646 is closed, but we did not find out why, so we cannot say if it was fixed or marked as a duplicate.
- The issue has the label "priority: medium" and was open at check time. No fix is claimed.
- Repo facts at check time: Apache-2.0 license, 3640 stars.
