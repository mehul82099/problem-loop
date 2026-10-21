# AlphaESS Home Assistant integration fails at setup: Cloud API timeouts and 504s (Oct 18-20)

- Source issue: https://github.com/CharlesGillanders/homeassistant-alphaESS/issues/285 (open at check time; opened 2026-10-18 22:56 UTC; last update 2026-10-20 23:10 UTC)
- Checked: 2026-10-21 00:20 UTC

## Problem
Starting around 18 October 2026, users of the AlphaESS integration for Home Assistant (a custom integration) reported that it would not start. The log shows a connection timeout calling `https://openapi.alphaess.com/api/getEssList`. The reporter (Home Assistant Core 2026.10.2, integration 0.8.5, an Australian system) said DNS, TCP port 443 and the TLS handshake worked from the Home Assistant terminal, but unauthenticated GET and empty POST requests got no HTTP response. They asked if it was related to a regional server migration. That link is the reporter's question only; nobody in the thread confirmed it.

Others said the AlphaESS mobile app and cloud login still worked while the integration did not. One said reinstalling did not help and no verification code arrived. One was on an older Home Assistant (2026.5.2) with the same result, which points away from a recent Home Assistant change.

## What the maintainer said
A collaborator on the repo said it was a 504 from the AlphaESS Cloud API, outside what the integration can control, and that `getEssList` is the first call made, so it is the one that shows up as failing. They also said Home Assistant retries failed integration setups periodically (they thought about every five minutes, with "i think" in their words) and data logging should resume once the API recovers. Their advice was to avoid deleting the system from the integration while the API is down.

## How it played out
- By 2026-10-19 04:51 to 07:09 UTC, several users wrote that it was working again with no changes.
- One user said it was still down on 2026-10-20 until they disabled and re-enabled the integration. They also quoted a reply from AlphaESS support that blamed a "Bad Gateway" and pointed to a different portal URL. The maintainer said that portal looks like a separate web interface not tied to the open API. We did not visit that portal and do not recommend it.
- On 2026-10-20 at 23:10 UTC a user posted that it had been working normally for a couple of days and called the issue resolved.
- The issue was still open at check time.

## Practical takeaways, as stated in the thread
- If the cloud API returns timeouts or 504s while the mobile app works, the thread says the fault was on the vendor's cloud side, not in Home Assistant.
- The maintainer's advice was to wait and not remove or reinstall the integration. One user said a disable then enable fixed their case. We did not test it.
- Credentials (API key and secret) are not needed again in the cases described.

## Honest limits
- We did not run the integration or call AlphaESS's API. The vendor side cause rests on the maintainer's statement and users' reports, and we found no status page or notice from AlphaESS.
- Timing (start 18 October, recovery 19 to 20 October) comes from user comments in different time zones. Exact outage times are not established, and different users may have been hit by different problems.
- The mention of support's reply is a commenter's quote, which we could not verify.
- Repo facts at check time: MIT license, 146 stars.
