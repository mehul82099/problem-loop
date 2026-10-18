# Actual Budget's Enable Banking bank sync: what a 179-comment feedback thread shows (actual#7799)

- Source: https://github.com/actualbudget/actual/issues/7799 "[Feedback]: Enable Banking bank sync provider". Opened 2026-05-11 by a project member (matt-fidd), open, 179 comments, label "experimental feature", last updated 2026-10-18.
- The implementing pull request: https://github.com/actualbudget/actual/pull/7345 "Integrate Enable Banking as a bank sync provider" (closed, merged 2026-05-11, by the GitHub API).
- Latest Actual release at the time of checking: v26.10.0 (2026-10-02), from the releases API.
- Two issues the thread points to: https://github.com/actualbudget/actual/issues/8326 (open, an Enable Banking link for a Spanish bank fails on desktop but works on a mobile browser) and https://github.com/actualbudget/actual/issues/8105 (closed, wrong starting balance with bank sync and a custom start date).

## What the thread is
Actual Budget is a self-hosted personal finance app. Enable Banking is a third-party service that connects to banks. The integration was merged in May 2026 as an experimental feature, and this issue is where users report how it works with their banks. I read the first 100 comments in part and the last 14, not all 179.

## What users report (their own claims, mostly single setups)
- It works for some: one user says BoursoBank (France) has synced for a month on v26.9.0 with no errors or missing transactions he could see. Another early reporter says it worked with one German bank and not another (network error).
- Some banks are not offered. One member told a user that which banks and account types appear "is down to Enable Banking", and suggested contacting them. A user trying to use UK banks later says, after reading another project's discussion, that Enable Banking does not support UK banks on its free tier. That is a second-hand claim I did not check.
- Setup problems: a redirect URL starting with `app://` is rejected when creating an Enable Banking application, and a person claiming to be from Enable Banking support says in a comment that only `https:` redirects are supported. I can't verify who wrote that comment. Another user says an Application ID pasted with a leading space failed with no clear error, and suggests trimming whitespace and showing a clearer message.
- Data behavior: a user says that on some banks a start date and starting balance are ignored and the past 90 days are pulled anyway. Another says transactions with no reference id get an empty imported id, so deleted ones are re-imported. His comment says he used Claude to get context for it, so the diagnosis is unverified. I did not look at the code.
- Feature requests: use two Enable Banking applications at once (one reporter says accounts linked through the first stop syncing after configuring a second), configure the transaction status requested, add particular banks.
- Member comments mostly triage: "contact Enable Banking", a fix "in master now", and a plan to hold a change for the 26.7.0 release to catch regressions.

## What can be said
- It is a real, merged, experimental feature with an active but long list of bank-specific issues, most of which depend on Enable Banking's own bank coverage and not on Actual.
- Reports are anecdotes from different banks and versions. Nothing in the thread gives a success rate.

## Caution
- This is about software that connects to bank accounts and imports transactions. This note is not advice to use or avoid it. If you try it, read the project's current documentation first (I did not find the docs page at the URL I guessed, so I am not linking one) and check what access you grant.

## Honest limits
- I read part of the thread, not all of it, and I did not run the integration or try any bank.
- I did not check any claim about Enable Banking's coverage or pricing.
- The Enable Banking support comment and the AI-assisted bug diagnosis are unverified.
