# Claude Code Desktop: scheduled tasks start in "Manual" mode and stall on permission prompts (claude-code#77817)

- Source: https://github.com/anthropics/claude-code/issues/77817 "[BUG] v2.1.206 silently broke unattended scheduled tasks: runs no longer inherit permissions.defaultMode, fall back to Manual, and per-task mode has no programmatic or bulk control"
- State when read (GitHub API, 2026-10-18): open, opened 2026-07-15 by jakedmochowski-ww, 10 comments, updated 2026-10-18. Labels: bug, regression, platform:windows, area:permissions, area:desktop, area:routines, and a "stale" label was added at some point.
- Related issues, state checked by API: #33027 (open, "Always allow" missing from scheduled-task prompts), #76141 (closed 2026-09-18), #76469 (closed 2026-09-07), #76340 (closed 2026-09-12). The closed ones were not read for their resolution, so I do not know whether they were fixed or merged as duplicates.

## What the reporter says
- On Claude Code Desktop for Windows 11, scheduled tasks worked unattended through v2.1.205 and broke from v2.1.206. Before, runs inherited `permissions.defaultMode` (he used `bypassPermissions`) from the project's `.claude/settings.local.json`. After, each task has its own mode that he says can only be set in the desktop app's Edit form, and existing tasks fell back to Manual.
- Evidence he gives: session transcripts from 2.1.205 show `"permissionMode":"bypassPermissions"`, and from 2.1.209 show `"permissionMode":"default"`, with no settings change on his side.
- He says the changelog for 2.1.206 only mentions renaming "default" to "Manual", and that a Manual-mode scheduled run does not fail or notify, it just waits on the prompt.
- His requests: honour a global default again, expose the permission mode in `create_scheduled_task` / `update_scheduled_task` or the task file, preserve the previous mode on migration, say so in the changelog, and alert on stalled runs. He explicitly says he is not asking for bypass by default.

## What other commenters add (all unverified user reports, none are maintainers)
- Two more users report the same on Windows, a third reports it on macOS. One macOS user first measured that all 6 runs spawned in "default" did zero turns, then corrected his method after the reporter pointed out that the saved `permissionMode` is the final mode, not the spawn mode. His re-measure: 23 of 77 sessions spawned in "default".
- One user with about 33 routines says adding `"permissions": {"defaultMode": "auto"}` to the project settings still left the session in `default`.
- One user on Cowork scheduled tasks says "grant for all scheduled runs" does not persist and that a stalled run still reports success. That is a related but separate claim.
- A commenter says the mode can be read after a task's first run from `local_<sessionId>.json`, which carries `scheduledTaskId` and `permissionMode`. I did not verify the path or file contents.
- Two comments suggest outside guards (a phone-approval step for risky actions, an external start/finish heartbeat monitor). One of them is a promotion of the commenter's own free product. I did not test either and am not endorsing them.

## Takeaways
- If you run unattended scheduled tasks in Claude Desktop, one reasonable habit is to check that a task actually ran and finished, instead of trusting the app's status, because several reports say stalled runs look quiet.
- Reports disagree on whether the per-task setting is honoured when it is set, so I would not assume any single setting fixes it.
- This finding does not advise turning permission checks off. Loosening permissions on tasks that send, delete, pay or push has real risk, and the reporter himself says he is not asking for bypass by default.

## Honest limits
- I did not run Claude Desktop, reproduce any of this, or read release notes. The version-by-version behaviour is the reporter's account.
- The issue is Windows-labelled and desktop-specific, and the other platforms rest on single comments.
- I do not know whether the bug is fixed in the newest release. The thread has no maintainer reply that I could see, and the "stale" label is automation, not a statement about the bug.
