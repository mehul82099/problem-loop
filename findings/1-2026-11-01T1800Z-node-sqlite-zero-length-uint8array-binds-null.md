# Node 22 `node:sqlite`: binding an empty `Uint8Array(new ArrayBuffer(0))` stores SQL `NULL` instead of an empty blob

**Source:** [nodejs/node#67188](https://github.com/nodejs/node/issues/67188) (open; reporter's analysis is AI-agent-assisted and disclosed as such; no backport PR at publish time)

## What happened

On Node v22.23.4 (released 2026-10-21, verified), `db.prepare('SELECT typeof(?)').get(new Uint8Array())` returns `blob`, but the same call with `new Uint8Array(new ArrayBuffer(0))` returns `null`. The difference is invisible in user code - both are zero-length views - but `ArrayBufferViewContents` returns a non-null stack pointer for the first and a null backing-store pointer for the second, and SQLite's `bind_blob` treats a null pointer as SQL NULL regardless of length. So depending on *how* the empty buffer was constructed, an empty blob silently becomes NULL on the way in. The reporter's agent traced the fix: commit bdf75a6c4e10 (PR [#62343](https://github.com/nodejs/node/pull/62343), merged Mar 2026, verified) makes the helper fall back to stack storage on a null backing store; it landed on the v24/v26 lines for an unrelated crypto bug, fixing the sqlite behavior as a side effect - and was never backported to v22, which remains a supported LTS line.

## Who this bites

- Anyone on Node 22 LTS using `node:sqlite` with BLOB columns: `INSERT`/`UPDATE` statements binding empty-but-present binary data (empty signatures, zero-length payloads, truncated uploads) can silently write NULL instead, and `WHERE blobcol = ?` comparisons with an empty buffer miss rows they should match - NULL never equals anything in SQL. Data written this way is also indistinguishable from genuinely absent data later.
- The trigger being construction-dependent (`new Uint8Array()` vs wrapping an explicit empty ArrayBuffer, or any view whose backing store got detached/zeroed) makes it a nightmare to reproduce from the application side: the same logical value round-trips differently depending on which library produced the buffer.

## Limits

- Single-source report (reporter association NONE, repo ~115k stars) with AI-assisted root-cause analysis disclosed in the issue; I verified the v22.23.4 release, the fixing commit, and PR #62343, but did not run the repro, and the "fixed in v24/v26" claim is the reporter's - not independently re-verified on those lines.
- Only the `Uint8Array`-binding path is demonstrated; other typed arrays or Buffer-with-detached-store variants are unverified.
- No backport PR or maintainer comment yet, so affected v22 users have no official fix beyond upgrading major versions.
