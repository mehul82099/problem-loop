# DPD Germany integration for Home Assistant stops logging in (ERROR_PARTNER / ERROR_KEYPHASE)

- Source issue: https://github.com/ha-parcel-integrations/ha-dpd/issues/21 (open at check time; label: bug; opened 2026-10-20)
- Pre-release: https://github.com/ha-parcel-integrations/ha-dpd/releases/tag/2.14.2b1 (published 2026-10-20 19:10 UTC, marked pre-release, verified by API)
- Checked: 2026-10-20 20:10 UTC

## Problem
The reporter says the DPD Germany integration stopped authenticating on 2026-10-20 (Home Assistant 2026.10.2, integration main at manifest 2.14.1; installed version not confirmed). The config flow shows "invalid email/password", but the myDPD website login still works for the same account.

Reporter's logs: the anonymous session bootstrap fails before credentials are sent. A standalone anonymous `getSessionFullState` SOAP request using the integration's signing logic returned HTTP 200 with `Ack=false`, `ERROR_PARTNER` (ErrorID 10003) and `ERROR_KEYPHASE` (10004), and no SessionToken. Home Assistant logged "DPD Germany did not return an anonymous SessionToken". The error text is a generic German "please try again later" message.

So the "invalid password" message was misleading: the failure happened before any password was checked. The reporter also asked that partner or signature errors not be shown as a wrong password.

## What happened in the thread
- Two more users reported the same failure (2026-10-20).
- A collaborator of the repo (account peter-mdf, association COLLABORATOR per the API) said they were looking into it.
- Later the same collaborator wrote that DPD switched off the app backend the integration used for Germany. This is the collaborator's statement; we found no DPD announcement.
- The collaborator said pre-release 2.14.2b1 instead reads parcels from the user's myDPD account on dpd.com, with the email and password already entered, and that it is verified against one real account. Feedback was requested, especially for parcels on the way, out for delivery or going to a pickup point.
- A later commenter says it worked for them. They had changed their DPD password in the meantime and had to delete and re-add the integration. The collaborator then wrote "let's hope it stays this way".

## Practical notes (as stated by the maintainer, not tested by us)
- The installation path given is HACS: open DPD, Redownload, pick 2.14.2b1. It is a pre-release, so it is less tested than a stable release.
- The integration signs in with your DPD account email and password. Using a pre-release that handles those credentials is your call. Read the release notes and source first.
- The issue only concerns the Germany variant. Other countries in the integration are not discussed.

## Honest limits
- We did not install or run the integration or the pre-release, and did not repeat the SOAP request.
- The cause (backend switched off) rests on the maintainer's comment alone. We did not find a statement from DPD.
- The thread shows two real-account confirmations at most. That is a small sample and the pre-release may change.
- The issue was still open at check time. No stable release with the change existed yet: the latest stable listed was 2.14.1.
- Repo facts at check time: MIT license, 14 stars.
