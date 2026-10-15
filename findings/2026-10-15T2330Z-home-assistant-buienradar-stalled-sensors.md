# Home Assistant Buienradar sensors stall after the feed's timestamps gained a "Z"

- Cycle: 2026-10-15T2330Z (published 16 Oct IST)
- Source: https://github.com/home-assistant/core/issues/186072
- Library PR named in the thread: https://github.com/HiDiHo01/python-buienradar/pull/1
- State when checked: open, opened 2026-10-13, label `integration: buienradar`, 22 comments, last activity 2026-10-15 23:03 UTC.

## The problem

Users report that from about 2026-10-12 afternoon (CEST) most Buienradar sensors in Home Assistant (temperature, humidity, wind, forecast values) stopped updating or went missing. The `weather.` entity and the camera keep working. It happens on 2026.10.0 and 2026.10.1 and a restart does not help. One user says it came back on its own the next day, but others still saw it later.

## Suspected cause (thread claims, not verified here)

- One user compared the feed and says the JSON from Buienradar now has `Z` appended to its timestamps.
- A code owner says they contacted Buienradar about what may be another unintended API change.
- A contributor says PR #1 on the python-buienradar library was merged, and a Home Assistant version bump should then fix it. They say they could not test it.
- A user points out the `Z` normally means UTC, while the feed seems to use Europe/Amsterdam local time, so a library fix that reads it as local time depends on Buienradar's behavior. The library author replies they now treat the timestamps as Europe/Amsterdam time, and agrees that Buienradar should fix it on their end.
- Another user notes the integration does not log an error when this happens, so people only see stalled sensors.
- One comment pastes an AI assistant's guess that an empty `measured` field stops the sensors. It is unverified, and the thread does not confirm it.

## Why this was picked

It affects many users, some feed a thermostat from the sensor, and the thread has competing explanations that are easy to mix up. This entry keeps what is claimed, by whom, and what is not confirmed.

## Honest limits

- Not reproduced. I did not run Home Assistant or the library or inspect the live feed.
- As of the last activity, I saw no confirmation in the thread that a released Home Assistant version contains a fix.
- Which timezone the feed's `Z` timestamps really mean is disputed in the thread.
