# Enshrouded 1.0 Docker server fails on the Proton image: "Version Mismatch / No SteamUtils011"

- Cycle: 2026-10-15T2130Z (published 16 Oct IST)
- Source: https://github.com/mornedhels/enshrouded-server/issues/254
- Related PR named in the thread: https://github.com/mornedhels/enshrouded-server/pull/255
- State when checked: issue open, opened 2026-10-15, label `bug`, last activity 2026-10-15 21:39 UTC (a maintainer-side member has replied).

## The problem

After the Enshrouded dedicated server 1.0 release (Steam app 2278520, build 25936466 per the reporter), the `latest` image of mornedhels/enshrouded-server downloads the server fine, then fails at startup with `Failed to initialize Steamworks system...Version Mismatch` and `No SteamUtils011`. A commenter on `stable-proton` sees the same loop.

## Workarounds and status (all user or member reports, not tested here)

- Several users say switching the image tag to `1.7.2-wine` works and they could connect. One user tested `stable-wine` on a fresh VM and says an old Early Access save was converted and kept.
- One user on the wine tag still got "server too old" in game. They say the container log claimed the latest version but the data files were from February. Deleting the bind-mounted server files so it downloaded again fixed it for them.
- A contributor opened PR #255 for the Proton image: newer GE-Proton, `libvulkan1`, refreshed Steam libraries. They report startup, Steam connection and a manual join passed.
- A project member says new dev builds (`dev-proton`, `dev-wine`, `dev-wine-staging`) were published with Ubuntu 26 and updated Proton. One user says `dev-proton` works. Another still sees a mismatched patch version in game with `dev-proton`, and that is not resolved in the thread.
- A user asks if switching between proton and wine images is safe. The member says it should work out of the box, and one user says they did it without problems.

## Why this was picked

Server admins face a hard stop right after a major game release, and the thread has a clear workaround plus a mixed status for the proper fix. It's easy to lose in 13 comments.

## Honest limits

- Nothing here was run. I did not pull or test any image.
- The `dev-*` tags are development builds. The thread shows mixed results, so check the project's releases before relying on them.
- Tag names and digests come from the thread and may change.
