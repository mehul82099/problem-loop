# Kueue: stale pull requests were not being closed, and what the thread found (kubernetes-sigs/kueue#17345)

- Source: https://github.com/kubernetes-sigs/kueue/issues/17345 "Create a GH action to mark PRs as stale and eventually close" (open, label kind/feature, opened 2026-10-16 by mimowo, 22 comments when read)
- Related items in the Kubernetes test-infra repository, state checked through the GitHub API on 2026-10-18:
  - https://github.com/kubernetes/test-infra/issues/38089 "`ci-k8s-triage-robot-close-issues` makes no progress: commenter skips reopened issues and skips consume `--ceiling`" (closed)
  - https://github.com/kubernetes/test-infra/pull/38090 "commenter: add --dedupe flag and don't count skips toward --ceiling" (merged 2026-10-16 21:18 UTC)
  - https://github.com/kubernetes/test-infra/pull/38091 "triage-robot: use --dedupe=latest for api-review" (merged 2026-10-16 23:06 UTC)
- GitHub Actions pricing page cited by a commenter: https://github.com/resources/insights/2026-pricing-changes-for-github-actions

## The question
Kueue (a job queueing project in the Kubernetes organisation) gets many pull requests, and the author says some are forgotten because nobody reviews them. mimowo proposed a GitHub Action that marks PRs stale after 30 days and closes them after another 30, so contributors seek reviewers before maintainers. Numbers could change.

## What others said (attributed)
- mbobrovskyi: a Kubernetes triage bot already does this across kubernetes-sigs with longer timers: stale after 90 days of inactivity, rotten after 30 more, closed after 30 more. He suggested a Kueue-specific job with shorter timers instead of a second bot working on the same labels.
- mimowo: the existing bot looks buggy for Kueue. He pointed at PR #4662, which he said had no activity for 1.5 years. I checked it: the PR is still open and the API shows its last update on 2026-08-26, after a bot comment he had linked. He wants bot comments not to extend a PR's life.
- kannon92 (CONTRIBUTOR) preferred fixing the shared tooling rather than each project running its own Actions workflows, and cautioned that Kubernetes has no official support for Actions and pointed at GitHub's Actions pricing changes. I fetched the page he linked: it is dated 2025-12-15 and says GitHub is postponing a billing change for self-hosted runners while reducing hosted-runner prices. It does not by itself show any risk to Kubernetes projects, which is his concern, not a statement on that page.
- mimowo replied with a table of other Kubernetes repositories that use GitHub Actions for various jobs, to show Actions are already widely used in the ecosystem.
- tenzen-y (MEMBER): the auto-close system is working, and old Kueue PRs stay open because when test configuration changes, the CI system re-runs tests on all open PRs and posts failure messages, which count as activity. mimowo called that a bug in effect.
- kannon92 found a separate fault in a different bot job (test-infra issue 38089, which concerns issues, not PRs): the commenter tool skipped any issue that already had an identical comment anywhere in its history, so issues the bot had closed and a human reopened were skipped forever, and skipped items used up the per-run limit of 10. He opened PR 38090, which adds a `--dedupe=latest` option and stops counting skipped items, and PR 38091 to use it. Both are merged, and on 2026-10-17 at about 12:20 UTC he wrote that he rolled out the fix and "it seems" to be closing issues and PRs again.

## What this shows and does not show
- Two different explanations were given for old PRs staying open: tenzen-y's (test failure messages count as activity) and the bug that 38089 fixed (reopened items being skipped). They may both be true, or only one may apply to Kueue's PRs. The thread does not settle this. The 38089 report is about issues, and the examples in the PR text are issues.
- Nothing in the thread says Kueue decided to adopt the 30 and 30 day policy. The issue is still open.
- I did not check whether the old PRs in Kueue have since been closed.

## Honest limits
- I read the issue and its comments, and the three test-infra items and the pricing page. I did not read the slide deck the author refers to (a Google Slides link).
- I did not read the bot's configuration or run any bot job.
- "Seems to be closing" is kannon92's own wording a few hours after rollout. I did not verify the result.
