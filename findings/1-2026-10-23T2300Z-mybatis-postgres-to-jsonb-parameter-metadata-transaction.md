# MyBatis 3.6: PostgreSQL `to_jsonb(?)` calls now fail inside a transaction unless the parameter type is explicit

- Source issue: https://github.com/mybatis/mybatis-3/issues/3829 (open at check time; label "bug"; opened 2026-10-23 09:40 UTC; 4 comments)
- Failing-test PR: https://github.com/mybatis/mybatis-3/pull/3832 (draft; "Reproduce PostgreSQL parameter metadata failure in active transactions"; test code only, marked by its author as AI-assisted drafting with results checked)
- Project: https://github.com/mybatis/mybatis-3 (Apache-2.0, about 20k stars per the API); releases: 3.5.19 (2025-01-02), 3.6.0 (2026-10-23)
- Checked: 2026-10-23 23:50 UTC

## Problem
The reporter says that with MyBatis after 3.5.19, PostgreSQL statements using `to_jsonb(?)` (and similar typed-function parameter calls) now error unless the parameter type is given explicitly (a `:: boolean` cast or `jdbcType=`). They first thought it was a blanket change, then narrowed it: it happens only inside a transaction (`autoCommit = false`) - an earlier parameter-metadata call produces an error (PostgreSQL `42804`) and the transaction then fails the UPDATE with `25P02`. The same statements worked on 3.5.19.

## What the thread says
- A second person reproduced it on master (commit 10ae003e) with PostgreSQL 18.6 and pgjdbc 42.7.14: the failure appears only when an earlier statement has started the transaction; `autoCommit=false` alone did not reproduce it for them. Explicit `jdbcType=BOOLEAN` avoids it. Their testing, not ours.
- A maintainer asked for a minimal reproducer, and the second person opened draft PR #3832 with a Testcontainers test: two intentionally failing cases (Boolean/String parameters after a `SELECT 1` started the transaction), eight controls passing, and all ten methods passing on 3.5.19. The PR author discloses AI assistance in drafting the tests; we did not review the test code and cannot vouch for what it proves.
- No production fix and no maintainer verdict on the intended behavior yet. Notably, 3.6.0 was released the same day the issue was filed.

## What we checked
- The issue, the draft PR, and the release timeline all exist as described (3.5.19 in January 2025, 3.6.0 on 2026-10-23).
- The PostgreSQL error codes and behavior come from the two reporters; we ran no database.
- The reporter's framing - "this might not really be a bug but it is definitely a change of behavior missing from the release notes" - is still open: the maintainers have not said whether the change was intended.

## What this does not tell you
- Which versions are affected: the reporters show 3.5.19 works and current master fails, but the exact version where behavior changed is not established in the thread.
- Whether explicit casts/jdbcType are a permanent fix or just a bypass is undecided.
- If you upgrade to 3.6.0 and use PostgreSQL typed functions with implicit parameter types inside transactions, this thread is the warning sign to test first; the trigger conditions are the reporters' account.

## Honest limits
- We read the issue, the PR listing, and release data. Nothing was executed.
- Issue state may have changed since 23:50 UTC.
