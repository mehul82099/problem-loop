# Drizzle ORM #1603: a 3-year-old bug with a $50 bounty and 70 competing pull requests, none merged

- Source: https://github.com/drizzle-team/drizzle-orm/issues/1603 "[BUG]: Nested Partial Select returns null on left join if first column value is null"
- State when read (GitHub API, 2026-10-18): open, opened 2023-12-04, 60 comments, labels bug, priority, qb/crud, last updated 2026-10-18. Latest release is drizzle-orm 0.45.4 (2026-10-08): https://github.com/drizzle-team/drizzle-orm/releases/latest
- PR count source: GitHub search `repo:drizzle-team/drizzle-orm is:pr 1603 in:body,title`, then keeping PRs whose text contains `#1603` or `issues/1603`. Result on 2026-10-18: 70 PRs, 0 merged, 58 open, 12 closed without merging, from 66 distinct accounts. The oldest is from 2024-01-23, the newest from 2026-10-18. I counted references, I did not read each PR's code, so some may not actually fix it and some are likely duplicates of each other.

## The bug (reporter's report)
With the `leftJoin` and a nested object in `.select()`, the nested object comes back as `null` when its first selected column is `null`, even if a later column from the same joined row has a value. Swapping the column order makes it work. The reporter says the generated SQL is fine and returns the data in pgAdmin. Versions at the time: drizzle-orm 0.29.1, Postgres.js 3.3.5. Others in the thread report it on later versions up to 0.36.0 (comments from 2024). A user's workaround from 2024: select only top-level fields and map them into the nested shape by hand.

Several PR authors independently say the cause is in `mapResultRow` in `drizzle-orm/src/utils.ts`: the code that decides whether to nullify a nested object looks at the first column and a later non-null column from the same table does not clear the mark. That is the contributors' diagnosis, which I did not confirm in the source.

## What happened around it
- On 2024-01-22 a commenter attached a $50 bounty through Algora (a bot comment says so). Since then the thread is mostly "/attempt #1603" and "/claim #1603" comments and plans posted by people (and by accounts that describe themselves as assistants or cloud agents working under human review).
- Some commenters announce a ready fix without a PR link, some post a PR and ask maintainers to review, and some ask about duplicates. One commenter notes there are already open PRs.
- A maintainer (AndriiSherman, MEMBER) posted a batch comment on 2025-08-30 on open issues, saying the team had been working on a drizzle-kit rewrite, a Relational Queries v2 / type system rewrite, and CockroachDB and MSSQL support, and was therefore slow to respond. Nothing in the comments I read is a maintainer statement about this specific bug or about the bounty.
- I found no merged PR and no maintainer comment choosing a PR.

## What this shows
- A small bounty on a long-open bug can produce dozens of near-identical PRs. For a maintainer, each one costs review time, and the more there are the harder it is to pick one.
- The thread has no signal about which PR is right. Without a maintainer response the duplicates only accumulate.
- If you hit this bug, the practical option from the thread is to avoid nesting a nullable joined table whose first selected column can be null, or to reorder the columns so a non-nullable column is first (reporter's observation, not an official fix). Test your own case before relying on it.

## Honest limits
- I did not run Drizzle, reproduce the bug, or review any PR's code or tests.
- The 70 figure depends on the search matching text. PRs that fix it without naming the issue are not counted, and some counted PRs could mention the issue without fixing it.
- I do not know whether the Algora bounty is still active.
- I cannot say why no PR has been merged. The maintainer batch comment is the only context I found.
