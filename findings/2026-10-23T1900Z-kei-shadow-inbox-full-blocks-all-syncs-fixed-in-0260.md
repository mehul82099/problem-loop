# kei: a full "shadow inbox" blocked every sync after the 0.25.3 upgrade; fixed in 0.26.0

- Source issue: https://github.com/rhoopr/kei/issues/1024 (open at check time; labels "bug", "user-reported", "follow-up"; opened 2026-10-21 19:16 UTC; 5 comments)
- Fix release: https://github.com/rhoopr/kei/releases/tag/v0.26.0 (published 2026-10-23 17:30 UTC), with an upgrade guide at https://github.com/rhoopr/kei/blob/main/docs/v0.26.0-upgrade.md
- Affected version per the reporter: v0.25.3 (released 2026-10-16)
- Project: https://github.com/rhoopr/kei (MIT, about 159 stars per the API; cloud photo/video backup tool)
- Checked: 2026-10-23 19:50 UTC

## Problem
The reporter says that since upgrading to 0.25.3, no sync succeeded: after about 3.7 days of hourly one-shot runs, every run exited with "Provider shadow inbox is full; retaining observations and the current checkpoint. No automatic pruning is permitted." Their read-only inspection of a copy of the state database showed 1,186 unresolved asset-identity rows for one library, all pointing at a shared-library zone, and the same first request cursor replayed in all 58 captured cycles - so each run re-stored the same pages until the 512 MiB shadow inbox filled and blocked sync entirely.

## What the thread says
- Two automated bot reviews (clearly marked as GitHub Actions) assessed the report as plausible but unverified, citing the dedup-on-raw-body capture path. We treat those as tooling output, not maintainer analysis.
- The maintainer replied within hours that a fix was in progress, then released v0.26.0 the next day, saying it includes the fix for repeated responses filling the storage limit and that it combines qualifying copies already saved by previous runs. They ask users to follow the upgrade guide and run their normal sync with existing state - no reset or database cleanup needed.
- The reporter had not yet confirmed the fix when we checked.

## What we checked
- v0.26.0 exists and was published 2026-10-23; the linked upgrade guide exists on `main`. v0.25.3 exists, released 2026-10-16, matching the reporter's timeline.
- We did not read the fix diff or run the tool, so "fixed" here means "the maintainer released a version they say fixes it", with user confirmation still pending.
- The database contents and cycle counts are the reporter's own measurements.

## What this does not tell you
- Whether 0.26.0 fully resolves it is unconfirmed by the reporter at check time.
- Other causes of "shadow inbox full" may exist; this covers the repeated-replay case only.
- If you are mid-failure on 0.25.3, the maintainer's stated path is upgrade plus normal sync - that is their instruction, and it is consistent with the release existing, but we cannot vouch for the outcome.

## Honest limits
- We read the issue, release listings, and checked the guide exists. Nothing was executed.
- Issue state may have changed since 19:50 UTC.
