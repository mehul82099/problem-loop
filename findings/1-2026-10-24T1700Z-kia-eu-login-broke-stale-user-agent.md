# Kia EU logins broke on 2026-10-22 because the servers started rejecting the library's 2012-era User-Agent

- Source issue: https://github.com/Hyundai-Kia-Connect/kia_uvo/issues/1984 (open at check time; labels "Bug", "Kia", "Europe"; opened 2026-10-22 16:43 UTC)
- Fix: https://github.com/Hyundai-Kia-Connect/hyundai_kia_connect_api/pull/1416 (merged; "send a current Android Chrome User-Agent to the OneApp signin")
- Projects: https://github.com/Hyundai-Kia-Connect/kia_uvo (MIT; the Home Assistant integration) and its hyundai_kia_connect_api library
- Checked: 2026-10-24 17:15 UTC

## Problem
Since 2026-10-22, the kia_uvo integration's EU login fails with valid credentials: the Kia servers answer the sign-in POST with a 302 straight back to the login page, and no token exchange is ever attempted. Users verified their credentials in the official app, changed passwords, restarted - nothing, because it was never a credential problem. Existing sessions also began failing with "Authentication failed - returned to login page".

## Root cause (confirmed in-thread, fix merged)
A user (smasog) traced it with before/after response headers on an independent setup: since 2026-10-22 the Kia EU signin endpoint rejects the ancient `USER_AGENT_MOZILLA` string the library was sending. They opened a PR replacing it with a current Android Chrome User-Agent in both EU modules plus a regression test pinning the composed header - 9 lines net. The maintainer merged it (PR #1416, verified merged), and another user confirmed the EU master branch fixes their login. So this one has an ending: the cause is identified, the fix is merged to master. What is not clear from the thread: whether a numbered release of the library/integration containing the fix has shipped - at check time users are pointing at master.

## What we checked
- The issue, the maintainer exchange, the merged PR, and the user confirmation exist as described.
- The header-rejection diagnosis is smasog's tracing (described as confirmed on an independent setup); we did not replay the login flow ourselves. The merged fix and a user's "master fixes it" are the strongest signals.
- The old constant is still present in the library source, but the merged PR title says the signin now sends a current Android Chrome UA; we did not diff the merge line by line.

## What this does not tell you
- Whether Hyundai EU (same library family) was equally affected - the thread centers on Kia EU, though the fix touches both EU modules.
- This is a reminder of the genre: unofficial API integrations live and die by looking like the official app, and servers change the rules without notice. If your login broke around 2026-10-22, it was them, not your password.

## Honest limits
- We read the issue, the PR, and the current library source. Nothing was executed.
- Issue state may have changed since 17:15 UTC.
