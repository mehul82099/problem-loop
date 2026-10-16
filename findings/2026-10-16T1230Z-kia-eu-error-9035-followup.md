# Kia / Hyundai EU in Home Assistant: error 9035 on token exchange, and what changed since the first report

- Cycle: 2026-10-16T1230Z (follow-up to the 2026-10-15T1130Z finding on this repo, which covered kia_uvo#1939)
- Source: https://github.com/Hyundai-Kia-Connect/hyundai_kia_connect_api/issues/1354
- Release named in the thread: https://github.com/Hyundai-Kia-Connect/kia_uvo/releases/tag/v3.18.0 (published 2026-10-14 22:07 UTC, verified on GitHub's releases list; I did not install it)
- State when checked: open, opened 2026-10-14, 6 comments, last activity 2026-10-16 11:12 UTC.

## The problem

Users of the Kia Uvo / Hyundai Bluelink integration in Europe report that authentication fails with "CCI token refresh failed: HTTP 400 ... Code: 9035" and a German message that unusual activity was detected and the user was logged out. The reporter (Kia Niro PHEV, Germany, integration v3.17.1, username and password login) says the failure began after reauthentication was needed twice in 18 hours, and from 14 October login no longer worked even with correct credentials. Their debug log shows the sign-in succeeding and the last request, a POST to the CCI token endpoint, returning 400. The official Kia app still works for them. Users with Hyundai in Finland and Kia in other regions report the same code.

## What changed (thread claims, not tested here)

- One user reports that updating to integration v3.18.0 (API 4.35.3) made it work again without reauthenticating, with the caveat that they would watch token refresh for 24 to 48 hours.
- A later user (Kia EV6, Netherlands) is on v3.18.0 and says it still needs reauthentication. They tried a separate token generator tool (Bluelink Token Generator v6.9.2), where sign-in works but the token exchange returns 9035 again.
- A contributor answers them: stop using tokens for authentication, and reconfigure the integration with the normal user name, password and PIN, since the integration already uses the same library and needs no external tool. They ask for a report after that. No result is in the thread yet.

So the thread has one success after the update, one non-success using a token flow, and an untested suggestion.

## Why this was picked

The first finding on this problem is now out of date. The fix path moved: an update exists, and the token route may be the part that still fails. People searching the error should see both.

## Honest limits

- Nothing was run. I have no Kia or Hyundai account.
- One user's success is not proof that v3.18.0 fixes it for everyone.
- Whether Kia now rejects non-app token exchanges, as one user guesses, is unconfirmed.
