# FreshRSS in Docker: users report HTTP 403 on "mark as read" after the 1.30.3 and 1.30.4 security releases

- Source issue: https://github.com/FreshRSS/FreshRSS/issues/9482 (open at check time; label: "Bug (unconfirmed)"; opened 2026-10-22 11:21 UTC; 4 comments, all from users)
- Release notes: https://github.com/FreshRSS/FreshRSS/releases/tag/1.30.3 (2026-10-21 14:30 UTC) and https://github.com/FreshRSS/FreshRSS/releases/tag/1.30.4 (2026-10-21 20:45 UTC)
- A Docker change in 1.30.4, as a pull request: https://github.com/FreshRSS/FreshRSS/pull/9476 ("Docker: disable session.upload_progress to mitigate CVE-2026-109618/9", closed)
- Project: https://github.com/FreshRSS/FreshRSS (AGPL-3.0, 16,387 stars per the API)
- Earlier findings in this repo on the PHP security release: `2026-10-21T0400Z-php-critical-security-release-2026-10-21.md`
- Checked: 2026-10-22 19:40 UTC

## Problem
The reporter says that since upgrading a self-hosted FreshRSS (standard Docker image, external MariaDB) to 1.30.4, marking one article as read shows "A request has failed" and leaves it unread. "Mark all as read" ends on FreshRSS's 403 "Forbidden" error page, and so does the installation check. Three more users say they see the same on Docker: one noticed it already on 1.30.3, one pasted a log (a POST to `c=entry&a=read` answered with a redirect to an error page with code 403), and one says most actions return 403, including logout, with mark as read being the first they noticed.

## What the releases changed (from the notes)
- 1.30.3 is described as a security release addressing "severe PHP vulnerabilities" (two CVE numbers are listed, linking to a php.net notice). It moved the default Docker image to Debian 13 with PHP 8.4.27 and Apache 2.4.69.
- 1.30.4 updated the alternative Alpine image to PHP 8.5.12 and, per the changelog and the pull request above, disabled the PHP setting `session.upload_progress.enabled` in the Docker entrypoint "for additional security". We confirmed that the pull request exists and that the commit touches `Docker/entrypoint.sh`.
- No other change in the commit range from 1.30.2 to 1.30.4 touches the request handling, from the commit titles we read. We did not read the diffs.

## What we do not know
- The cause is unknown. The issue has no maintainer reply and carries the "unconfirmed" label. The PHP package update and the session setting change are the Docker-level changes that landed together with the first reports, so they are places to look. That is our hypothesis, not something anyone in the thread said, and it is possible the cause is somewhere else, such as a reverse proxy or cookie setup specific to these users.
- We cannot tell how many installs are affected, or whether the Alpine and Debian images behave the same. One commenter says they use Podman.

## What this does not tell you
- We do not advise rolling back, re-enabling PHP options or changing the container configuration. The changes in question are security mitigations for PHP CVEs, so undoing them has its own risk. If you are affected, the safer route is to wait for the maintainers' answer in the issue.
- The 403 pages in the reports are FreshRSS's own error page. We did not see a log from the application itself.

## Honest limits
- We did not run FreshRSS or Docker. Everything about the failures is from four user comments.
- State may have changed since 19:40 UTC.
