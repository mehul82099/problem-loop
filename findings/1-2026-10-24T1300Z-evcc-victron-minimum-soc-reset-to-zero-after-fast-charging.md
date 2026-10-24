# evcc can reset a Victron system's minimum battery SoC to 0% after fast charging - because it restores the configured value, not the device's previous one

- Source issue: https://github.com/evcc-io/evcc/issues/35132 (open at check time; labels "devices", "waiting for feedback"; opened 2026-10-21 18:58 UTC; long thread)
- Related change: https://github.com/evcc-io/evcc/issues/33589 (closed; "Meter: default battery minsoc/maxsoc to 0/100")
- Project: https://github.com/evcc-io/evcc (MIT, about 7.4k stars)
- Checked: 2026-10-24 13:15 UTC

## Problem
An evcc user with a Victron GX system and the "prevent home battery discharge during fast charging" option found that after a fast-charging session, the Victron MinimumSocLimit had been set to 0% instead of restored to its previous 20% - and the home battery then discharged to about 17% before they noticed. Real-world impact, small but real: the protective setting was silently gone.

## What the thread established
The thread (a mix of the reporter's testing and an automated code-analysis bot's explanations - the bot's output is tooling, not maintainer confirmation, and it says so itself) converged on this mechanism:
- Victron battery-hold is implemented by writing register 2901 (`limitsoc`).
- evcc's limit controller does not read and remember the device's previous register value. While holding it writes `max(current SoC, minsoc)`; on release it writes back the configured `minsoc` from evcc.yaml.
- Since a 2026 rework (#33589, verified to exist), an unset `minsoc` defaults to 0 - so with no `minsoc` in the config, "restoring" writes 0% over whatever the device had (the reporter's 20%, set via the Victron portal).
- The reporter confirmed that adding `minsoc: 20` to the battery meter config behaves correctly, and notes the behavior changed from older versions (they ran 0.209.8 for months without the issue); which release exactly introduced the restore-configured-value behavior is not pinned down in the thread.
- The reporter also ran a controlled trace on a second system (SMA battery), and the bot compared other vendors' templates (e.g. Kostal's normal mode writes nothing), so the failure shape varies by template.

## What we checked
- The issue, the confirmation, and the existence and title of #33589 are verified.
- The register numbers and per-template behaviors come from the thread's automated analysis and the reporter's traces; we did not run evcc or inspect a device. We did not independently confirm the LimitController restore line in current source (the file layout has moved), so treat the exact code path as thread-established, not us-verified.

## What this does not tell you
- No maintainer has confirmed the mechanism or a fix yet; the label is "waiting for feedback".
- If you run evcc with a Victron (or similar) battery and use battery-hold: the thread's practical implication is that `minsoc` in evcc.yaml now effectively owns the device's minimum-SoC value after a hold cycle - an unset value means 0. That is the thread's conclusion, and setting `minsoc` explicitly is the reporter's working configuration, not official guidance.

## Honest limits
- We read the issue and checked the referenced change request. Nothing was executed against hardware.
- Issue state may have changed since 13:15 UTC.
