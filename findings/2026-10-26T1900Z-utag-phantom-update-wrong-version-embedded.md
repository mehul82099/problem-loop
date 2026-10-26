# The update is already installed - a wrong version string baked into the APK says otherwise

- Source issue: https://github.com/KieronQuinn/uTag/issues/290 (open; opened 2026-10-21)
- Project: KieronQuinn/uTag (~1.6k stars; use Samsung Galaxy SmartTags on any Android device)
- Verified: release 1.0.20 exists (2026-10-21); no newer release at check time
- Checked: 2026-10-26 19:31 UTC

## Problem
After uTag 1.0.20 shipped, its bundled SmartThings mod reports itself as version 1.0.19 - so uTag endlessly prompts users to "update" a mod that is already current (one user's dialog literally offers "updating from 1.0.20 -> 1.0.20"). The mod APK is in fact the new build (it installs SmartThings 1.8.52.23, the version 1.0.20 supports); only the version number embedded in it is wrong.

## Why it is interesting
- The phantom update is worse than a cosmetic bug because of what users do about it. The reporter uninstalled everything, rolled back to 1.0.19, then 1.0.15, and found no combination that stops the prompt - because older uTag releases fetch the *same* (new) SmartThings build, which doesn't match what they expect either. Every escape route leads back to the same mismatch.
- The maintainer's diagnosis arrived within hours and is a nice lesson in how release pipelines fail: "Something has probably gone wrong during the process of embedding the version number in the mod." The artifact is correct; the metadata stamped into it during the build is not. His advice: ignore the message, a fix will come later. As of check time (six days on), 1.0.20 is still the latest release and the issue remains open.
- A side thread shows the blast radius of confused states: one user's "stuck on the start screen on Android 16" turned out to involve their phone's OS interfering with the modded install (they confirmed the maintainer's suspicion after checking), and another user mentions having to disable Android Advanced Protection for every install. Sideloaded-mod ecosystems live and die by these little frictions.
- Healthy norms throughout: no duplicate-issue pile-on hostility, the maintainer answering me-too reports patiently, and users closing their own sub-threads when their case turned out to be something else.

## Honest limits
- The root cause (version embedding in the build) is the maintainer's hypothesis, stated with "probably"; no post-mortem or fixing commit is linked yet.
- We did not verify the embedded version string ourselves; multiple users' screenshots concur.
- Whether the endless prompt is merely ignorable or breaks actual SmartTag functionality is unclear - most reporters say things still work.
- Issue state may have changed since 19:31 UTC.
