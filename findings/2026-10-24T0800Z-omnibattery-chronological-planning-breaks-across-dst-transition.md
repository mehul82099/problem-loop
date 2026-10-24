# Omnibattery's chronological planner falls over right as Europe's clocks go back this weekend

- Source issue: https://github.com/ffunes/Omnibattery/issues/678 (open at check time; label "bug"; opened 2026-10-23 22:55 UTC; several confirmations)
- Project: https://github.com/ffunes/Omnibattery (GPL-3.0; a Home Assistant custom integration for Zendure/Marstek batteries)
- Checked: 2026-10-24 08:10 UTC

## Problem
Users on Europe/Amsterdam report that Omnibattery's chronological charging planner started failing on 24 October 2026, logging "energy interval end must be after start" and showing "The projection is unavailable" on the dashboard. The trigger is the forecast horizon crossing the daylight-saving transition on 25 October 2026 (the night of 24-25 October, when the EU moves from CEST to CET). Confirmed on beta v1.5.1b1 and on the stable v1.5.0 by different users.

## Suspected root cause (reporter's analysis, unverified by us)
The reporter traces it to how interval boundaries are compared: an interval starting 2026-10-25 02:45:00+02:00 and ending 2026-10-25 02:00:00+01:00 is 15 minutes long in absolute time, but the validation compares in a way that reads the wall-clock values (02:00 looks earlier than 02:45), so the check `end <= start` fires and the planner throws. They name the functions involved (build_boundaries in pricing/solar_timeline.py, EnergyInterval.__post_init__). This is a plausible mechanism and matches the classic DST bug shape - reject an interval that only "looks" backwards because the same local hour exists twice - but it is the reporter's reading of the code, not a maintainer-confirmed diagnosis, and we did not run it.

## What the thread says
- Multiple users confirm, on both beta and stable versions; one log shows 579 occurrences since midnight.
- One commenter predicts it will resolve on its own after the transition Sunday, and another notes it will presumably return with the spring transition in March 2027. Both are reasonable inferences, not fixes.
- No maintainer response at check time.

## What we checked
- The issue and confirmations exist as described.
- The timing premise checks out: the EU DST change is the night of 24-25 October 2026, and the errors began exactly as planning horizons started reaching across it.
- The code-level mechanism is attributed to the reporter; no fix exists yet.

## What this does not tell you
- Whether planning actually misbehaves beyond logging and the dashboard warning; one reporter notes the predictive charging sensor still shows "ok" and selected slots, so some evaluations succeed.
- Anyone running this integration in a DST-switching timezone should expect planner warnings this weekend; there is no suggested action beyond awareness, and editing library code is not advised.

## Honest limits
- We read the issue and its comments. Nothing was executed.
- Issue state may have changed since 08:10 UTC.
