# Home Assistant: Rituals Perfume Genie reports "Invalid authentication" for many users on 21 October

- New issue: https://github.com/home-assistant/core/issues/187887 (open at check time; label: integration: rituals_perfume_genie; opened 2026-10-21 16:28 UTC; 6 comments, 8 reactions)
- Older issue with the same title, reopened by comments today: https://github.com/home-assistant/core/issues/171993 (closed 2026-10-05; 9 comments)
- Library migration PR (merged to `dev` 2026-10-05): https://github.com/home-assistant/core/pull/184313
- Checked: 2026-10-21 22:35 UTC

## Problem
The reporter says the Rituals Genie integration shows "Invalid authentication" in Home Assistant 2026.9.3 (Home Assistant OS). They removed and re-added the integration, rebooted, and reset their Rituals password, with no change, while the Rituals mobile app still logs in with the same credentials. A commenter says it is an API problem on Rituals' side and that they see it on an existing install. Others add "same here". Comments on the older issue #171993 say it started "all of a sudden" around 12:00 to 12:30 UTC on 21 October after months of working, on Home Assistant 2026.10.2.

## What one detailed comment says
On #171993 a commenter (at 18:10 UTC) writes that Home Assistant first showed `Too many login attempts` and then `No success token` after the lockout expired. They say they tested separately on a Mac with the `ritualsgenie 0.1.0` library, that old and new passwords were both rejected, and that the login request returned HTTP 200 with the body `{"success": false}` and no error message. They suggest a server-side change at Rituals and note the failure also happens with the new library. We cannot verify that test.

## Background from the project
- Home Assistant's earlier thread (#171993) was closed on 2026-10-05 by a project member who said the likely cause was Rituals' login lockout: after too many login attempts, Rituals answers like it does for a wrong password, and the old library could not tell the two apart, so Home Assistant kept asking for the password and each retry extended the lockout. They said PR #184313 replaces that library, so the integration recognizes the lockout, does not ask for a password because of it, and tries again later, and that it "will be in the next release".
- We checked the files in the Home Assistant release tags by API: the manifest in `2026.9.3`, `2026.10.0` and `2026.10.2` lists `pyrituals==0.0.7`, so as far as we can tell the new library is not in any 2026.10 release. It is in the development branch, per the merged PR. Another merged PR (#184519, 2026-10-17) stores the token in the config entry.
- On #171993 in June, a person who said they develop for Rituals wrote that they still saw many Home Assistant users log in successfully in their logs. We cannot verify that identity.
- A Home Assistant member posted the standard "please react with a thumbs up instead of +1 comments" notice on the new issue. No one from the project or from Rituals has said what is behind today's failures.

## What this does not tell you
- It does not say what is wrong today. Candidate causes in the threads are Rituals' lockout behavior and an unannounced change at Rituals. Neither is confirmed.
- It does not say the new library or the pending Home Assistant change would help, since one commenter says the new library also fails for them.
- One commenter says deleting the integration "does nothing". We do not advise for or against it. Repeated login attempts may extend a lockout, per the project's earlier explanation.

## Honest limits
- We did not run Home Assistant, the integration or either library, and did not call the Rituals API.
- We verified the PR states, merge dates, release tags and manifest requirements by API. Everything about causes comes from commenters and the earlier project reply.
- The picture may have changed since 22:35 UTC.
