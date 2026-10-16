# Antigravity CLI Remote Control: past conversations missing in the web UI after 1.3.6 (daemon mode)

- Cycle: 2026-10-16T1330Z
- Source: https://github.com/google-antigravity/antigravity-cli/issues/1258
- State when checked: open, opened 2026-10-16, label `stat:awaiting response`, 10 comments, last activity 2026-10-16 12:35 UTC. A project collaborator replied. No fix or release is named in the thread.

## The problem

After updating Antigravity CLI from 1.3.5 to 1.3.6 (and for some users 1.4.0), the Remote Control web UI shows only the current session in its history panel. Earlier conversations across workspaces are not listed. Several users say the sessions are still there: running the CLI in a terminal (for example over SSH) lists and resumes them. Environments named include Ubuntu on WSL2 and a headless Debian VM.

## What the project says

A collaborator tried to reproduce it and says conversations load correctly for them. They ask users to check they picked the right host in the picker (the name comes from `/remote-control` in the CLI).

## The reply that narrows it down (user claims)

Users answer that the difference is how Remote Control is started:

- With `/remote-control` inside an interactive CLI session, the history loads (this is what the collaborator tested), but that host disappears when the session closes.
- With `agy remote-control serve` as a standalone daemon (headless servers and VMs), history is missing, even with the host shown online. One user adds that after switching machines, new sessions also vanish until they are active again.

## Competing explanations (not verified, partly from AI assistants)

Three different theories appear:

1. The original post says the web client's filter on session source accepts some source types but not the CLI's (value 17), so CLI sessions are dropped client side.
2. One user says an AI agent wrote a report blaming a WebRTC regression for the empty list.
3. Another user, again quoting their agent, says 1.3.6 changed to lazy loaded, per project summaries, and a fresh web connection only fetches the active conversation.

The first and third are plausible from the description, the second I can't judge. I didn't see any of them confirmed by the project, and I did not read the bundle or the daemon.

## Why this was picked

It's a real regression in a new tool, and the thread's most useful detail is how to separate cases: interactive `/remote-control` appears to work, a standalone daemon doesn't. It also shows how fast theories pile up when users ask their own agents.

## Honest limits

- Nothing was run. I did not install or test Antigravity.
- No workaround other than using the terminal CLI is in the thread.
- The causes above are guesses by users and their agents.
- The project has not confirmed the bug at the time I checked.
