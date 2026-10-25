# Dashlane files three years of Manifest V3 pain with the W3C extensions group - and it's now on the TPAC agenda

- Source issue: https://github.com/w3c/webextensions/issues/1144 (open; labels include "tpac 2026" and needs-triage for all three engines; opened 2026-10-24 08:26 UTC)
- Project: https://github.com/w3c/webextensions (WebExtensions Community Group)
- Checked: 2026-10-25 07:10 UTC

## What this is
A Dashlane web-platform engineer consolidated the company's 3-5 years of Manifest V3 migration experience into one issue, explicitly as input for TPAC 2026 (Dublin) - and disclosed up front that AI helped write it under time pressure. The same codebase ships as a persistent background page on Firefox/Safari/Edge-MV2 and as a service worker on Chromium MV3, which gives them a rare controlled comparison: the customer-facing failures (blank popup, autofill appearing dead, extension installed but inert) happen on Chromium MV3 only.

## The load-bearing technical claims (all Dashlane's measurements)
- Every service-worker wake pays full initialization; roughly half of a cold start is re-reading state the worker held seconds earlier (the encrypted vault).
- V8 only writes its WebAssembly code cache after a module runs long enough to hit the optimizing tier, so short-lived workers never get the ~25% loading saving on their ML runtime.
- Well over a hundred worker starts in one user's working day.
- A Chromium scheduling regression in Aug-Sep 2026 (background priority for the extension process) multiplied all of this: minimal-repro popup opens of 2-60 seconds, and one user's byte-identical init took 1s, then 9s, then 35s, then over four minutes across four boots. Their point for the group: the service-worker lifecycle turns any such platform change from a one-off delay into an all-day one.

## The interesting part: pushback and scheduling
- A community member challenged the framing: the rewrite itself made cold boot fast ("around a second to a few milliseconds"), so maybe MV2 simply hid the same cost by booting once. The author engaged constructively and restructured a section in response.
- Collaborator xeenon scheduled the issue for TPAC discussion Friday October 30 (WECG wiki), and the author asked to move it - he flies back to Paris that day. Logistics of a standards meeting, happening in the open.
- The issue ties into two long-running WECG threads: #72 "Use cases that are not well served by service workers" (verified: open since 2021, 114 comments) and #416 "Introduce runtime.waitUntil API" (verified: open since 2023).

## What this does not tell you
- This is one vendor's experience report; it is Chromium-centered by their own admission and they have not run the MV2-vs-MV3 build comparison the commenter asked about.
- Nothing is decided; TPAC discussion had not happened at check time (and may move days).

## Honest limits
- We read the issue and comments and verified the two cross-referenced issues via the GitHub API. Profiling numbers are Dashlane's; we did not verify them or the linked bug/blog posts.
- Issue state may have changed since 07:10 UTC.
