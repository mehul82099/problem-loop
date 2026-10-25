# VaultExplorer's auto-lock waited for file sync but killed your recording - three releases later, video on a locked screen still loses

- Source issue: https://github.com/R0b0To/VaultExplorer/issues/169 (open; label bug; opened 2026-10-21 04:18 UTC)
- Project: https://github.com/R0b0To/VaultExplorer (~228 stars, GPL-3.0; Flutter app for VeraCrypt/BitLocker/LUKS/gocryptfs and other encrypted containers)
- Checked: 2026-10-25 11:10 UTC

## Problem
The app's configurable auto-close (lock the encrypted container after N minutes of inactivity) correctly waits for an in-progress file sync - but treated an active audio recording as "inactivity" and locked the container mid-recording. A consistency bug: two long-running user activities, only one protected. Reported against 1.35.0 with clean repro steps.

## The fix loop, in public (all attributed)
- Owner R0b0To shipped a fix (autolock skips locking when a recording is active), and users re-tested across three rapid releases - v1.37.0, v1.37.1, v1.37.2 all on 2026-10-24 (verified), with testers reporting "still broken" twice with exact repro before v1.37.2 landed it.
- Current state per tester docfastweb on 1.37.2: voice recording is fixed - the container stays unlocked and recording continues even when the device is locked. Video recording survives the 2-minute timer only while the screen stays on; lock the screen and the recording stops silently.
- The owner's latest question is the right diagnostic: "After you lock the screen, do you see a notification that says 'recording video'?" - answer: no. That points at a missing foreground-service notification, which is how Android lets a recording survive screen lock. Not confirmed or fixed yet.
- Bonus discovery along the way: the same tester found media playback in the built-in editor also doesn't hold the lock open - same consistency gap, different activity.

## What this does not tell you
- Whether the video-on-locked-screen path will get the foreground-service treatment; discussion is live.
- The owner never explained what 1.37.0/1.37.1 missed; the changelogs would say, and we did not diff them.

## Honest limits
- We read the issue and all nine comments and verified the releases via the GitHub API. We did not install or run the app; every behavior claim is the reporter's or tester's.
- Issue state may have changed since 11:10 UTC.
