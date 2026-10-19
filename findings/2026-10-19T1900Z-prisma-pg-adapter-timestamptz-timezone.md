# Prisma: `@db.Timestamptz` is read wrong with the pg driver adapter when the database time zone is not UTC (prisma/orm#26786)

- Source issue: https://github.com/prisma/orm/issues/26786 . Opened 2025-03-30, open, labels include "kind/bug", "topic: postgresql", "topic: driverAdapters" and "bug/1-unconfirmed". 11 reactions on the post, 7 comments, latest 2026-10-19. (The repo was moved from prisma/prisma; GitHub redirects the old address.)
- Open pull request: https://github.com/prisma/orm/pull/29481 "fix(adapter-pg): correctly handle TIMESTAMPTZ reads and writes on non-UTC servers", by an outside contributor (matingathani). Opened 2026-04-17, not merged at checking time (open, 5 files), last updated 2026-08-25. Reviews on it so far are from review bots and one human comment.
- The PR text says it also closes https://github.com/prisma/orm/issues/28629 , a separate issue about writes.

## The problem
The reporter followed Prisma's docs to use the node-postgres driver adapter. With a `DateTime @db.Timestamptz()` field and a PostgreSQL session time zone other than UTC (he used Asia/Tokyo), values read back are wrong. He says it does not happen without driver adapters, nor with node-postgres alone, and gives a reproduction repository.

## What the thread and PR say
- Several users (2025) say it blocks them from moving to driver adapters, for example "the main reason why our system cannot proceed to the driver adapter".
- The PR author says (2026-04-17) the cause is in `normalize_timestamptz` in the pg adapter's conversion code: it replaces the time zone offset text with `+00:00` without converting the time. His example: `09:26:34.887-06` came back as `09:26:34.887+00:00`, six hours off. His change converts through a JavaScript `Date` before printing. He says the PR also fixes writes, where no time zone suffix was sent and the server read the value in its local zone, and adds a regression test. These are the author's statements. I did not read the code diff or run the tests.
- On 2026-10-19 a commenter says it still happens on `@prisma/adapter-pg` 7.8.0 with PostgreSQL 18, for reads and writes, and posts a short script plus output. With the session zone set to Asia/Karachi (UTC+5), the adapter returned `17:00:00+00:00` for a stored `12:00 UTC` value, while PostgreSQL's own text was `17:00:00+05`, which is the same instant shown in local time. For writes he reports the stored UTC value as `07:00:00` where `12:00:00` was expected. The same comment says a Prisma write then read cancels the two errors, so application tests pass while psql, pg_dump and SQL using `now()` see times off by the session offset.
- His stated workaround is to set the session zone to UTC in the connection options (`-c TimeZone=UTC`) and as a role setting (`ALTER ROLE ... SET TimeZone = 'UTC'`). That is one user's suggestion, not an official one. Changing a role's time zone affects every connection of that role, so test it first.

## What can be said
- Two independent reports (the original and the 2026-10-19 one) describe wrong values and the PR author gives a cause. No Prisma maintainer has confirmed it in the thread, and the issue still has the "unconfirmed" label.
- If your database is on UTC you would not see it, per these reports. If your session zone is not UTC and you use the pg adapter with `timestamptz`, check a known value by comparing what the app returns with what `SELECT at::text` shows in psql.
- The fix is in an open PR and not in a release, as far as I could see.

## Honest limits
- I did not run the reproduction or Prisma. The numbers above are from the commenter's posted output.
- I did not read the PR diff or check whether the adapter code on the main branch has changed since the PR was opened.
- The mention that the issue is "unconfirmed" is a label, not a ruling by maintainers on whether it is a bug.
