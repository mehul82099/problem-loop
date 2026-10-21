# Dyson Spot+Scrub Ai (RB05) in Matterbridge: live cleaning map errors and unreliable Apple Home commands

- Source issue: https://github.com/thoukydides/matterbridge-dyson-robot/issues/51 (open at check time; label: bug; opened 2026-10-20)
- Plugin releases (API): v1.13.0 published 2026-10-20 16:36 UTC, v1.12.5 on 2026-10-18
- Checked: 2026-10-21 05:25 UTC

## Problem
matterbridge-dyson-robot (ISC license, 15 stars at check time) is a Matterbridge plugin that exposes Dyson robot vacuums as Matter devices. A user with a Dyson Spot+Scrub Ai (RB05, firmware RB05PR.01.109.6314.260713) on plugin v1.12.5 and Matterbridge 3.10.14 in Docker says:
- the robot shows up in Apple Home as a Matter robot vacuum, but cleaning commands are sometimes delayed or not carried out;
- while cleaning, the log repeats `DysonCloudError: Unexpected Dyson Cloud API response structure` roughly every 3 to 4 seconds when polling the live cleaning map. The pasted lines say values in `cleanPath[...].update` and `robotLocation.id` are not the expected types.
The reporter says they cannot tell if the errors and the unreliable commands are related.

## What the maintainer said (the repo owner, per GitHub's association field)
- Support for this model is new, completely untested, and based on information from other open-source projects and partial packet captures. The reporter was the first to give feedback on it. The maintainer does not own an RB05 to test on.
- The repeat interval matches the plugin's live-map polling. An automated assistant reply in the thread said the plugin's type definitions accept only numeric 0 or 1 for `update` and a number for `robotLocation.id`. That is an automated comment, not the maintainer.
- The maintainer asked for a full debug log with `wildcardTopic` and `debug` enabled and three debug features switched on, covering a full clean. They said the plugin redacts serial numbers and credentials, but users should check the log before posting.
- On 2026-10-20 16:54 UTC they released v1.13.0 (which they said fixes a number of issues for another Dyson model) and said it might help the RB05 too, but without a full log they cannot tell. They asked the reporter to try it and send a log.
- On 2026-10-20 the maintainer also said that "extraneous fields" warnings and `REQUEST-CURRENT-FAULTS` messages would not cause significant functional problems.
- On 2026-10-21 the maintainer thanked the reporter for a log excerpt. They said it covered only two minutes, did not show the period when status fails to update, and in fact showed Matter attributes updating correctly as the robot returned to its dock. They said they would look at the `Unrecognised Dyson MQTT message` errors in it, which they expect are background noise, and again asked for a complete log of an entire cleaning run.

## Honest limits
- We did not run the plugin or touch any Dyson device. Every behaviour above is the reporter's or the maintainer's statement.
- No cause is established. The maintainer says the map-polling errors and the command delays may be unrelated, and that more data is needed. No fix for the RB05 is claimed. v1.13.0 is not shown to fix anything for this model.
- RB05 support is described by the maintainer as experimental. Treat results with that model accordingly.
- Debug logs for this plugin can contain account-related details. The maintainer says redaction happens automatically, but also asks users to review logs before posting. This finding does not repeat any log content beyond error names.
- Only one user report was in the thread at check time, so we do not know how many RB05 owners are affected.
