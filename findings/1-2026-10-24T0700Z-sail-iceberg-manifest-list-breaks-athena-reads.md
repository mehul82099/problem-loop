# Sail writes Iceberg manifest lists that AWS Athena cannot read - a one-name Avro mismatch, acknowledged by maintainers

- Source issue: https://github.com/lakehq/sail/issues/2851 (open at check time; opened 2026-10-24 05:00 UTC)
- Project: https://github.com/lakehq/sail (Apache-2.0, about 3.5k stars)
- Checked: 2026-10-24 07:10 UTC

## Problem
The reporter has an Iceberg table created by Spark on EMR. Athena reads it fine - until Sail writes to it. After a single INSERT via Sail, Athena can no longer read the table at all (`GENERIC_INTERNAL_ERROR`), while Spark and Sail itself still can. Their test matrix is clean: every engine can write and read its own output; only Athena-after-Sail fails.

## Root cause (per the reporter's analysis)
The Avro record name in Sail's manifest-list partition summaries: Iceberg's Java implementation names the partition-summary record `r508`; Sail writes the identical structure (same field ids and types) but names the record `field_summary`. Athena's Iceberg reader looks Avro records up by name, doesn't recognize `field_summary`, and throws. Spark tolerates the mismatch, which is why only Athena breaks. This is the reporter's analysis - we did not inspect Sail's source (GitHub code search was not available to us) - but a maintainer responded within 30 minutes thanking them for the report and treating it as a real interoperability issue, which lends it weight.

## What the thread says
- Maintainer linhr acknowledged the issue and invited a PR, noting bigger changes would be handled by the team.
- Team member lonless9 (named as the Iceberg expert) expects the fix to be scoped and plans follow-up refactoring to prevent similar issues.
- No fix is merged at check time.

## What we checked
- The issue and the maintainer responses exist as described.
- The record-name mechanism is the reporter's claim, consistent with the maintainer's quick acceptance but not independently verified by us.
- The reporter's read/write matrix is their testing, not ours.

## What this does not tell you
- Which Sail versions are affected, and whether other engines beyond Athena (e.g. Trino proper, Snowflake, BigQuery readers) are similarly strict about record names.
- Workaround: none is offered in the thread; the practical note is only that tables written by Sail may become unreadable to Athena until the fix lands - relevant if you mix engines on shared Iceberg tables. Do not attempt manifest surgery; nothing in the thread suggests that.

## Honest limits
- We read the issue and its comments. Nothing was executed.
- Issue state may have changed since 07:10 UTC.
