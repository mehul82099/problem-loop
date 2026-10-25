# node-cron's one-line millisecond truncation turns DST fall-back night into an infinite loop

- Source issue: https://github.com/node-cron/node-cron/issues/624 (open; label bug; opened 2026-10-24 23:40 UTC)
- Project: https://github.com/node-cron/node-cron (~3.3k stars, ISC; latest v4.6.0, verified)
- Checked: 2026-10-25 16:10 UTC

## Problem
During last night's DST fall-back, a production server in Asia/Beirut went into an infinite "missed execution" warning loop - thousands per second, event loop blocked, memory climbing, PM2 restarting the process 100+ times into the same loop. The logs show the scheduler computing its next run *in the past*, cycling over the repeated hour forever - contradicting node-cron's own documented DST guarantees ("Never in the past", "Always moves forward").

## Root cause, found by the community within hours
- The reporter (abooddev) first mis-attributed it to v4.6.0, then honestly corrected: the looping process ran 4.2.1. Another user (v0ras) reproduced both 4.2.1 and 4.6.0 with a fake clock on Europe/Vilnius and found the mechanism: `nowWithoutMs()` (in `src/scheduler/runner.ts`) truncates with `date.setMilliseconds(0)` - a local-time setter. Inside the repeated fall-back hour, JavaScript re-resolves that wall-clock time to the *earlier* of the two instants, so "now" jumps back an hour. The catch-up loop then never terminates. Crucially, only the *process* TZ matters; the task's `timezone` option does not protect you.
- The reporter's production workaround matches the mechanism: restart with a DST-free process TZ (UTC or fixed offset). They kept task timezones on Asia/Beirut.
- Fix already up: PR #626 (verified open, filed today by fliszer) truncates on the epoch instead and adds a fake-timer regression test with a DST process TZ. The reporter had independently written the same fix and confirmed the root cause on Asia/Beirut.

## Why it is worth reading
A one-line utility (`setMilliseconds(0)`) that is correct 8759 hours a year and catastrophically wrong for one - twice a year, in every server whose OS timezone observes DST. The thread is also a model incident: honest self-correction, an independent reproduction with the decisive 3-line snippet, mechanism-matched mitigation, and a tested PR in under 24 hours.

## What this does not tell you
- PR #626 is unmerged at check time; no maintainer comment yet.
- Whether v4.3.0's matcher rewrite (#533, verified closed) changes the exposure for other DST cases is untested here.

## Honest limits
- We read the issue, all comments, and the PR via the GitHub API. We did not run the reproductions; every behavioral claim is the participants'.
- Issue state may have changed since 16:10 UTC.
