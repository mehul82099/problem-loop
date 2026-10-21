# Libation: "You were denied a content license" and Audible throttling

- Source issues: https://github.com/rmcrackan/Libation/issues/2110 (open, opened 2026-10-19), https://github.com/rmcrackan/Libation/issues/2096 (open, opened 2026-10-04), plus closed #2064 and open #2077 for context
- Checked: 2026-10-21 03:20 UTC

## Problem
Libation is an open-source desktop app (GPL-3.0, 6347 stars at check time; latest release v14.2.2, published 2026-09-16 per API) that downloads and decrypts the Audible audiobooks a user owns. Since early October 2026, many users report downloads failing with: "You were denied a content license ... Audible says this account is being throttled. This can also happen with an old device registration." The in-app message itself says Audible changed something in early September 2026 and says it cannot be certain every recovery step is needed. Several reports say the Audible phone app still downloads the same books.

## What the thread says
Replies below are from commenters, including some GitHub marks as CONTRIBUTOR. We do not name them.
- Recovery steps in the app's own message, repeated in the threads: deregister entries named "Libation" in the Amazon devices page, remove the account in Libation settings, re-add it with the same region, scan, and retry. After that, wait 24 to 48 hours or longer, because Audible also applies temporary rate limits.
- Several users in #2096 say that removing and re-adding the account fixed it for them (reports dated 2026-10-08 and 2026-10-10). Others say the same steps did not help (2026-10-06 to 2026-10-20).
- A contributor says Audible counts throttled attempts against you, so repeated retries or timed auto-scans can lengthen the wait. They advise stopping for about 24 hours before one more try.
- Some users report that changing the device emulation setting helped them, in both directions: Mac or iOS to Android in some cases, and Android back from iPhone in another (#2064, #2096, #2110). A contributor also says Widevine mode seems more stable. These are individual reports, and one user says switching to iOS did not help.
- Contributors suggest downloading one title with the stoplight button instead of "liberate all", and testing with a title you know you own as Premium. They say that has cleared the block for some people.
- On 2026-10-20 a contributor wrote that next steps "remain speculative", suggested setting parallel downloads to 1, an optional daily limit, and trying a different device registration. They also said one user's log showed "nothing enormously new". One later comment concluded it is the account, not just the device. This is an observation, not a proven cause.
- One user said that on a day the phone app also queued a download without finishing, and that it then downloaded hours later with no change from them. That suggests a vendor side delay for them, but it is one report.

## Caution
- Deregistering devices or deleting accounts changes your Audible/Amazon account setup. Do it only if you understand it, and follow the app's own instructions, not a summary.
- Libation automates access to an Audible account. We take no position on terms of service, and we did not check Audible's rules. Repeated automated retries are described in the thread as making throttling worse.
- This finding does not recommend any specific emulation mode or setting.

## Honest limits
- We did not run Libation or contact Audible, and did not read the log files attached in the threads.
- The cause (an Audible change in early September, account throttling) comes from the app's message and contributors' statements, not from Audible. We saw no Audible statement.
- Success and failure reports are anecdotes with no consistent pattern. We do not know why the same steps work for some people and not others.
- The docs links in the threads (getlibation.com) were not opened by us.
- No fix is claimed. #2110 and #2096 were open at check time.
