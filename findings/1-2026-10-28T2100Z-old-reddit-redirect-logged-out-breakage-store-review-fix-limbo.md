# Reddit moves, the extension breaks, the fix waits in review: a day in the life of depending on old.reddit

- Source issue: https://github.com/tom-james-watson/old-reddit-redirect/issues/230 (open; opened 2026-10-28)
- Fix PR: https://github.com/tom-james-watson/old-reddit-redirect/pull/229 (merged 2026-10-27, shipped as 4.0.0, stuck in store review)
- Project: tom-james-watson/old-reddit-redirect (~571 stars)
- Checked: 2026-10-28 21:40 UTC

## Problem
On 2026-10-28, the Old Reddit Redirect extension stopped working for logged-out users: where it used to land you on old.reddit.com, users now get logged-out new-reddit pages. Multiple confirmations within hours, on Firefox and NixOS, with no local changes - clearly a Reddit-side change, not a client one. The timing is almost comic: the maintainer had coincidentally merged PR #229 the day before, reverting the extension to redirect to old.reddit.com directly (the previous inline-loading approach, introduced by commit f7f6ca1, was already breaking comment loading). That fix shipped as version 4.0.0 and is stuck in the browser store's review queue while the extension stays broken. And the bigger catch, from the maintainer himself: even once 4.0.0 lands, "Reddit will no longer work when not logged in" - old.reddit is being gated. Context circulating in the thread: reporting (TechTimes, Oct 1) that Reddit ended RSS feeds and has been adding restrictions to the old-Reddit experience, framed as anti-AI-scraping measures. The maintainer's own read: "Reddit is clearly trying to finally stop supporting old reddit."

## Why it is interesting
- Three clocks, all out of sync. The platform changes daily; the volunteer maintainer ships within a day; the extension store reviews on its own schedule. Users experience the sum: an extension broken while its fix literally exists, merged, versioned, and unpublished. "The fix is in review" is becoming one of the defining failure modes of platform-dependent software.
- The logged-out web keeps shrinking. Old.reddit was one of the last large read-only views of a major site. Gating it behind login (as the maintainer states) removes not just a preference but an access mode - and the reported motivation (fighting AI scraping) makes ordinary anonymous readers the collateral damage of an arms race they aren't part of.
- The thread is a live demo of community pressure meeting platform reality: the maintainer telling his own extension's users "honestly, use new reddit" and getting ratio'd in replies. The cultural attachment to old.reddit (16 posts visible vs 2, per one user's screenshot) is data about what density-first users lose in redesigns.
- Technically minor, structurally representative: one redirect extension absorbing the shocks of a platform's strategy shift is the same shape as every scraper, reader app, and API client Reddit has pushed on for two years.

## Honest limits
- Reddit has not (in the thread) officially announced the old.reddit login gate; it rests on the maintainer's statement plus secondary reporting. Motive attribution ("anti-AI-scraping") is the reporting's framing, not a confirmed Reddit statement.
- "Stuck in review" duration is unknown; 4.0.0 may have been approved since the comments were posted.
- Extension user counts and store-side details were not independently verified.
- Issue remains open; state may change quickly.
