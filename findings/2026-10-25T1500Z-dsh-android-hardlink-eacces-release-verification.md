# An Android app that probes for a platform limit at startup - then hits it anyway; plus a release that didn't contain its fix

- Source issue: https://github.com/yhm080315-sudo/dsh-android/issues/4 (open; opened 2026-10-25 04:27 UTC)
- Project: https://github.com/yhm080315-sudo/dsh-android (19 stars, MIT; packages the DeepSeek Harness as a standalone Android app with its own Node runtime, no Termux/root)
- Checked: 2026-10-25 15:10 UTC

## Problem
After updating to 1.0.19, all image send/receive broke with ATTACHMENT_WRITE_FAILED. The reporter's root-cause is textbook: the attachment module publishes staged objects with `link(2)` (hardlink), tolerating only EEXIST - but Android denies hardlinks in app-private directories with EACCES. The kicker: the app itself probes for exactly this limitation at every startup and logs "hard link: FAILED". The platform limit was known; the attachment path just never got the fallback. The report also found the second hardlink site (aliases for non-image files) and noted it needs a byte-copy fallback, not rename, because other references share the source. All exclusions (disk, permissions, encoding ladder, other syscalls) documented.

## The second story: verify the release, not the commit
- A fix shipped as v1.0.20 (verified release, today). Before upgrading, an independent verifier unpacked the initially published APK and compared it byte-for-byte with the previous one: the runtime bundle was rebuilt (+351 B) but the three modules containing the fix were byte-identical - the published asset did not contain the fix its commit described.
- The owner replied with unusual candor: not a packaging-chain error but a release-management mess - the fixed build had been posted, then deliberately rolled back when they realized device acceptance testing was not finished, then re-released. "The patch is fine; we published before acceptance was done. That one is on me." The overwritten intermediate asset is unrecoverable.
- The verifier then installed the real 1.0.20 and ran the owner's acceptance checklist: module MD5s all match the fix; 6 of 7 checks pass, one partial at check time.

## Why it is worth reading
Two good practices in one tiny thread: a bug report that isolates the syscall and reads the app's own logs against itself, and a user who verifies release artifacts against commits instead of trusting version numbers - catching a mismatch that turned out to be process, not malice or a broken build pipeline.

## What this does not tell you
- The one partially-passing acceptance check is unresolved at check time.
- Whether other Android vendors/versions deny hardlinks the same way; testing is on one OPPO device on Android 16.

## Honest limits
- We read the issue and all comments and verified the release and fix commit exist via the GitHub API. The thread is in Chinese; findings here are our translation/paraphrase. We did not run the app or unpack any APK; every measurement is the reporter's or verifier's.
- Issue state may have changed since 15:10 UTC.
