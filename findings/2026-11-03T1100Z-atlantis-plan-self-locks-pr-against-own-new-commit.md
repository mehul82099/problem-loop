# Atlantis: pushing a commit while plan is running locks the pull request against itself and fails the new head

**Source:** [runatlantis/atlantis#7050](https://github.com/runatlantis/atlantis/issues/7050) - opened 2026-11-03 by dorkamotorka (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

If `atlantis plan` is already running on a pull request and a new commit is pushed to that same pull request, the new commit's (auto)plan is rejected because the pull request is locked by its own in-progress plan:

```
cannot run "plan": pull request <N> is currently locked by "plan" for commit <old-sha>.
Wait until the previous command is complete and try again.
```

Nothing else holds the lock. The new head is then marked `atlantis/plan: failed`, and it stays failed after the older plan finishes, because that plan's output belongs to the previous commit. Re-running plan only works after the stale command fully finishes, and someone must trigger it manually. `atlantis unlock` does not clear it - the lock is the in-memory pull/working-directory lock of the running command, not a project lock in the UI. The reported workaround is `--disable-autoplan`, which avoids the self-lock only by not planning new commits at all.

## Root cause (reported, verified against current source)

The reporter traces it to the pull-level lock taken at the start of plan (`PlanCommandRunner.lockPullForPlan` -> `WorkingDirLocker.TryLockPull`). I checked current `main`:

- `server/events/working_dir_locker.go`, `TryLockPull` (~line 91): if a lock for this pull key already exists it returns `d.pullLockError(...)`; it also rejects when `findCommandLock(repo, pull, command.Plan, "")` finds a plan command lock for the pull *regardless of commit SHA* - which is exactly the old plan still running on the previous head.
- `server/events/plan_command_runner.go`, `handleNoProjectPlanStateError` (~line 404): on that lock error it sets a `FailedCommitStatus` for `command.Plan` (via `commitStatusUpdater.UpdateCombined`) and posts the error on the pull, then returns - the in-progress plan is not cancelled, and no plan for the new head is queued.

So a newer commit on the same pull request fails because the pull request is still planning an older commit, and the failure persists after the old command ends. The reporter notes that #6646 (v0.40+, "include commit SHA in working directory lock errors") made this visible by naming the owning commit in the lock message; that message is accurate, but the outcome is wrong.

Related, but distinct per the reporter: #305 and #4829 (both open) ask for cancelling or queueing the in-progress plan when a new commit arrives; #5556 (open) covers a second command refreshing the working directory out from under a running plan.

## Verification and environment

- Reproduced by the reporter against current `main` (v0.49.0; the release exists, published 2026-10-25). Trigger is default autoplan; a manual `atlantis plan` overlapping a push hits the same `TryLockPull` path.
- Code anchors above verified on `main` as of 2026-11-03: the lock-key rejection and the failed-status-then-return behavior are as quoted. Related issues #305, #4829, #5556 are open; #6646 is closed/merged.

## Limits

- The reproduction sequence is from the issue; it was not re-run here against a live Atlantis deployment. The mechanism follows directly from the verified code paths.
- The reporter's association is NONE. The only comment on the issue is the reporter's own internal-tracking note, so there is no maintainer position yet on whether this is a bug versus intended locking semantics (the deployment note on #6646 reportedly treats the overlap as a way to observe the lock message).
- Scope is the pull-level plan lock path; whether apply or other commands have an analogous self-rejection was not assessed.

## Sources

- Issue: <https://github.com/runatlantis/atlantis/issues/7050>
- TryLockPull (main): <https://github.com/runatlantis/atlantis/blob/main/server/events/working_dir_locker.go>
- handleNoProjectPlanStateError (main): <https://github.com/runatlantis/atlantis/blob/main/server/events/plan_command_runner.go>
- Related: <https://github.com/runatlantis/atlantis/issues/305>, <https://github.com/runatlantis/atlantis/issues/4829>, <https://github.com/runatlantis/atlantis/issues/5556>, <https://github.com/runatlantis/atlantis/pull/6646>
