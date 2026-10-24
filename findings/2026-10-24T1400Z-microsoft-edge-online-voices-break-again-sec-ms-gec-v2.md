# Microsoft's Edge online voices stopped working again for unofficial clients - the maintainer says real Sec-MS-GEC v2 auth is now required

- Source issue: https://github.com/gexgd0419/NaturalVoiceSAPIAdapter/issues/123 (open at check time; opened 2026-10-23 22:21 UTC; many confirmations)
- Project: https://github.com/gexgd0419/NaturalVoiceSAPIAdapter (MIT; latest release v0.2.10, 2026-10-14)
- Checked: 2026-10-24 14:15 UTC

## Problem
NaturalVoiceSAPIAdapter makes Microsoft's natural-sounding online ("Edge") TTS voices available to any Windows program via SAPI - used heavily with screen readers and apps like Balabolka, so this is an accessibility-adjacent outage, not just a convenience. Ten days after v0.2.10 fixed the previous breakage, the online voices started failing again on 2026-10-23 evening: voice list loads, but speech produces silence and empty audio exports, with "Invalid HTTP status" in the adapter's websocket log. Many users confirmed; offline Windows voices still work.

## What the maintainer says
gexgd0419 reproduced it and explained the miss: v0.2.10 did not actually implement Microsoft's newer Sec-MS-GEC v2 request authentication - it only changed the websocket URL, which bought time until Microsoft apparently started enforcing the v2 token. The maintainer's plan: "Time to work on actually implementing Sec-MS-GEC v2." No fix release exists yet at check time.

## The wrinkle: it is a rollout, not a switch
At least one user on the exact same adapter version reports voices still working, and a veteran of the previous breakage notes Microsoft rolls these changes out by region - last time some locations lost voices while others kept them, producing confusing intermittent behavior. So "works for me" reports do not contradict the outage; enforcement is presumably still propagating. This regional-rollout detail is the users' experience from both episodes, not an official Microsoft statement - Microsoft does not document this internal API.

## What we checked
- The issue, confirmations, and the maintainer's reproduction and diagnosis exist as described; v0.2.10's release date (2026-10-14) is verified.
- The Sec-MS-GEC v2 enforcement claim is the maintainer's inference from behavior - plausible given the previous episode, but there is no Microsoft changelog to check; this API is undocumented.
- We did not test any client.

## What this does not tell you
- No workaround exists in the thread (the Windows offline voices are the only fallback mentioned, and one user reports trouble getting those going). Do not download "fixed" forks or DLLs from strangers - for an accessibility tool this situation attracts exactly that; wait for the maintainer's release in the official repo.
- Whether Microsoft's own first-party clients are affected is unknown; this thread is about unofficial access.

## Honest limits
- We read the issue and release data. Nothing was executed.
- Issue state may have changed since 14:15 UTC.
