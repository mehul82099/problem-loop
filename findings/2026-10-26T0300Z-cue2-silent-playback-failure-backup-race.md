# The cue that pretended to play: a race condition left a live performer pressing Go on silence

- Source issue: https://github.com/Tech-mop/Cue2/issues/9 (open; bug; opened 2026-10-22)
- Project: https://github.com/Tech-mop/Cue2 (tiny, 4 stars, MIT; audio playback software for live events)
- Fix: https://github.com/Tech-mop/Cue2/releases/tag/v0.2.0-rc.1 (verified prerelease, published 2026-10-26)
- Checked: 2026-10-26 03:19 UTC

## Problem
Mid-performance, a Cue2 user pressed Go and got nothing: the cue sat in the list, the orange playback indicator swept across it, the output device was selected - and no sound came out. The file had been added three hours earlier, so this was not a last-second import. The UI's only honest signal was buried: the cue never showed its duration, channels, codec or bitrate, which a contributor spotted in the screenshot as proof the file never actually loaded.

## Why it is interesting
- The diagnosed cause is a race in the media backup path (per the contributor who fixed it): while a file was still being backed up, the cue could reference the *incomplete* backup; when that reference failed, the player still showed the audio component as if everything were fine. A loading failure was rendered as successful playback - the worst possible lie for live-sound software, where silence on Go is a show-stopping event.
- The reporter's expected-behavior list doubles as a design principle: if a file cannot play, say so loudly; never show a seemingly active playback indicator for a file that did not load.
- Full-loop resolution in four days: reproduce on the maintainer's own machine, fix on main, and a release candidate (v0.2.0-rc.1) published with the fix and linked back into the thread. Small projects can move faster than big ones.
- One loose end honestly noted: early comments also raised possible OS permission errors blocking audio outputs; the race condition was the reproducible defect, but the log showed more than one anomaly.

## Honest limits
- The diagnosis and fix are the contributor's; we read the thread and verified the RC release exists, but did not build Cue2 or test the RC.
- The fix is in a prerelease; stable-release users do not have it yet.
- Whether the permission-denied errors in the user's log are a second bug or collateral of the first is unresolved in the thread.
- Issue state may have changed since 03:19 UTC.
