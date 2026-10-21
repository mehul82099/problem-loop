# PHP announces a critical security release for 2026-10-21 14:00 UTC: what is confirmed and what is not

- Official notice: https://www.php.net/archive/2026.php (item dated 20 Oct 2026, "Upcoming Critical PHP Security Release")
- Threads where downstream projects react: https://github.com/php/frankenphp/issues/2732, https://github.com/FreshRSS/FreshRSS/issues/9475, https://github.com/litespeedtech/openlitespeed/issues/532 (all open at check time)
- Checked: 2026-10-21 04:20 UTC. The release had not happened yet at that time. Anything published after that is not covered here.

## What PHP itself says (read directly)
The PHP security team gave advance notice of a security release scheduled for Wednesday, 21 October 2026 at 14:00 UTC. It addresses two critical vulnerabilities, both rated CVSS v4.0 9.2. All PHP users are urged to prepare to upgrade as soon as it is out. PHP reserves the right to release earlier if details become public or exploitation is seen. Full details, affected versions and fixed versions are to be published with the release. That is all the notice states. It does not name the CVEs, the component, or the affected versions.

## What third parties say (not confirmed by PHP at check time)
- The two CVE numbers used in the threads are CVE-2026-109618 and CVE-2026-109619. The PHP notice does not list them, so the link between those IDs and the announced release comes from the issue authors and other pages.
- CERT-EU advisory 2026-018 (published 2026-10-20, page read): it summarizes the PHP announcement, says the flaws could lead to remote code execution "according to other leaks", says no technical details were public, and advises organisations to prepare for immediate patching.
- A FreshRSS issue reporter says both are pre-auth remote code execution flaws affecting PHP 5 onwards. We did not find that in the PHP notice or the CERT-EU text we read, so treat it as the reporter's claim.
- GMO Flatt Security published a preliminary analysis (a blog post in Japanese; we read the parts that matter, and a commenter on an OpenLiteSpeed issue summarized it in English). It calls the pair "php2shell", says that if its own research matches the announced flaws, the memory corruption involves PHP's Session Upload Progress feature in `ext/session`, which is on by default, and suggests setting `session.upload_progress.enabled = 0` as a mitigation before patches exist. The authors say they cannot be sure it helps and that it is not a substitute for patching.

## What projects are doing
- FreshRSS (#9475, open): the reporter says the official Docker images are built on Debian and Alpine PHP packages and stay vulnerable until rebuilt after those distributions ship fixes, and says they took their public instance offline. A project member replied with the same upload-progress setting as a possible stopgap, and welcomed a pull request to set it in the image if no update lands in time.
- FrankenPHP (#2732, open): a user asks if the scheduled Docker image build will run after the release. Others ask for clarity. One commenter says they added the upload-progress setting to their Dockerfile. Another added a web server rule that rejects multipart form requests, calling it better than nothing. We saw no evidence either helps, and no maintainer reply at check time. The FrankenPHP repo is MIT, 11406 stars.
- OpenLiteSpeed (#532, open): asks for update guidance for LSAPI/lsphp users. It says explicitly that the request does not claim OpenLiteSpeed itself is vulnerable.

## What this does not tell you
- Which PHP versions are affected, which fixed versions to install, and what exactly the bugs are. PHP said those come with the release.
- Whether the upload-progress setting or blocking multipart requests blocks anything. No one has shown that. Blocking multipart requests will also break file uploads in your own apps.
- It is not a patch guide. When the release is out, use PHP's own announcement and your distribution or image vendor's updates.

## Honest limits
- We did not test any setting, run any PHP, or look at exploit code, and we did not look for any.
- The CVE IDs and the Session Upload Progress link rest on third-party sources. We did not find a statement from PHP confirming either.
- The time of the release is in PHP's notice. It may come earlier, as the notice says.
- Status of Docker image rebuilds is unknown. We did not check any registry.
