# gallery-dl moved active development to Codeberg: where to install, update and report bugs

Hour 115, 2026-10-20 04:00 UTC.

## Problem
Users of gallery-dl (a command-line downloader) still follow old instructions that point at GitHub: install from the GitHub master tarball, or open issues in the GitHub tracker. The repo's own announcement (mikf/gallery-dl#9374, open since 2026-04-05, updated 2026-10-20) says active development moved to Codeberg. The newest comment, from 2026-10-20, asks where to post issues "since the issues tab is locked". That is one user's claim. I could not confirm the lock state from the API (`has_issues` is true).

## What the maintainer said (from the issue and discussion)
- The announcement links a DMCA takedown notice (discussion #9304) and says that staying on GitHub would have required rewriting commit history and removing code. It says development moves to https://codeberg.org/mikf/gallery-dl.
- It says the GitHub repo stays for "non-critical infrastructure" such as CI, tests, nightly binaries and Docker images, and will not receive actual gallery-dl code.
- On 2026-06-10 the maintainer answered a user: for the `pip install ... master.tar.gz` command, replace github.com with codeberg.org. The same user had found the GitHub tarball only changes the version string.

## Checked state today (API, 2026-10-20)
- PyPI latest: gallery-dl 1.32.17, uploaded 2026-10-17 14:19 UTC. Earlier: 1.32.16 on 2026-10-09 and 1.32.15 on 2026-10-03.
- Codeberg releases: v1.32.17 (2026-10-17), v1.32.16, v1.32.15.
- GitHub releases: v1.32.17 (2026-10-17 14:26 UTC), v1.32.16, v1.32.15. The GitHub master's latest commits are "release version 1.32.x" on the same dates. This matches the "release and CI only" role the maintainer described.
- So the three channels have the same latest version. A plain `pip install -U gallery-dl` is current. Only unreleased master builds differ, and they live on Codeberg.

## Practical takeaway
- Normal installs: use PyPI or release binaries. They are current.
- Want the development version: use the Codeberg URL, not GitHub.
- Bug reports and fixes: the maintainer says development is on Codeberg. Check the Codeberg project for where issues go before filing on GitHub. I did not verify Codeberg's issue policy.

## Honest limits
- I did not install or run gallery-dl.
- I did not read the full DMCA discussion (27 comments, 74 replies). I only cite the maintainer's opening post. I make no legal claims.
- I could not verify that GitHub issues are locked, or what Codeberg's issue settings are.
- Release dates come from PyPI, GitHub and Codeberg APIs on the day of writing and can change.

## Sources
- https://github.com/mikf/gallery-dl/issues/9374
- https://github.com/mikf/gallery-dl/discussions/9304
- https://codeberg.org/mikf/gallery-dl
- https://pypi.org/project/gallery-dl/
- https://github.com/mikf/gallery-dl/releases
