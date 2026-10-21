# Slurm-Mail: upgrading the .deb removes the cron job and clears the mail spool

- Source issue: https://github.com/neilmunday/slurm-mail/issues/209 (open at check time; label: bug; opened 2026-10-20)
- Script in the repo: https://github.com/neilmunday/slurm-mail/blob/main/build-tools/debian/slurm-mail.postrm
- Checked: 2026-10-21 07:25 UTC

## Problem
Slurm-Mail (GPL-3.0, 123 stars; latest release v4.36, published 2026-10-19 per API) replaces Slurm's job e-mails with richer ones. The reporter (Ubuntu 24, Slurm 24.11.4, Slurm-Mail 4.36, upgrading from 4.23 by installing the .deb) says that after the upgrade no e-mails went out and the spool directory kept growing. They found that the package's `postrm` step deleted the cron file, and also cleared the spool directory. They posted a one-line workaround that recreates the cron file by hand. They note that this does not bring back deleted spool contents.

## What we checked
- We read `build-tools/debian/slurm-mail.postrm` on the main branch (API listing confirmed the file exists). Its whole content is one command, with no condition: `rm -rf /etc/cron.d/slurm-mail /etc/logrotate.d/slurm-mail /var/spool/slurm-mail`. So, as written, it removes those three paths whenever it runs.
- Debian packaging normally runs a package's `postrm` for several actions, not only a purge (for example during an upgrade). The script does not look at which action it was called with. This is our reading of the script and of general Debian behaviour. We did not install or upgrade the package to confirm it is the cause.

## What the thread says
- A second commenter says the logrotate file is removed too.
- Another notes an earlier similar report, issue #163, "no crontab file when installing from deb" (closed, opened 2025-04-25, verified by API). In that thread the maintainer could not reproduce on a fresh install and said they believed it only happens when installing a new version from a package file instead of upgrading through the package repository. The reporter there got the files by forcing the install, then closed it as a duplicate of an older issue (#73, also closed).
- A commenter suggests this may be an easy fix: only delete those files on purge, and that it is Debian-only. No change had been merged at check time.
- The maintainer asked how the new version was installed. The reporter answered that they installed the .deb file directly.

## What to take from this (a user-side note)
If you upgrade Slurm-Mail from a .deb on Debian or Ubuntu, check afterwards that `/etc/cron.d/slurm-mail` exists and that mail is flowing. Back up the spool directory first if queued mails matter. This is a precaution, not a tested procedure. Whether a repository upgrade behaves the same is unknown from this thread.

## Honest limits
- We did not install or upgrade any Slurm-Mail package, so the cause is our reading of the script plus the reporter's report.
- It is unknown whether all upgrade paths trigger it. The thread shows one confirmed report, plus two comments that look similar.
- Only the Debian packaging file was read. RPM and source installs were not checked, and the reporter only wondered if they are affected.
- No fix was merged and no maintainer diagnosis was in the thread at check time.
