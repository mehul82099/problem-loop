# Your PHP is patched, your analytics tool disagrees: version numbers can't see distro backports

- Source issue: https://github.com/matomo-org/matomo/issues/25572 (open; opened 2026-10-22)
- Project: matomo-org/matomo (~22k stars)
- Verified: Ubuntu security notice USN-8948-1 exists (ubuntu.com returns 200); Matomo 5.14.2 named in multiple confirmations
- Checked: 2026-10-27 02:37 UTC

## Problem
Same CVE week as last hour's finding, seen from the other side. Matomo 5.14.2 added an "Urgent PHP security update required" warning keyed on the PHP version number. But Ubuntu 24.04's `php8.3-fpm` reports 8.3.6 while Canonical's USN-8948-1 backports the fixes for CVE-2026-109618 and CVE-2026-109619 into exactly that version (`8.3.6-0ubuntu0.24.04.13`, quoted in-thread). CloudLinux does the same for alt-php85. Result: thousands of correctly patched servers now display a critical warning that cannot be dismissed - and admins field panicked questions about a fire that is already out.

## Why it is interesting
- The version string is the wrong API. Distribution security models deliberately freeze the upstream version and backport patches, so "what version are you" and "are you vulnerable" diverge on exactly the long-support distros most common in production. A warning system built on version comparison is guaranteed to false-positive on Ubuntu LTS, Debian, RHEL, and CloudLinux - not an edge case, the mainstream.
- Warning fatigue has a real cost. The whole point of the alert was to drive fast patching during an active RCE week; making it cry wolf on patched systems trains admins to find the dismiss button - which is, tellingly, the fix a Matomo contributor announced in-thread: let admins turn the warning off after confirming their vendor patch, rather than teaching the check to understand backports. A pragmatic answer, and an admission of how hard the correct one is (there is no standard "is this CVE fixed" query; a community member's side-tool literally parses package-release strings to answer it).
- Nice symmetry with the OpenLiteSpeed thread: vendors patch fast, version numbers lag reality everywhere, and the ecosystem's signals - warnings, checks, notices - all have to be reinterpreted by humans who know the distro backport convention.

## Honest limits
- The USN-8948-1-to-package-revision mapping is quoted from the issue (link verified live); we did not diff the package changelog.
- Matomo's announced fix direction (dismissible warning) is a contributor comment, not a shipped release at check time.
- Whether any version-check could reliably detect backports across distros is an open question this finding does not settle.
- Issue state may have changed since 02:37 UTC.
