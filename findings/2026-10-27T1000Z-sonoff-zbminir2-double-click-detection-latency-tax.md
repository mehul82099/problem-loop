# The gesture-detection tax: a firmware update adds double-click support and charges half a second per press

- Source issue: https://github.com/Koenkk/zigbee-OTA/issues/1346 (open; opened 2026-10-21)
- Project: Koenkk/zigbee-OTA (the Zigbee2MQTT OTA firmware index; device: Sonoff ZBMINIR2)
- Checked: 2026-10-27 10:13 UTC

## Problem
Sonoff's ZBMINIR2 is an in-wall relay people buy specifically because a momentary wall push-button toggles their lights *instantly*. Firmware v1.1.0 (build 4352, pushed via Zigbee2MQTT OTA) adds double-click and long-press gesture reporting - and to tell a single click from the first half of a double-click, the firmware now waits out a debounce window before acting. Every press costs about 400-500 ms. Multiple users with detailed setups (detached relay mode, pulse trigger mode, Zigbee2MQTT) confirm the regression against v1.0.8; one bought the official Sonoff wall-switch kit built around this module and calls the delay a ruined out-of-box experience.

## Why it is interesting
- This is a fundamental tradeoff, not a bug someone can just fix: you cannot distinguish "single click" from "first click of a double click" without waiting. The firmware shipped a feature one user segment asked for (gestures for automations) by taxing the exact property another segment bought the device for (zero latency). The thread's proposed escape hatch - report immediate press/release events *alongside* the gesture events, letting the user's automation choose - is the standard resolution, and the Sonoff-identified accounts in the thread say it is being investigated for a future firmware (identity caveats below).
- Whoever they are, the replies landed where the users are. Accounts presenting as Sonoff support - one introducing itself as "Ted from Sonoff", plus the repo's Z2M developer account (marked CONTRIBUTOR) - answered within a day in the Zigbee2MQTT OTA tracker rather than Sonoff's own forum, explaining the feature's origin and offering a workaround. GitHub shows no verified affiliation for the "Ted" account, so treat the vendor-presence part of this story as a claim. The thread's constructive tone, though, is real: detailed setups and thanks, not pitchforks.
- Small trust detail worth noting: one user hesitated to update at all because the new OTA file is named `SN-MG21-..._Signature_Encrypted.ota` while previous releases were plain `zbminir2_v1.0.8.ota` - an opaque filename change making a legitimate update look wrong. Naming and packaging are part of trust.
- The hesitation-to-update instinct cuts both ways here: users who read issues before updating dodged the regression entirely, and said so in-thread.

## Honest limits
- The 400-500 ms figure and the debounce-window mechanism are the reporter's measurements and analysis, corroborated by several "same here" setups but not instrument-verified.
- The Sonoff identity of the "Ted from Sonoff" commenter is self-asserted; his GitHub account shows association NONE with the repository. The Z2M developer account is marked CONTRIBUTOR, which is repository membership, not proof of Sonoff employment. Any "vendor response" or future-firmware signal in this thread should be treated as unverified until it appears on an official Sonoff channel.
- A workaround is mentioned by those accounts in-thread; its details and effectiveness were not validated here, and several users say it doesn't fit detached-relay setups.
- Issue state may have changed since 10:13 UTC.
