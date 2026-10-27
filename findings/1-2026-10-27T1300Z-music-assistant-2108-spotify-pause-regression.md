# A point release breaks Spotify mid-track, and the fix gets validated by the people who reported it

- Source issue: https://github.com/music-assistant/support/issues/6860 (open; opened 2026-10-24)
- Project: music-assistant/server (~3.2k stars; Music Assistant, the multi-source whole-home audio server)
- Checked: 2026-10-27 13:15 UTC

## Problem
Music Assistant 2.10.8 (released Oct 23) breaks Spotify playback: tracks stop mid-song - sometimes after 20 seconds, sometimes several minutes in - with the log showing a Spotify "pause" event immediately followed by the queue stopping. Tidal plays fine, so it is Spotify-specific. Rolling back to 2.10.7 restores stability; multiple users across Docker, AirPlay, ESP32 hardware players, and browser playback confirm the same failure signature, including the odd "child process pid ... exit status already read: will report return code 255" line.

## Why it is interesting
- The confirmation pattern is what good crowd triage looks like. Reporters isolate variables unprompted: one rules out his ESP32 player by reproducing in Chrome and noting Tidal is unaffected; another tests with and without his own Spotify Client ID; a third posts full diagnostics. Within two days the thread had a consistent signature across five independent setups - before any maintainer weighed in.
- Then the whole repair arc completes in public. A maintainer (who discloses his comment was drafted by Claude on his behalf - the transparent-AI norm, used properly) posts a fix build with careful test instructions that don't touch existing installs, and seven hours later one of the affected users reports back: tested with the Soloist engine, tracks no longer randomly pause. Reporter-to-tester in the same thread is the loop working as designed.
- The "pause event immediately followed by queue stop" sequence is a suggestive fingerprint: something in 2.10.8's Spotify provider turns the stream's natural end-of-track (or a spurious pause) into a full queue teardown. Nobody in-thread has posted the code-level cause, so treat that as symptom analysis, not root cause.
- Minor human detail: the original reporter didn't save full logs before restoring his backup, and said so - honest evidence-keeping beats confident guessing.

## Honest limits
- The fix is a maintainer-offered test build with one confirming user test at check time; not verified merged or released (latest stable remained 2.10.8-era when checked).
- Code-level root cause is not established in-thread; the pause-to-queue-stop mechanism above is inference from logs.
- Tidal-unaffected and rollback-works claims are user reports, consistent across several setups.
- Issue state may have changed since 13:15 UTC.
