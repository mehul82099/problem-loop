# A fork, a co-maintainer offer, and a possible reunion: Meerkat CRM's maintainer-bandwidth drama resolves in public

- Source issue: https://github.com/fbuchner/meerkat-crm/issues/256 (open; opened 2026-10-21)
- Project: https://github.com/fbuchner/meerkat-crm (~298 stars; self-hosted personal CRM, Go + React)
- Checked: 2026-10-26 05:20 UTC

## Problem
Meerkat CRM's single maintainer fell behind: 17 open pull requests, 25 open issues, some contributor PRs unanswered for two months, Dependabot updates waiting a month. A repeat contributor (omarkohl) opened an issue doing the polite-but-direct thing: here is my fork with my improvements, and I volunteer as co-maintainer.

## Why it is interesting
- The thread then surfaced the cost of the stall: omarkohl discovered that back in July, another contributor whose PRs sat unmerged had quietly hard-forked into mycorrhizal-crm (verified: repo exists since 2026-07-24, actively pushed) and racked up 2,000+ commits. The forker, DrewBrunning, confirmed in-thread there had been little discussion at the time. Unanswered PRs do not just delay features; they split communities.
- The owner responded within days: merged the open PRs, started on the issue backlog, added AI-assisted PR reviews to stretch limited review time (his framing), and welcomed omarkohl as co-maintainer. omarkohl then floated the bigger question - merging mycorrhizal-crm back upstream - explicitly naming the tradeoff between one person's creative control and many shoulders.
- A bystander comment captures the stakes for small self-hosted projects: users had watched the Monica CRM stall before, and a second maintainer is continuity insurance, not just velocity.
- It is a rare public example of the healthy path: no flame war, a direct ask, a discovery, an honest admission, and a plausible reunification - all in one thread.

## Honest limits
- Everything is from the thread participants; whether the fork actually merges back, and how co-maintenance works out, is undecided at check time.
- Commit counts and fork activity are as stated in the thread plus repository metadata we verified (creation date, push recency, star counts); we did not audit code divergence between the forks.
- Issue state may have changed since 05:20 UTC.
