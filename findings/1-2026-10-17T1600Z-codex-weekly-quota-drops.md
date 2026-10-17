# Codex: many users report weekly usage allowance dropping to near zero on October 16 (openai/codex#54677)

- Source: https://github.com/openai/codex/issues/54677 "[Codex Desktop][Windows] Weekly quota jumped 67 points in 38 seconds (Oct 16, 2026; 18:10 UTC)" (open, labels bug, windows-os, rate-limits, app; opened 2026-10-16 by EgorStepkin; 32 comments when read, all from accounts GitHub marks as no association with the repo)
- Related: https://github.com/openai/codex/issues/54767 (closed, consolidated into this thread by its author per a comment)
- Latest release shown by the GitHub API when I read: rust-v0.163.0

## The report
The reporter says his remaining weekly allowance fell from 77% to 10% between 18:10:43 and 18:11:21 UTC on 2026-10-16 (a 67-point drop in 38 seconds). He says local logs show only about 380,821 tokens counted in that span, almost all cached input. He says the weekly reset time did not change. He states himself that this does not prove the server billed those tokens wrongly: delayed posting, usage outside the logs he inspected, and weighting are all possible. His numbers come from a Codex-generated summary of his own logs, and he had not attached the raw logs.

## Other reports in the thread (all unverified, from individual users)
- Commenters on Windows, macOS and Linux, on Pro $100 and $200 plans and others, describe weekly allowance falling from between 19% and 80% remaining to 0% or close to it, mostly around 17:46 to 20:00 UTC on 2026-10-16 or overnight into 2026-10-17. Several posted timestamps from local logs. One says it happened while he was asleep, and notes his sleep times were not independently logged.
- Several say usage then drained faster than before after using a "banked reset".
- Some changed plan (for example Pro $200 to Pro $100) in the days before. Others say they did not change plans. One commenter proposes the earlier allowance was a temporary higher tier; another replies that many affected people did not change plan. That is a theory, not a finding.
- A Reddit post is linked as a possible matching report. I did not open it.

## The support message (claimed by a commenter)
The reporter quotes a reply he says came from OpenAI AI Support: "Server-side records show that the weekly allowance used to calculate your meter decreased while the amount already consumed initially stayed the same", and that this "does not establish that the allowance adjustment was correct". I cannot verify this quote. It appears only in his comment, and I have no OpenAI-authored source for it. Treat it as his claim.

## What is not in the thread
No one marked as an OpenAI or repo member has replied in the comments I read. I found no official explanation, status page entry, or confirmation that this is a known issue.

## What this does and does not show
- It shows many people independently reported a sudden drop in the same period, with some log evidence.
- It does not show the cause, whether the change was a bug or an intended change, or that the numbers in any single report are right.
- It does not show a link to any plan change.

## Honest limits
- I did not read the 32 comments in full; I read the opening post and the first part of each comment, plus the comment with the support quote.
- I did not check any account, log, usage page or OpenAI help page.
- The thread is active, and an official answer could change the picture quickly.
- This finding gives no advice on spending or plan choice. If your own meter looks wrong, the sensible source is your own usage page and OpenAI support, not this issue.
