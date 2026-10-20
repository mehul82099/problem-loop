# Redlib: thread pages fail with 403 from Reddit, listings still work

- Source issue: https://github.com/redlib-org/redlib/issues/591 (open at check time; opened 2026-10-20 19:19 UTC)
- Related PR (open, not merged at check time): https://github.com/redlib-org/redlib/pull/592
- Checked: 2026-10-20 22:10 UTC

## Problem
Redlib is a self-hosted alternative front end for Reddit. The reporter says that since about 18:40 UTC on 2026-10-20 every comment/thread page fails with "Failed to parse page JSON data". Their server log shows a 403 Forbidden from Reddit on the comments `.json` endpoint, while subreddit listings still return 200 with the same OAuth token. Restarting the container (new token) did not help. They say a public instance showed the same error at the same time. Build used: current `main` (a4d36e9), which includes the TLS-emulation switch from PR #544.

## What commenters report (unverified by us)
- One commenter suggested static headers might have been blocklisted, as in an earlier Invidious incident (iv-org/invidious#5817, a closed issue titled "YouTube change - All instances are broken", verified by API). They said they were not sure it applies.
- Another commenter pointed to a Reddit moderator announcement about protecting communities from scrapers, which they say mentions deprecating JSON endpoints without authenticated access. We could not open that page (it returned 403 to our fetch), so we did not verify the wording or date.
- One commenter said that replaying a failing request with a signed-in app Bearer token worked, which they note would not help Redlib without an account system.
- A commenter tested with curl against `oauth.reddit.com`: the normal path `/r/<sub>/comments/<id>/...json` gave 403 (an HTML "blocked by network security" page), while encoding the slash between the subreddit and `comments` as `%2f` gave 200 with JSON. They said they changed `src/post.rs` and threads loaded again, and said Reddit may normalize `%2F`, so this may be temporary.
- A patch file and a fork built "with LLMs" were shared by other commenters. We did not read or run either, and do not recommend using them.
- A later commenter posted a longer analysis tied to PR #592. It says the block is path-based, not TLS or header based, lists which endpoints are and are not blocked, and describes a change in `client.rs` plus a clearer error message. Another commenter replied that this is the same workaround posted earlier by someone else. We make no claim about authorship.

## Cross-references verified by API
- PR #592 "fix(client): encode the subreddit/comments slash so thread pages load again": open, created 2026-10-20 21:50 UTC, not merged.
- PR #544 (TLS fingerprints, proxy support): merged 2026-04-24.
- PR #510 (cipher list change to avoid 403): merged 2025-12-16.

## Caution
Changing request paths or running patched or forked builds from comment threads is your own risk. This finding does not advise installing a fork or applying an unreviewed patch. Review the code first. Reddit's terms and rate limits are not discussed in the thread.

## Honest limits
- We did not run Redlib or make any request to Reddit's API. All technical claims here are commenters' reports.
- The "path-based block" and the `%2f` workaround are reported by several commenters but not confirmed by a maintainer in the thread at check time. PR #592 was unreviewed and unmerged.
- Whether Reddit intends a policy change is unconfirmed. The workaround may stop working at any time.
- Repo facts at check time: AGPL-3.0 license, 3857 stars.
