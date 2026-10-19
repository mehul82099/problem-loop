# Argo CD: rolling back an app that has auto-sync on (argoproj/argo-cd#9570)

- Source issue: https://github.com/argoproj/argo-cd/issues/9570 "Rollback aware auto-sync". Opened 2022-06-02, open, labeled "enhancement", 117 reactions, about 25 comments, last updated 2026-10-19.
- Docs statement, read 2026-10-19: https://github.com/argoproj/argo-cd/blob/master/docs/user-guide/auto_sync.md says "Rollback cannot be performed against an application with automated sync enabled."
- Open pull request that says it closes the issue: https://github.com/argoproj/argo-cd/pull/29926 "feat: allow rollback while auto-sync is enabled". Opened 2026-09-30, not merged (state open at checking time), 47 files changed.
- Related issues, all still open when checked: #5351 "Prevent autosync reconcile after rollback" (2021), #6494 "Rollback in middle of Sync operation should terminate/override existing sync" (2021), #8686 (2022, about prune on manual sync, linked by a maintainer as one of the "dots" to connect).

## The problem
With auto-sync on, the History and Rollback action in Argo CD is blocked, because the next auto-sync would push the app straight back to the newest Git commit. So the usual steps are: turn auto-sync off, roll back, fix or revert the bad commit in Git, turn auto-sync back on. The reporter asked for an option where Argo CD remembers the rolled-back commit and auto-sync skips it. His stated motive is automation: run tests in a post-sync hook, and roll back automatically when they fail.

## What the thread says
- Users say rolling back feels unsafe because Argo "will happily re-deploy shortly after" (comment, 2023).
- Apps created by an ApplicationSet make it worse. Commenters report that turning off auto-sync on the child app is undone by the ApplicationSet controller. One commenter suggests `ignoreApplicationDifferences` on `/spec/syncPolicy` in the ApplicationSet, with the catch that you must remember to turn auto-sync back on. I have not tested that, and it changes how the ApplicationSet manages the apps, so read the Argo CD docs before using it.
- A contributor said in 2024 that the History and Rollback dialog now offers to disable auto-sync for you. A later summary comment repeats this.
- A project member (2025-09-10) said the automated-rollback case is already covered by Argo Rollouts and its Analysis feature, which they say works with auto-sync. A later commenter wants a custom rollback action for pipelines instead. I did not test either.

## The open PR
- Per its description, the PR adds a feature that is off by default. It can be turned on for the whole instance with an `application.rollbackAwareAutoSyncEnabled` key in `argocd-cm`, or per app with `argocd app set <app> --rollback-aware`. While a revision is being skipped the UI says so and the app gets a warning condition you can alert on. These details are from the PR text, not from a release.
- On 2026-10-02 a project member (crenshaw-dev) asked that protection still behave sensibly if an unrelated commit lands, for example in a monorepo. On 2026-10-19 the PR author replied that, as built, the record keeps only the revision, so any new commit on the branch clears it and the next auto-sync brings back what you rolled back from. The author says path-based change detection does not help here, and prefers documenting the limit now and doing a comparison in a follow-up. That is the author's analysis. I did not read the PR code.

## What this means
- Today (per the docs), the manual steps are still needed. No release containing the PR exists as far as I could see, since the PR is open. Do not rely on `--rollback-aware` or the config key being available in your version.
- If the PR merges as described, the skipped-revision protection ends at the next commit of any kind to the tracked branch. A rollback would then not be a safe pause for a busy repository. This is the open design question in the thread.
- This note does not recommend a workaround. Changing sync policy on production apps can cause unwanted deploys or deletions, so test on a non-critical app first.

## Honest limits
- I did not run Argo CD, build the PR, or confirm the Argo Rollouts claim.
- I read the issue comments and the PR description, not the PR review threads.
- The issue has 117 reactions, which shows interest, not how many teams are affected.
