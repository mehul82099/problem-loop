# Dota 2's ghost guilds: creating a guild half-fails and the account gets stuck with no way out

- Source issue: https://github.com/ValveSoftware/Dota2-Gameplay/issues/36443 (open; no labels, no Valve response at check time; opened 2026-10-23)
- Tracker: ValveSoftware/Dota2-Gameplay (Valve's official community bug tracker)
- Checked: 2026-10-25 21:15 UTC

## Problem
Since October 23, players who create a new Dota 2 guild land in a broken half-state: the guild page never loads any data, trying to leave fails with "This guild does not exist," and because the account still counts as guild-affiliated, the player cannot join any other guild. There is no self-serve exit.

## What the thread shows
- This is a cluster, not one unlucky account: at least 19 distinct players replied "same" with their own Steam and guild IDs across three days, and the reports keep arriving.
- The reported guild IDs are close sequential numbers (roughly 1180673 to 1182143), consistent with a broad window of newly created guilds being affected rather than isolated corruption.
- Two different recovery wishes appear: most just want their account unstuck, but one user explicitly asks Valve to *restore* the guild - name and membership - rather than reset it. Any fix has to decide which of those it does, and resetting would silently destroy guilds some founders want kept.
- Screenshots from the original report show the empty guild page and the contradictory "does not exist" leave-error.

## Honest limits
- Everything here is user-reported; there is no Valve acknowledgment, root cause, or workaround in the thread at check time, and this finding offers none.
- "At least 19 affected" counts distinct commenters in one thread; total scope is unknown.
- We did not reproduce this (it requires spending the in-game guild creation cost on a live account).
- Players should be cautious posting account IDs publicly; the thread is full of them.
- Issue state may have changed since 21:15 UTC.
