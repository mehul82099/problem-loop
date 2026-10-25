# Meshtastic on nRF54L15 deadlocks saving its node database - and the watchdog is configured to sleep through it

- Source issue: https://github.com/meshtastic/firmware/issues/12228 (open; labels bug, first-contribution, triage; opened 2026-10-24 12:19 UTC)
- Project: https://github.com/meshtastic/firmware (~5k-star LoRa mesh firmware, GPL-3.0)
- Checked: 2026-10-25 08:10 UTC

## Problem
On the nRF54L15 (Arduino core), a LittleFS write of `/prefs/nodes.proto` can freeze the node indefinitely: BLE drops, no LoRa packets are processed, and the device never recovers on its own. Pressing the user button unsticks it - and the very same write then completes - until it freezes again 5-15 minutes later. First-time contributor sussydevil filed it with RTT logs, GDB output, and a full mechanism analysis.

## The mechanism is three design choices colliding (reporter's analysis)
1. The CPU waits for the SoftDevice flash-completion event in `sd_app_evt_wait()` (WFI sleep) - but that event's SWI does not wake the CPU.
2. `checkSDEvents()`, which would drain the event queue and clear the write flag, is only called from the main loop - which is asleep.
3. The watchdog is configured with `behaviour = 0` in `nrf52Setup()`, which pauses it while the CPU sleeps - so the 90-second watchdog never fires either.
The button press works because its GPIOTE interrupt wakes the CPU, letting `checkSDEvents()` run. Any one of the three being different and the bug could not happen.

## Thread state
- Reproduced by the reporter on a second board (Seeed XIAO nRF54L15).
- Contributor markbirss reports a related-but-different symptom on other DIY nRF54L15 boards (runs ~1 hour, then resets) and is collecting a GDB backtrace - possibly the same root, possibly not.
- Reporter's latest observation: the freeze correlates with on-air inactivity - no events means nothing wakes the CPU, matching the mechanism.
- No maintainer root-cause confirmation or fix at check time; it sits in triage.

## What this does not tell you
- Whether this affects only DIY/custom nRF54L15 builds or shipping devices; all reports so far are DIY boards.
- The reporter's mechanism analysis is thorough but unconfirmed by maintainers; we did not audit the firmware source.
- Which of the three choices should change (wake source, event draining, watchdog behaviour) is an open design question - each has power or safety tradeoffs, and the finding does not recommend one.

## Honest limits
- We read the issue and all five comments via the GitHub API. We did not build, flash, or run any firmware.
- Firmware 2.8.2 and board specifics are the reporter's environment.
- Issue state may have changed since 08:10 UTC.
