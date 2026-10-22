# firebase-tools 15.34.1: npm release exists but the standalone binaries do not, so the curl installer saves an error page

- Source issue: https://github.com/firebase/firebase-tools/issues/11329 (open at check time; labels: type: bug, firepit, reproducible; opened 2026-10-22 01:36 UTC; 4 comments)
- Earlier similar report (closed): https://github.com/firebase/firebase-tools/issues/10787 (about 15.23.0, July 2026)
- Project: https://github.com/firebase/firebase-tools (MIT, 4,477 stars per the API)
- Checked: 2026-10-22 10:40 UTC

## Problem
The reporter says the one-line standalone installer (the one served from firebase.tools) fails on macOS right now. Their account of why:
1. The installer reads the latest version from npm, which is 15.34.1 (published 2026-10-21 22:18 UTC).
2. It then downloads a binary from a GitHub release named for that version, but no such release exists. The latest GitHub release is 15.34.0.
3. The download gets a 9-byte "Not Found" body, and the script saves it as the binary and tries to run it, giving `Not: command not found`. The reporter says the script does not fail on HTTP errors.

## What we checked ourselves
- The npm registry says `latest` for `firebase-tools` is 15.34.1, published 2026-10-21T22:18:15Z.
- The GitHub API returns 404 for a release tagged `v15.34.1`. The git tag `v15.34.1` itself exists (the ref lookup returned 200). The newest releases listed are 15.34.0 (2026-10-15), 15.33.0 and 15.32.1, each with 4 assets.
- So the report matches what we see: a tag and an npm publish without a matching release with binaries. We did not run the installer and did not download any binary.
- Issue #10787 exists, is closed, and is about 15.23.0 failing to install.

## What the thread says
- A commenter says the same thing happened at 15.23.0 and asks whether the release process needs fixing.
- A person labeled as a contributor wrote that the team hit an issue in the release pipeline, that earlier approaches to prevent it "may have missed some scenarios", and that they would ping the engineering team to get the latest release fixed. That is the only project response. No fix or new release was visible at check time.
- The reporter says that the "latest GitHub release" path of the same download service (which serves 15.34.0) works. A commenter suggests editing the install command with `sed`. We do not repeat that here and have not tested either.

## What this does not tell you
- This is about the standalone installer and binaries. The npm package `firebase-tools@15.34.1` is published, and the issue does not say it is broken.
- It does not say how many people are affected or for how long.
- Piping a downloaded script into a shell runs whatever the server returns. We do not advise running or modifying such commands. If you need the CLI now, use whatever install route you already trust and pin a version you have verified, such as a release listed on the project's releases page.

## Honest limits
- We did not run the installer or any install command, and did not test the workaround.
- The pipeline cause is a project contributor's brief statement, not a published post-mortem.
- State may have changed since 10:40 UTC.
