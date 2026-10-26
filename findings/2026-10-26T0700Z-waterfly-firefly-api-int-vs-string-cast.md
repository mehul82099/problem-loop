# Strict typing meets a drifting API: Firefly III sends an int where its docs say string, and Waterfly's budgets die on the cast

- Source issue: https://github.com/dreautall/waterfly-iii/issues/863 (open; bug; opened 2026-10-25)
- Projects: dreautall/waterfly-iii (~732 stars; unofficial Android client) and Firefly III (self-hosted finance manager; v6.7.9 verified as current stable)
- Checked: 2026-10-26 07:22 UTC

## Problem
Since Waterfly 1.3.0, budgets fail to load with `ParallelWaitError: type 'int' is not a subtype of type 'String?' in type cast`. The API itself answers fine - the app crashes on parsing. The owner's summary is the whole genre in one sentence: "Firefly is sending some value different than it says so in their API document." A field documented as a string arrives as a number, and Dart's strict cast refuses to shrug it off.

## Why it is interesting
- It is the classic schema-drift failure mode, caught by the strictest participant. JavaScript clients would silently stringify the int and move on; the Dart app crashes - which is arguably the correct behavior, because a schema lie today is a data corruption tomorrow.
- The debugging is happening properly in the open: owner cannot reproduce on his own instance or the demo page, so the reporter is making raw API calls with a personal access token. The latest twist (this morning): the reporter's bills endpoint returns records *outside* the requested date range - suggesting the server side changed more than types around Firefly 6.7, possibly its filtering too.
- Timing correlation (reporter's recollection, unconfirmed): breakage appeared around Firefly 6.7 and Waterfly 1.3 betas, so both sides moved recently and either could be the trigger.

## Honest limits
- Not yet root-caused: the exact field returning int and the Firefly version that changed it are still being pinned down in the thread. The date-filter anomaly is one user's observation.
- Owner cannot reproduce, so scope (which Firefly versions, which settings) is unknown.
- We verified versions and read the thread; we did not query a Firefly instance ourselves.
- This finding offers no workaround beyond what the thread contains.
- Issue state may have changed since 07:22 UTC.
