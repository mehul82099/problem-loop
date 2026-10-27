# The merge landed the commit but GitHub forgot the rest - twice, five seconds apart

- Source issue: https://github.com/cli/cli/issues/14843 (open; opened 2026-10-27)
- Verified: cli/cli PR #14837 (the parallel victim); maintainer escalation in thread
- Project: cli/cli (~41k stars; GitHub's official CLI) - but the bug is in GitHub itself
- Checked: 2026-10-27 22:05 UTC

## Problem
A user ran `gh pr merge --squash` and got a haunted repository: the squash commit landed on main, but the pull request stayed open - `state: OPEN`, `mergedAt: null`, no `merged` event in the timeline, and no workflow run for the push. Filed as a CLI bug, it dissolved on contact: a maintainer (williammartin) realized a colleague's plain web-UI merge of cli/cli#14837 had produced the exact same zombie state five seconds earlier (merge commits timestamped 13:01:10 and 13:01:15 UTC). Two different clients, two different repos' workflows, one five-second window - this was GitHub's merge pipeline dropping the bookkeeping, not either client.

## Why it is interesting
- The split-brain merge is a nasty state to be in. The commit is on the base branch, so the work is "done"; the PR is open, so every dashboard, required-check, and automation layer thinks it is not. And because the push event was lost too, no CI ran on the landed commit - the worst combination: merged in fact, unmerged in every system that watches.
- Five seconds is a forensic goldmine. Two independent failures across unrelated repos and unrelated clients, timestamped five seconds apart, converts "intermittent CLI weirdness" into "something in GitHub's merge path had a bad moment at 13:01 UTC." The maintainer spotted the coincidence within minutes of the report and escalated to the pull requests team the same hour.
- It shows why "the same operation via the website works" is a weaker test than it looks. The reporter checked that (web merge of the same PR behaved correctly - a later retry), but the parallel victim WAS a web merge. Client-side A/B testing cannot clear the client when the bug lives in a shared backend window.
- The reporter's evidence discipline made the five-second connection possible: API queries for PR state, timeline events, and workflow runs, all captured before anything was retried. Zombie states are self-healing by retry; undocumented ones vanish.

## Honest limits
- Root cause unconfirmed: "backend merge-pipeline window" is inference from two correlated failures; GitHub has not posted an explanation at check time, and there is no linked status incident in the thread.
- Sample size is two confirmed cases (plus the reporter's intermittent history); blast radius unknown.
- The maintainer's escalation ("asked the pull requests team") is internal; no public follow-up yet at 22:05 UTC.
- Issue state may have changed since 22:05 UTC.
