# GitHub CLI Linux packages: signing key rotation, and how the announcement thread filled with noise (cli/cli#13118)

- Source: https://github.com/cli/cli/issues/13118 "Upcoming PGP signing key rotation for GitHub CLI Linux packages [September 2026]". Opened 2026-04-08 by a cli member (babakks), still open, 53 comments, 36 reactions on the post.
- Cross-check: https://github.com/cli/cli/blob/trunk/docs/install_linux.md (read 2026-10-18).
- Earlier incident referenced in the issue: https://github.com/cli/cli/issues/9569 (the 2024 key expiry).

## What the announcement says (from the issue body, written by the project)
- Only Linux users who install `gh` from the project's APT or RPM repositories are affected. Windows, macOS, Homebrew, GitHub Releases and source builds are not.
- The old signing key expired on 2026-09-05. A new key was created, and a keyring file containing both keys was published on 2026-04-08.
- Fingerprints given: old `2C6106201985B60E6C7AC87323F3D4EA75716059`, new `7F38BBB59D064DBCB3D84D725612B36462313325`.
- After the expiry, installs and updates that rely only on the old key start failing with errors such as EXPKEYSIG or "NO_PUBKEY 5612B36462313325" (APT), or signature verification failures (DNF, zypper, yum). The body lists the messages and per-distribution steps.
- The new key has no fixed expiry date. A maintainer explains on 2026-09-05 that this is intentional to avoid breakage, and that it is not a promise it will never be rotated.

## What I verified
- The two fingerprints in the issue body match the ones listed at the top of the project's `docs/install_linux.md` in the repository on 2026-10-18. This is a check that the issue and the docs agree. It does not independently prove the keys themselves.
- The latest `gh` release is v2.102.0 (releases API).
- Docs tell users how to verify keys before installing, by comparing listed fingerprints with those at the top of the document.

## Discussion that is worth knowing
- 2026-09-05: users asked why no detached signature by the old key vouches for the new key. A maintainer replied that this is not a common requirement for key rotations and pointed to comparing fingerprints against the docs.
- 2026-09-08 and 2026-09-12: a user reported a DNF failure on an older Fedora with a global `repo_gpgcheck=1`. The maintainer first said the project's recommended `.repo` file disables metadata signature checking, then corrected himself: it does not, it leaves the decision to the user's DNF config. He reproduced a failure on Fedora 32 with DNF4 and not with DNF5 on Fedora 43, and said the repository metadata had been signed with the old key before it expired. His comment says it would be resolved with a later release; I did not read the rest of that comment or verify it was.

## The thread itself
- A large share of the comments after September are not about the key. Many are copies of the whole announcement, bare links to the issue, single emoji or words, or unrelated text. A rough pattern match on the comments flagged 16 of 53, and 46 comments are from accounts with no association with the repo. That is a count of my own heuristic and not a moderation record.
- Practical point: for a security announcement that people copy, the place to get fingerprints is the project's own docs and release assets, not a copy in a comment.

## Honest limits
- I did not install anything, run any of the commands, or check the actual keyring files and their checksums.
- I do not advise any particular key-handling command. Follow the project's current docs for your distribution, and compare fingerprints yourself.
- I cannot tell whether every report in the thread was resolved by the steps in the issue.
