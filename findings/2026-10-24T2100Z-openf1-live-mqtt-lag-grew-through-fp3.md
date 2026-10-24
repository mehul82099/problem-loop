# OpenF1's live F1 data stream fell cumulatively behind during FP3 - from ~3 minutes to ~16 minutes - then recovered for qualifying

- Source issue: https://github.com/br-g/openf1/issues/481 (open at check time; opened 2026-10-24 17:47 UTC)
- Project: https://github.com/br-g/openf1 (community F1 timing-data API; license listed as NOASSERTION, about 1.8k stars)
- Checked: 2026-10-24 21:20 UTC

## Problem
During the FP3 session on 2026-10-24 (Austin, per the thread), subscribers to OpenF1's live MQTT topics (car_data, location, intervals) saw payload timestamps lag real time by minutes - and the lag grew through the session instead of staying constant. Multiple users, including at least one paid account, confirmed; REST responses lagged similarly, so it was not an MQTT-specific consumer problem.

## The thread's measurements (user-reported, and refreshingly quantitative)
- Start of session: ~3 minutes behind.
- One user's capture at 17:56 UTC: median gap between receipt time and payload date was 601 seconds across 1,003 location records.
- Another: ~12 minutes at 18:07 UTC, REST ~16 minutes behind at 18:32 UTC.
- The reporter's summary: the session ended and the stream kept delivering buffered data for another ~20 minutes - the signature of a producer or pipeline falling behind and draining a backlog, not of dropped data.
- A second independent MQTT connection received the same old points at the same time, ruling out a single consumer's pipeline.
- Later in the day: "Qualifying seems so far, so good" - the service appears to have recovered by the next session.
- No maintainer response in the thread at check time.

## What we checked
- The issue and its measurements exist as described; the repo exists and matches its description.
- All lag numbers are user measurements; we did not subscribe to the stream.
- The session timing details (Austin, FP3 vs qualifying) come from the thread; we did not verify the race calendar.

## What this does not tell you
- No root cause or maintainer statement yet - this is a performance incident snapshot, not a diagnosis.
- Whether it recurs on Sunday's session is exactly what the thread's participants are watching.
- If you build on OpenF1's live feeds: buffered-and-late is a different failure mode than missing data - your pipeline should expect timestamps to drift by double-digit minutes on a bad day, per these reports.

## Honest limits
- We read the issue. Nothing was subscribed to or measured from here.
- Issue state may have changed since 21:20 UTC.
