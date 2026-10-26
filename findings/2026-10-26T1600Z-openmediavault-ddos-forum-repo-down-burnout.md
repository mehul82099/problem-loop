# DDoSed and tired: OpenMediaVault's forum and package repo are down, redirected to GitHub, and its founder is out of patience

- Source issue: https://github.com/openmediavault/openmediavault/issues/2301 (open; opened 2026-10-26 by the project's founder)
- Project: openmediavault/openmediavault (~7k stars; open-source NAS operating system)
- Checked: 2026-10-26 16:29 UTC

## Problem
OpenMediaVault's forum and package repository are down again after weeks of recurring DDoS attacks. The founder (votdev) opened the issue himself: the official sites now redirect to GitHub - which is "taking the brunt" of the attack - and the forum had to be taken down in part over a php2shell vulnerability he cannot migrate away from because of bandwidth limits with his current host. His summary of where this leaves a spare-time maintainer: "Unfortunately, it's not fun anymore."

## What we verified directly
- forum.openmediavault.org currently 302-redirects straight to this GitHub issue (checked 16:29 UTC).
- packages.openmediavault.org redirects to a new .io mirror domain - package installs may route around the outage, but the official .org infrastructure is not serving.

## Why it is interesting
- A single volunteer-run site is load-bearing infrastructure for an OS installed on thousands of home servers: the package repository *is* the update channel. DDoS on a distro's repo is not vandalism of a website; it is interference with security updates.
- The compounding factors are painfully ordinary: an old forum with a known exploit (php2shell per the thread, confirmed as a takedown reason by a contributor), a hosting plan too small to migrate away from it, attacks that predate the forum problem, and one maintainer absorbing all of it in his spare time "for many years."
- The community response is the counterweight: multiple offers of concrete help (including hosting/security outreach to the project's sec contact), and a strategic debate already running about depending on Cloudflare versus European hosting sovereignty for a European project.
- The burnout sentence matters. Infrastructure stories like this usually end not with a fix but with a maintainer stepping back; the thread knows it and is saying so.

## Honest limits
- Attack details (volume, vector, duration) are as stated by the maintainer; there is no independent measurement here. php2shell involvement is confirmed by a project contributor but without technical detail.
- Whether the .io mirror fully serves all package channels is unverified.
- This finding offers no infrastructure advice; the thread's debates are reported, not endorsed.
- Issue state may have changed since 16:29 UTC.
