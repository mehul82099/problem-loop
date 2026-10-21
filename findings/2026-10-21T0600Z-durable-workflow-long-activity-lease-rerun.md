# Durable Workflow: activities longer than 5 minutes without heartbeats get re-run and never complete

- Source issue: https://github.com/durable-workflow/workflow/issues/878 (open at check time; labels include bug, priority:P1, status:in-progress; opened 2026-10-20 19:00 UTC)
- Related draft PR: https://github.com/durable-workflow/workflow/pull/879 (open, draft, not merged, opened 2026-10-20 19:45 UTC)
- Checked: 2026-10-21 06:25 UTC

## Problem
Durable Workflow (MIT, 1253 stars at check time) is a PHP (Laravel) library and server for long-running workflows and activities. The reporter says an activity that runs longer than 5 minutes without sending heartbeats is run again and again, and never completes, although the docs list activity timeouts as optional.

Reported reproduction (Server 2.9.9, Python SDK 2.6.1; we confirmed a server release 2.9.9 exists, published 2026-10-20 17:05 UTC): one activity that sleeps 330 seconds, with no timeouts, retry policy or heartbeats.
- Attempt 1's lease expired at about 5 minutes and the task was handed out again while attempt 1 was still running.
- When attempt 1 finished, its result was rejected with `409 stale_attempt` and discarded. Attempt 2 expired the same way, then attempt 3 started. The workflow stayed `waiting`.
- History showed only three `ActivityStarted` events, with no record of expiry, retry or failure.
- The same activity with a heartbeat every 30 seconds completed once, in 348 seconds.
The reporter also links source lines for a hard-coded 5-minute lease, and says the documented setting `DW_ACTIVITY_TASK_TIMEOUT` is not read by anything. We did not check those lines. They point at a specific commit, and that commit's date is 2026-10-20 (verified).

Practical effect, in the reporter's words: repeated work and duplicate side effects, some running at the same time, while the workflow waits with no visible reason.

## What the project said
All replies are from a repo member account.
- The report was accepted as a P1 product defect. They said that documenting a five-minute limit, or asking users to add heartbeats, does not meet the "optional timeouts" promise, and that a longer fixed lease alone would only delay recovery.
- Planned approach, as written: keep the original attempt authoritative while it is alive, without requiring heartbeats in user code; fence a lost or replaced worker; apply a bounded redelivery policy; and record expiry, redelivery and late refusals in history. The `DW_ACTIVITY_TASK_TIMEOUT` setting is to get one documented path.
- Progress notes through 2026-10-21 06:09 UTC describe tests-first commits, and a draft PR #879 ("Add bounded activity lease recovery and runtime renewal") with test counts and passing local runs on SQLite, PostgreSQL and MySQL. We did not rerun any of this. #879 was still a draft and not merged at check time. One note says server routes and worker-side renewal for the SDKs were still to come.
- A related follow-up in the thread (2026-10-21) says that when a worker shuts down cleanly, its leased activity tasks are not released, so an abandoned activity waits for its lease, or heartbeat timeout, before another worker can take it. Prepared changes for that were described as pushed to a branch, not merged.

## What this means for users (as described in the thread)
- Until a fix is released, activities with no heartbeats that run longer than 5 minutes are at risk of re-runs. The reporter's evidence says heartbeats avoid it in their test. The maintainers say heartbeats should not be required in the end.
- Side effects in such activities may run more than once. Making them safe to repeat is a user decision we do not advise on here.

## Honest limits
- We did not run Durable Workflow. The reproduction, source line claims and test results are the reporter's and the project's statements.
- At check time no released version was shown to contain a fix. The latest core release we saw was 2.9.0 (2026-10-21 03:48 UTC) and the latest server release 2.9.11. We did not check whether either includes the work in #879.
- The project's replies are very long, detailed status notes. We summarized and did not verify their test numbers or commit hashes except where stated.
- We cannot say how many users hit this. Only one report was in the issue.
