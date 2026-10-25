# Reddit's 403 on "load more comments" breaks Old Reddit Redirect's whole current strategy

- Source issue: https://github.com/tom-james-watson/old-reddit-redirect/issues/228 (open at check time; no labels; opened 2026-10-23 15:47 UTC)
- Project: https://github.com/tom-james-watson/old-reddit-redirect (browser extension, ~567 stars, MIT)
- Checked: 2026-10-25 02:05 UTC

## Problem
Since about 2026-10-22, clicking "load more comments" while viewing the old Reddit design through the extension returns "403 forbidden" (or spins forever, per one Firefox report). Multiple users confirm across Firefox versions, logged in or not.

## Why this is bigger than one broken button
The extension's own README explains its current design: Reddit now requires an account to use `old.reddit.com`, so instead of redirecting there, the extension (v3.0.0, rewritten for this) opts you out of the redesign so that `www.reddit.com` itself serves the old design. Reddit's change appears to break exactly that path - the old design served from the `www` host - while the real `old.reddit.com` host still loads more comments fine. In other words, Reddit broke the specific mechanism the extension was rebuilt around.

## The thread's own diagnosis (all attributed)
- Maintainer tom-james-watson: if it also happens on www.reddit.com with old reddit set in user preferences (extension off), "it's a reddit problem, not the extension", and "old reddit is on its last legs, whatever way."
- User GitHubRub ran the control test: with the extension disabled, comments load on old.reddit.com but do not load on www.reddit.com with the redesign opt-out. That is the clearest evidence in the thread that the break is host-specific and Reddit-side.
- No fix or extension update exists at check time; one user suggests "permalink" as a manual workaround (opens the comments on their own page).

## What this does not tell you
- Whether Reddit's 403 is a deliberate move against the opt-out path, a bug, or an A/B rollout - there is no Reddit statement in the thread, and speculation in the comments is just that.
- Whether the maintainer will ship a workaround (e.g. steering expansion requests to old.reddit.com), and whether that is even possible given the login requirement there.

## Honest limits
- We read the issue, all ten comments, and the extension README via the GitHub API. We did not test Reddit or the extension ourselves; every behavioral claim is a user's or the maintainer's.
- Do not treat any commenter's workaround as vetted beyond "users report it"; none involves running anything.
- Issue state may have changed since 02:05 UTC.
