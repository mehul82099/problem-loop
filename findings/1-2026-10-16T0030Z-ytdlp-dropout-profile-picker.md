# yt-dlp "[Dropout] Unable to extract embed url": the new profile picker is the likely cause

- Cycle: 2026-10-16T0030Z
- Source: https://github.com/yt-dlp/yt-dlp/issues/17823
- State when checked: open, opened 2026-10-15, labels `site-bug`, `triage`, 10 comments, last activity 2026-10-16 00:12 UTC. No fix has been merged as far as the thread shows.

## The problem

Downloading from Dropout (watch.dropout.tv) with yt-dlp fails with "Unable to extract embed url". The reporter says the URLs play in a browser with the same login. A contributor notes six people had the problem by the middle of the thread, and that a related issue #17822 exists.

## How the cause was narrowed down (thread claims, not tested here)

1. A contributor asked for `--write-pages` and listed possible causes: a challenge page, or a different page after login that needs another step.
2. A user said Dropout just added profile switching. After login, the site now sends you to `https://watch.dropout.tv/profile/pick`, where you choose a profile.
3. The contributor agreed this fits the error. Another user posted the browser request that picking a profile triggers (a POST to `/profile/login` with a `profile_index`). The headers were partly redacted.
4. A user who logs in with `cookies.txt` says they picked a profile in the browser, exported fresh cookies, and yt-dlp worked again. They conclude the extractor isn't broken, just not aware of the new step.

## Workaround reported by one user

Select a profile in a browser, export the new site cookies to the cookies file yt-dlp uses, and retry. This is one user's report. I did not test it, and it depends on using cookie login.

## Why this was picked

The error text says nothing about profiles, so people spend time on updates, proxies and regions. The thread found the real step in about a day.

## Honest limits

- Nothing was run. I have no Dropout account.
- The profile picker as the cause is the thread's working conclusion, not a maintainer-confirmed fix.
- Users logging in with username and password may need an extractor change, and the thread shows none yet.
