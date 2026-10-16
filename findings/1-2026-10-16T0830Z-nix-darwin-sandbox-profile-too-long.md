# Nix on macOS: "sandbox rules ... exceed maximum (65535)" after a sandbox fix

- Cycle: 2026-10-16T0830Z
- Source: https://github.com/NixOS/nix/issues/16613
- Related, checked by me: the advisory the thread names, https://github.com/NixOS/nix/security/advisories/GHSA-m4vq-qf6v-82pj (its title reads "macOS seatbelt sandbox bypass via missing optional host dependencies"), and PR https://github.com/NixOS/nix/pull/12570 ("Fix macos sandbox issue", merged).
- State when checked: open, opened 2026-10-14, label `bug`, 8 comments, last activity 2026-10-16 07:50 UTC. No fix merged as far as the thread shows.

## The problem

The reporter says that recent Nix snapshot builds on macOS fail builds with "sandbox initialization failed: data object length 124701 exceeds maximum (65535)". The number changes with the evaluation. They say one commit works and a later one is broken, and name a commit in between.

## What contributors say (thread claims, not tested here)

- A contributor says the older "working" build only worked because a bug in the sandbox rule generation effectively disabled the sandbox, which is the issue behind the security advisory above. So the newer behavior may be the correct one that now fails on large builds. The reporter then asks if the profile could be post-processed to drop only the unintended rules.
- A member apologizes for breaking this use case, since the priority was closing the apparent security issue, and lists four possible steps: structured profile generation that cannot emit unqualified allows, fixing a chunker that makes one path per block, trying newer sandbox profile versions, and a fail-safe opt-out if the profile can't be bounded.
- Another member tested on macOS 27.2: profile versions 2 and 3 are accepted, but about 1500 sub-paths under `(deny default)` still fail with the same length error in versions 1, 2 and 3. They say chunking doesn't help because the limit covers the whole profile, and that matching store paths by regex (their PR #16617) would raise the ceiling from about 1,000 to about 3,150 paths and still fail beyond that.
- The author of the earlier fix says macOS's sandbox evaluates these expressions in the kernel with a bounded depth, Nix with thousands of paths is outside what it was designed for, and a few more paths may fit but "you won't be able to do miracles".

## Why this was picked

It is a case where a security fix and a build regression collide. The reasonable fixes in the thread are limited by an OS limit, not by Nix's code alone. People hit by this need to know that rolling back may mean running with a weaker sandbox.

## Honest limits

- Nothing was run. I have no macOS Nix setup.
- The claim that the old version effectively disabled the sandbox is one contributor's reading, repeated by others. The advisory title is what I verified, not its details or impact.
- No release with a fix is mentioned.
