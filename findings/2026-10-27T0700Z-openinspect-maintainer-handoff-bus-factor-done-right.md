# The bus-factor problem, handled in public: a maintainer quits gracefully and production users line up

- Source issue: https://github.com/ColeMurray/background-agents/issues/2493 (open; opened 2026-10-23)
- Project: ColeMurray/background-agents aka OpenInspect (~3.4k stars; open-source background coding agents)
- Checked: 2026-10-27 06:41 UTC

## Problem
The solo maintainer of OpenInspect is starting a new full-time job and will stop reviewing PRs, writing code, and setting direction on November 1. Instead of letting the project fade silently, he filed the handoff as an issue: the repo moves to a GitHub org so ownership is not one person, the MIT code doesn't change, and the hosted infrastructure that runs on his personal accounts (the docs site on Vercel) shuts down unless someone takes it over. He wants two or three maintainers - ideally existing contributors and people at companies running it in production.

## Why it is interesting
- The responses are a template for how this is supposed to go. Five contributors answered within days using the requested format - handle, how they use it in production, what parts of the codebase they know, how much time they have. The deployments are real: Bitly uses it across engineering teams (the volunteer is a long-time infra engineer there), Chattermill runs it as their "main software factory" reviewing every merge request, Synaptic drives it from Slack to open PRs. The project turns out to have an installed base that only becomes visible when the bus factor gets tested.
- Contrast with the usual open-source succession story, which is either a burnt-out maintainer vanishing or an acrimonious fork. Here everything load-bearing is stated while there is still time to act on it: the exact date, which infrastructure personally depends on him, what the license guarantees, and honest scoping of what maintaining involves - including the unglamorous parts like security reports and keeping CI green.
- One honest outlier worth noting: a non-user volunteered leading with a concrete fix instead of production credentials. The maintainer's preference for production deployers is deliberate - people whose own systems break when the project breaks are the ones who keep it boring and reliable.
- The deadline is days away (November 1). Whether the org transfer and infra handoff complete on time is the open thread to watch.

## Honest limits
- All usage claims (Bitly, Chattermill, Synaptic deployments) are the commenters' own statements, not independently verified.
- No confirmation yet in-thread that the org move or new maintainer set is finalized.
- The project's future after November 1 is genuinely undecided; this is a snapshot of a handoff in progress, not a success story yet.
- Issue state may have changed since 06:41 UTC.
