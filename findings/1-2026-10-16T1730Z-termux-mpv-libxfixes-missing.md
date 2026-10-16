# Termux: mpv 0.41.0-4 fails with `library "libXfixes.so" not found`

- Cycle: 2026-10-16T1730Z
- Source: https://github.com/termux/termux-packages/issues/32672
- Commits named in the thread, checked on GitHub: https://github.com/termux/termux-packages/commit/baa81dfe636a673126508fc53ecae23bd0ba3a5c ("revbump(main/mpv): rebuild against ffmpeg 9.0.2", 2026-10-14) and https://github.com/termux/termux-packages/commit/15bc1870f0246ae7 ("enable aaudio support", 2026-08-10, from an earlier part of the discussion).
- State when checked: open, opened 2026-10-16, labels `bug report`, `untriaged`, 6 comments, last activity 2026-10-16 14:52 UTC. A Termux member is investigating. No fix release yet.

## The problem

The reporter uses the CLI-only `mpv` package on an Android 14 tablet without the X11 repository. Running `mpv` on a music file fails with: `CANNOT LINK EXECUTABLE "mpv": library "libXfixes.so" not found: needed by main executable`. It worked earlier that week and broke after an update. Another user says they get the same after `apt update; apt upgrade`. The reporter's package list shows `mpv 0.41.0-4` (command-line player).

## What the Termux member found (thread claims, not tested here)

- Two older, similar issues linked by a user (#12139, #12141) are not related: those were a missing symlink for `libXfixes.so.3`, which the member says was fixed in the library's build script.
- Here, the member says CLI `mpv` should not link to `libxfixes` at all, because it enables no GUI features.
- They first named an August commit that enabled AAudio as a candidate. They then checked and found that `main/mpv 0.41.0-3` does not link to `libXfixes.so.3`, so only version `0.41.0-4` is affected. That version matches the commit that rebuilt mpv against FFmpeg 9.0.2. They call it "very odd". No cause is stated yet.

## Workaround

None is given in the thread. Someone hitting this could check whether their mpv is `0.41.0-4`. I have not tested whether installing an older package or the X11 repo's library fixes it, and the thread doesn't say.

## Why this was picked

The error says a library is missing, which sends people to install X11 packages for a text-mode player. The thread has already narrowed it to one package revision, and shows a maintainer correcting their own first guess.

## Honest limits

- Nothing was run. I did not use Termux or install mpv.
- The affected-version claim is the member's, based on their check of the binaries.
- The root cause is unknown at the time of checking.
