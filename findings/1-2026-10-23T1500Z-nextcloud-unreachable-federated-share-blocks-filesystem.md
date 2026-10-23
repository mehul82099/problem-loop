# Nextcloud: one unreachable federated-share remote can make the whole Files app unusable for that user

- Source issue: https://github.com/nextcloud/server/issues/65766 (open at check time; labels "bug", "0. Needs triage", "team: Files"; opened 2026-10-21 19:23 UTC; 4 comments)
- Code read on `master`: https://github.com/nextcloud/server/blob/master/apps/files_sharing/lib/External/Storage.php (discovery call at line 95 in our read)
- Project: https://github.com/nextcloud/server (AGPL-3.0); recent releases per the API: v35.0.2 and v34.0.5, both 2026-10-15
- Checked: 2026-10-23 15:50 UTC

## Problem
The reporter says that when a user has accepted a federated share from a remote server that does not respond (connections time out rather than being refused), the web Files app never loads for that user: every filesystem setup runs `files_sharing\External\Storage::__construct()`, which calls `OCMDiscoveryService::discover()` synchronously and blocks until the 10-second cURL connect timeout. A failed discovery is not cached and the share is not marked unavailable, so every request waits again. Their example: `occ user:info` took 20.6 s for the affected user versus under 1 s for others.

## What the thread says
- A second user confirmed on 34.0.5.1 (AIO) and found it is not only Files: WebDAV PROPFIND, calendar REPORT, notify_push and the recommendations API all slowed, each request logging a discovery cache failure and then a cURL error 28 after 10001 ms. Their log reading, not ours.
- A third user reports the same on 34.0.3 and 34.0.5 with PostgreSQL and Redis.
- One commenter posted raw SQL to list external shares and set `accepted = 0` as a temporary workaround. We are not repeating the statements: hand-running UPDATEs against the Nextcloud database can corrupt share state, and this is exactly the kind of unvetted fix to avoid. If you are affected, talk to your admin and consider disabling the share through the UI or `occ` instead.

## What we checked
- On `master`, `Storage.php` does call `$discoveryService->discover(...)` in the constructor (line 95), matching the report's mechanism. We did not trace whether failures are cached anywhere else; that part is the reporter's account.
- The reported versions (34.0.x) are current release lines; v34.0.5 and v35.0.2 both shipped 2026-10-15.
- The issue is labeled "0. Needs triage"; no maintainer had responded when we checked.

## What this does not tell you
- No fix exists or is scheduled that we know of.
- We cannot say how many users or versions are affected; three reporters on 34.0.x is what the thread shows.
- Whether the 10-second timeout is configurable in a way that mitigates this is untested here.

## Honest limits
- We read the issue and the cited source on `master`. We ran no Nextcloud server.
- Issue state may have changed since 15:50 UTC.
