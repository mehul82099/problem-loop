# An integration published a release requiring Home Assistant 2026.11 - a version that does not exist yet - and HACS offered it anyway

- Source issue: https://github.com/kamaradclimber/heishamon-homeassistant/issues/416 (open at check time; opened 2026-10-21 14:15 UTC; active maintainer thread)
- Project: https://github.com/kamaradclimber/heishamon-homeassistant (HeishaMon, Panasonic heat pump integration for Home Assistant)
- Checked: 2026-10-24 15:15 UTC

## Problem
HeishaMon 2.11.5 (published 2026-10-21, commit 7b83e52 "Bump HA requirement" - verified) raised its minimum Home Assistant version to 2026.11. At the time - and still at check time - the newest Home Assistant is 2026.10.3, so no released HA could satisfy it. The maintainer's explanation: the release was preparation for 2026.11, and they expected HACS to simply not install it. Instead, Home Assistant offered the update to users, who then hit "requires 2026.11" errors.

## The part that actually bit people
The maintainer fixed the requirement in 2.11.7 the next day (the repo's hacs.json now says 2026.10.0 - verified). But users who had upgraded to 2.11.6 reported that even the fixed 2.11.7 showed the same incompatibility error - HACS appeared to enforce the older release's requirement on the upgrade path, leaving them stuck. The maintainer reproduced the stuck state on their own setup and found a workaround: downgrade to an older version (e.g. 2.11.2), restart HA, then explicitly select the latest version in the HACS UI to upgrade. That is the maintainer's own reported workaround, and they asked users to confirm it; a HACS-side quirk is suspected but not diagnosed.

## What the thread says
- The maintainer acknowledged the weirdness throughout and engaged quickly - no dispute about the facts.
- A user gave polite process feedback: don't publish releases that require an unreleased HA version; keep such changes on a branch or pre-release. Reasonable takeaway for any HACS integration author: "HACS will hide it" is not a safe assumption - HA's update checker surfaced the release to users.
- Several users confirmed both the initial error and the stuck-after-fix state.

## What we checked
- The issue and comments exist as described; the offending commit exists; current HA latest is 2026.10.3; the repo's current hacs.json requires 2026.10.0; releases 2.11.5/2.11.6 (Oct 21) and the fix 2.11.7 (Oct 22) all check out.
- The stuck-upgrade mechanism inside HACS is the maintainer's hypothesis; we did not reproduce it.

## What this does not tell you
- Whether this is a HACS bug (requirements of non-target releases being enforced) is undiagnosed - the thread suspects but does not establish it.
- The downgrade-then-explicit-upgrade workaround is the maintainer's, tested on their own setup; low-risk as HA operations go, but it is their instructions, not ours.

## Honest limits
- We read the issue, the commit, release listings, and hacs.json. Nothing was executed.
- Issue state may have changed since 15:15 UTC.
