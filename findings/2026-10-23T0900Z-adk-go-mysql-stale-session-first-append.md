# Google ADK Go: on MySQL, the first AppendEvent after Create can fail with "stale session error"

- Source issue: https://github.com/google/adk-go/issues/1928 (open at check time; label "bug"; opened 2026-10-21; 8 comments)
- Code read on `main`:
  - https://github.com/google/adk-go/blob/main/session/database/storage_session.go (`createStorageSession`, line 50)
  - https://github.com/google/adk-go/blob/main/session/database/service.go (event-timestamp truncation at lines 384 to 385; stale check at lines 425 to 435)
- Prior fix the thread cites: https://github.com/google/adk-go/pull/414 ("set microsecond precision for gorm session service", merged), closing https://github.com/google/adk-go/issues/408 ("fix stale session error")
- Project: https://github.com/google/adk-go (Apache-2.0, about 8.9k stars per the API)
- Checked: 2026-10-23 09:55 UTC

## Problem
The reporter says that with MySQL-backed sessions, the first `AppendEvent` after `Create` fails about half the time with "stale session error: last update time from request (T) is older than in database (T + 1µs)". Their account: `createStorageSession` stores a nanosecond-precision `time.Time`, MySQL rounds it into a `datetime(6)` column, and when it rounds up the stored `update_time` is 1 microsecond newer than the in-memory value, so the stale check in `applyEvent` rejects the append. A retry after reloading the session works, because the reloaded value comes from the database.

## What the thread says
- A second developer reproduced it locally (macOS arm64, MySQL 8.4.8 in Docker, gorm mysql driver v1.6.0, go-sql-driver v1.10.0): with a creation timestamp of .123456789, MySQL stored .123457 and the first append failed. Their numbers, not ours; we did not run it.
- The same developer says a one-line change, truncating the creation time to microseconds in `createStorageSession`, made all their test cases pass, and removing it brought the failures back. Their report, unverified by us.
- A maintainer-side reply on 2026-10-23 invited that developer to open the PR. No PR was linked in the thread when we checked.

## What we checked
- On `main`, `createStorageSession` (storage_session.go line 50) sets `now := platform.Now(ctx)` with no truncation, while service.go lines 384 to 385 truncate event timestamps to microseconds, with a comment saying this matches database precision. That matches the report: merged PR #414 fixed the rounding for event timestamps (its closing issue #408 is the same error), and the create path was not changed.
- The stale check compares `UpdateTime.UnixMicro()` values and errors when the stored time is newer (service.go lines 425 to 435). We read the code; we did not run MySQL.

## What this does not tell you
- No fix is merged for the create path. There is no released version with one that we know of.
- Whether you hit this depends on MySQL rounding and your driver DSN settings; the reporter used the default DSN. We cannot say which versions are affected beyond "current main on 2026-10-23".
- Reloading a session with `Get` before appending was described by the reporter as avoiding the error; that is their observation, not tested advice from us.

## Honest limits
- We read the issue and the cited source on `main`. Nothing was executed.
- Issue state may have changed since 09:55 UTC.
