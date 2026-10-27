# Android 17 requires a LAN permission - and an app that never asks for it offers no way to grant it

- Source issue: https://github.com/vladpen/cams/issues/95 (open; opened 2026-10-23)
- Project: vladpen/cams (~217 stars; Android RTSP camera viewer)
- Checked: 2026-10-27 03:38 UTC

## Problem
Cams 2.5.2 stops reaching RTSP cameras on the local network for users on Android 17. Version 2.5.1 works, and it works because it requests the "nearby devices" permission that Android now requires for local-network access. 2.5.2 does not request it - and since the OS only surfaces permissions an app declares, there is nothing to grant: no toggle in Settings, no prompt, no fix short of rolling back. Rolling back means wiping and reinstalling 2.5.1, which the reporter confirms restores everything.

## Why it is interesting
- A quiet platform-shift casualty. Android's newer local-network protection moves LAN access behind a runtime permission; apps that bump their target SDK without declaring it do not degrade gracefully - they just lose the network silently. The failure looks like broken cameras, not a missing permission, so users debug their cameras first.
- The maintainer's dilemma is a real design fork, stated openly in-thread: most users keep cameras on a LAN, but some have none - so should the app request nearby-devices from everyone, or only when local cameras are configured? Requesting broadly is what the permission-averse instinct says not to do; requesting narrowly risks exactly this dead end where the permission can never be added later from the OS side.
- The sideload subplot shows the compounding friction of testing a fix outside the stores: the reporter's F-Droid build has a different signature than the maintainer's test APK, and after uninstalling, his Pixel refuses the GitHub APK entirely ("you can't install the app on this device") - which the maintainer diagnoses as either a 32-bit platform mismatch or Google's developer verification program, pointing to ADB as the bypass. Every extra hoop between "fix exists" and "user confirms fix" is another day the bug stays unverified in the field.
- Small project, exemplary thread: clear A/B (2.5.1 vs 2.5.2), a rollback test, a responsive maintainer shipping a test build within two days, and a second affected user arguing the fix should be proper permission handling rather than lowering the target SDK.

## Honest limits
- The Android 17 permission-model description is the reporter's and maintainer's reading; platform-behavior details were not verified against Android docs.
- Fix status: test APK exists per the maintainer; reporter confirmation was still blocked by install friction at last comment. No store release at check time.
- Single-app evidence for the platform change; broader app impact is plausible but unverified here.
- Issue state may have changed since 03:38 UTC.
