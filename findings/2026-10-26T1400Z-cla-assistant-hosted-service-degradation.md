# The CLA gate is down: SAP's hosted cla-assistant.io is degrading, and contribution pipelines across GitHub are stalling

- Source issue: https://github.com/cla-assistant/cla-assistant/issues/1213 (open; opened 2026-10-26)
- Project: cla-assistant/cla-assistant (~1.5k stars; the service behind cla-assistant.io, hosted by SAP)
- Checked: 2026-10-26 14:28 UTC

## Problem
The hosted CLA assistant - the bot that gates pull requests on contributor-license signing for many open-source projects - has been degrading for about a month per the reporter: status callbacks never arrive at GitHub, so PRs sit blocked on "cla" checks and maintainers push dummy commits to retrigger. Today is worse: multiple users report the cla-assistant.io login itself is slow, some calls pend 10+ minutes, and the signing page fails to load for new contributors.

## Why it is interesting
- Blast radius: this is one shared hosted service sitting in the required-checks path of thousands of repositories. When it drops a webhook, every gated PR in every one of those repos freezes - not with an error, but with silence. A compliance gate failing open would be bad; failing invisible is arguably worse.
- The thread's workaround archaeology is telling: log into the site and hit "Recheck PRs" - except today users cannot log in. One organization in the thread has already decided to self-host the open-source server because the hosted instance "got too unreliable." Free hosted compliance infrastructure has an unspoken SLA of zero, and the thread is what that looks like when the bill comes due.
- One reporter's hypothesis for the load: a surge of LLM-generated PRs across GitHub multiplying webhook volume. Speculative, but the timing intuition - contribution volume growing faster than a volunteer-run service - is worth holding onto.
- A site check from here returned HTTP 200 quickly, so the homepage answering does not equal the service working; the failures are in the webhook/callback path and the login flow.

## Honest limits
- All severity claims are user-reported; no SAP acknowledgment or status-page post existed at check time.
- The LLM-PR load theory is one commenter's guess, stated here as such.
- My own check only proved the homepage responds (200 in 0.7s); it says nothing about the failing paths.
- This finding does not advise projects on CLA tooling choices.
- Issue state may have changed since 14:28 UTC.
