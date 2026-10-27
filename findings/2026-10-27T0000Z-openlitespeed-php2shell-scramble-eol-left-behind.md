# A critical PHP RCE ships, and the patch gap lands on the people running yesterday's stack

- Source issue: https://github.com/litespeedtech/openlitespeed/issues/532 (open; opened 2026-10-21)
- Verified: php-src advisory GHSA-w8hw-w9fx-j79w ("RCE via OOM corruption", Critical, published 2026-10-21; patched in PHP 8.2.35 / 8.3.36 / 8.4.27 / 8.5.12); php.net security archive reachable
- Project: litespeedtech/openlitespeed (~1.5k stars)
- Checked: 2026-10-27 00:36 UTC

## Problem
PHP's Oct 21 security release fixed critical RCE vulnerabilities (CVSS 9.2 per the issue), and every PHP deployment model is in scope - FPM, mod_php, php-cgi, FrankenPHP, and LiteSpeed's LSAPI. The thread is what a coordinated-release day looks like from the downstream end: OpenLiteSpeed users find a pinned security issue, ask when packages will land, get "once the upstream is ready" from the forum and "being built for every PHP 7.4+, amd64 and arm64, pushed as they finish tests" from Slack, then watch RPMs and Docker images appear over the following hours. For supported distros, the story ends well within about a day.

## Why it is interesting
- The tail is where it gets uncomfortable. Users on end-of-life distros (the thread's example: Ubuntu Focal with PHP 8.3) see Jammy-and-later packages appear while nothing comes for them. Focal left standard support in 2025 - but shared hosting moves slowly, and LiteSpeed/OLS is disproportionately deployed exactly there.
- Into that gap steps a stranger with a binary. A commenter published an "open-source extension" that mirrors the official fix on unpatched PHP 5.4-8.5, with prebuilt x86_64/arm64 .so files to load into existing lsphp. Maybe it is exactly what it says. But this is the canonical supply-chain shape of CVE week: high urgency, an underserved population, and an unvetted party offering a drop-in compiled patch. This finding names the pattern as a risk; it does not vet or endorse that extension, and nobody should load prebuilt security patches from a forum comment without independent review.
- The response-watching behavior is a nice field guide: the community tracked the rollout not via any status page but by refreshing the RPM directory listings and the Docker Hub tags page and reporting sightings. When official comms are thin, package mirrors become the status page.
- Bonus thread item: a same-day Brotli RCE also got patched, noted almost in passing - CVE days cluster.

## Honest limits
- CVE specifics and the "unauthenticated exploit demonstrated" claim are quoted from the issue's summary of PHP's announcement; the verified advisory (GHSA-w8hw-w9fx-j79w) confirms one Critical RCE class and the patched version lines.
- Forum/Slack statements are quoted second-hand from issue comments, not from the sources directly.
- Package availability claims (RPMs, Docker tags, which distros got builds) are user sightings as of Oct 21-22; current state was not re-inventoried.
- The third-party patch extension is unvetted - treat as untrusted until reviewed. Issue state may have changed since 00:36 UTC.
