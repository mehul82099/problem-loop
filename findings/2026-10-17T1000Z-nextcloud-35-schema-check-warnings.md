# Nextcloud 35: "The database schema does not match what is expected" after upgrade

- Source: https://github.com/nextcloud/server/issues/64505 (open, labels include `bug`, `high`, `feature: database`, `35-feedback`; opened 2026-09-17; 69 comments; 22 reactions; last activity 2026-10-17)
- Releases per the GitHub API on 2026-10-17: v35.0.2 and v34.0.5 (both 2026-10-15)
- Related items, state checked through the API: nextcloud/server PR 64696 "silence reports from db:add-missing-indices" (closed); nextcloud/spreed PR 19539 "Correctly check for Index rather than Constraint" (merged); nextcloud/polls issue 5091, a separate and unverified report titled "After upgrading Nextcloud from 34.0.5 to 35.0.2 database corrupt" (open).

## What users see
After updating to Nextcloud 35, `occ upgrade` finishes with "Update successful" and then prints a warning: the database schema does not match what is expected, followed by lists of missing or unexpected tables, indexes and columns. `occ db:schema:check -v` shows the full list. Reporters use PostgreSQL 15 to 18, MariaDB 11.8 and MySQL 8, in Docker, distro packages and manual installs, both from the web updater and from a manual unzip. The output differs per instance.

## What a Nextcloud contributor said (Antreesy, author of the check by his own statement; maintainer status not verified here)
- It is an information-level check, a combination of the existing `db:schema:export` and `db:schema:expected` commands. Most differences already existed before the upgrade and went unnoticed because the command did not exist on 34.x.
- "Unexpected" tables usually mean an app that was installed once and removed. Whether to keep that data is the admin's decision. He later struck out an earlier claim that `occ app:remove` drops tables, and wrote that none of the apps drop tables on removal.
- `missing table 'oc_federated_invites'` is a false positive: a migration creates it and a post-migration drops it.
- `differs in: comment` is likely carry-over from before about Nextcloud 18. Several other kinds (a missing `activity_object` index, some `differs in: default`, `differs in: type`) are false positives he was preparing fixes for.
- `oc_share_external: column 'id' differs in: autoincrement` is a "known bug" in a files_sharing migration file (confirmed to exist at that path through the API).
- In his 2026-09-27 summary, three options: ignore it if things work, help find false positives with per-case detail instead of pasting full output, or change your own database after researching which app owns each table.

## What helped one user (dfrei25, MariaDB, distro packages; their report, not tested here)
They backed up the database first, ran `occ db:add-missing-indices`, and found that missing `oc_systemtag` columns came from a disabled systemtags app whose migrations had not run. The comment recommends the backup before any change.

## Reading the thread
Most of the warnings look like a new report on old differences, plus a few real false positives that are being fixed. Nobody in the thread shows data loss from these warnings. One user (BolkoSchreiber, Docker image, Postgres 18) said Nextcloud still needed a database upgrade and would not start, and tried creating a missing table by hand. That is a different state from the warning, and I did not see it resolved. Another user asked how to correct the warnings, and the thread gave no single procedure.

## Honest limits
- I ran no upgrade and no `occ` commands. All output and results are reporters' or the contributor's, and the guidance here only repeats what they said.
- I did not verify the contributor's claims about which items are false positives beyond checking that the cited PRs exist and their states.
- This finding does not advise dropping tables. Whether a given table is safe to drop depends on the instance and is, as the contributor said, the admin's call, after a backup.
- The polls report is a separate open issue that I only confirmed exists.
