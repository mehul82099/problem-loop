# Ariston Home Assistant integration: one failing "bus errors" cloud call stops the whole integration from loading

- Source issue: https://github.com/fustom/ariston-remotethermo-home-assistant-v3/issues/497 (open at check time; label: bug; opened 2026-10-22 14:29 UTC; 6 comments, all from users)
- Project: https://github.com/fustom/ariston-remotethermo-home-assistant-v3 (MIT, 291 stars per the API). Latest release v0.19.9 (2026-01-09); latest commit on the default branch is dated 2026-02-06 per the API.
- Checked: 2026-10-22 18:40 UTC

## Problem
The reporter says that since 2026-10-22 the Ariston cloud returns HTTP 500 ("An error has occurred.") for the `busErrors` request, with and without `blockingOnly`. They say the other requests for the same token and gateway (features, data items, menu items, energy reports) still return 200 with live data. Because the integration waits for that one request during setup, a 500 makes Home Assistant log "Failed setup, will retry: 500", and all entities become unavailable. Their setup: integration and library 0.19.9, a GALEVO device.

## The design point
The reporter says the bus-errors data is not critical and that the setup should carry on without it, leaving only the bus-errors sensor unavailable while the endpoint is broken. They name the exact call that makes it fatal. We checked the project's default branch: the file `custom_components/ariston/__init__.py` does call `bus_errors_coordinator.async_config_entry_first_refresh()` at line 124, as they describe. Home Assistant's documentation says this first-refresh call raises "not ready" when the first update fails. We did not re-check that page today. So the report's code claim is consistent with the source we read.

## What commenters say
Six users replied; five say a local edit suggested in the issue fixed it for them, one adding that a plain reload of the integration did not work for them and a restart of Home Assistant did. These are user reports. We do not repeat the edit here or recommend editing installed integration files: the change is outside the project's release, it is overwritten on update, and we have not tested it.

## Status
- No reply from the maintainer, no linked fix or pull request, and no release since January. The project's recent history is slow, so a quick fix is not something we can predict.
- It is a vendor cloud fault, not a bug in this integration alone: the integration treats one failing vendor endpoint as fatal. We cannot say how long Ariston's side stays broken.

## What this does not tell you
- It does not say the 500 is gone or that other devices behave the same. The reporter has one device type.
- It does not say that the unfixed bus-errors data is safe to ignore for your heating system. That is the reporter's view.

## Honest limits
- We did not run Home Assistant or call Ariston's cloud. The 500 response is the reporter's observation.
- State may have changed since 18:40 UTC.
