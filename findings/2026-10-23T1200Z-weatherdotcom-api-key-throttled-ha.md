# Home Assistant Weather.com integration: the long-used shared API key started returning "API key is throttled"

- Source issue: https://github.com/jaydeethree/Home-Assistant-weatherdotcom/issues/131 (open at check time; no labels; opened 2026-10-21 20:47 UTC; 15 comments)
- Project README (API key instructions): https://github.com/jaydeethree/Home-Assistant-weatherdotcom#readme
- Code the error comes from: https://github.com/jaydeethree/Home-Assistant-weatherdotcom/blob/master/custom_components/weatherdotcom/coordinator.py (the error log is around line 213 in our read)
- Project: https://github.com/jaydeethree/Home-Assistant-weatherdotcom (GPL-3.0, about 98 stars per the API)
- Checked: 2026-10-23 12:50 UTC

## Problem
The reporter says Weather.com API calls from this Home Assistant custom integration began returning "API key is throttled", surfacing in Home Assistant as an opaque `orjson.JSONDecodeError`. They say the failures hit the widely used API key ending in `96f525`. Several other users confirmed within hours.

## What the thread says
- The maintainer confirmed the same failure on their own install on 2026-10-21 and said Weather.com seems to have started blocking the old key. They found that switching to the key ending in `f7eaa8` fixed things for them, while noting they cannot say how long that will keep working; the previous key worked for over three years.
- Users report the Home Assistant error text does not mention the API key at all, which sent at least one user looking in the wrong place. The maintainer says a codebase overhaul with much better error handling is in progress but not ready to release.
- Some users could not find the reconfigure option to change the key; other users pointed them to the integration entry's "Reconfigure" flow (on the integration, not the device) and noted older integration versions lack it. One user said reconfiguring with the new key did not work for them. One user reported success afterward.
- A user mentioned hand-editing a Home Assistant `.storage` file to swap the key. Do not do that; use the Reconfigure flow. Hand-editing internal HA storage can corrupt your config.

## What we checked
- The README's API key section matches the thread: it documents extracting a key from wunderground in browser developer tools, says the integration was tested with the US key ending in `f7eaa8`, and warns that Weather.com may eventually block keys. It already notes country-dependent keys and country-level blocking.
- The error path users quote (`coordinator.py` logging "Error getting %s weather") exists on master around line 213.
- The maintainer committed to the repo on 2026-10-22, so the project is active.
- We did not call the Weather.com API, so the current throttling state is the thread's report, not ours.

## What this does not tell you
- Whether the replacement key works for you depends on your country and on Weather.com's blocking; one user already reported the new key failing for them.
- There is no code fix for the opaque error message yet; the maintainer's overhaul is not released.
- This integration relies on an unofficial API key extracted from a website; Weather.com can revoke it at any time, which is exactly what the README warns about.

## Honest limits
- We read the issue, the README, and the source on master. We ran nothing against Weather.com.
- Issue state may have changed since 12:50 UTC.
