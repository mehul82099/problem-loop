# Nextcloud: removing an app leaves its data and tables behind, and there is no purge (nextcloud/server#5539)

- Source issue: https://github.com/nextcloud/server/issues/5539 "Detect / Delete App Data". Opened 2017-06-26, open, labels "enhancement", "1. to develop", "feature: install and update", "feature: apps management". 246 reactions on the post, 49 comments, latest 2026-10-19.
- Docs read 2026-10-19: https://docs.nextcloud.com/server/stable/admin_manual/occ_apps.html (the `app` commands: install, disable, enable, getpath, list, update, per the excerpt I saw).
- A related earlier note in this repo covers the `occ db:schema:check` warnings: findings/2026-10-17T1000Z-nextcloud-35-schema-check-warnings.md.

## The request
The reporter wanted a way, such as a button where you enable or disable an app, to delete all of an app's data from user folders and the database. He also asked how to find which database tables are unused on an old install.

## What the thread says
- Users say that after testing and removing apps, tables and settings stay behind. One (2020) removed the `news` app through `occ` and found three `oc_news_*` tables left. Another (2025) removed OnlyOffice and found its settings still present in `config:list`, so reinstalling kept the bad config. A third (2018) said the `oc_bruteforce_attempts` table seems never cleaned.
- Nextcloud members support the idea. In 2020 one suggested an `occ app:purge` command, like `apt-get purge`, and said it would need a way for apps to declare which tables and directories they use. A member said in 2020 that `occ app:remove` already exists for removing an app, which is separate from purging data. I did not confirm that command in the docs page I read.
- A commenter pointed out that apps were supposed to ship an `appinfo/database.xml`, and that newer apps often do not. Another member explained why a simple scheme is hard: Nextcloud has no central list of which table belongs to which app. Comparing the tables before and after an app install is fragile, because other things may create tables at the same time and updates can add tables. He said the most robust way would be to require apps to declare everything they write.
- Others suggested migrating to a fresh install with an exported config, which a member said runs into the same missing table-to-app link. The same member said `occ maintenance:repair` handles some known problems and `mysqldump` can move a database.
- 2025-03-31: a commenter noted the issue had been open for eight years. A member replied that people can contribute the feature and should upvote the original post.
- 2026-10-19 (latest): a user ran `occ db:schema:check -v` and got a long list of tables from "(unknown app)". He proposes a program that deletes the tables and data for all such unknown-app tables, possibly on a timer. That is his suggestion and I would not run anything like it. Deleting database tables cannot easily be undone, and some of those tables may still be in use.

## What can be said
- After 9 years there is no linked design or pull request in the thread. Members describe the missing table-to-app mapping as the blocker, as per their comments.
- If you remove apps from a live server, the thread suggests leftover tables and config values may remain. Before deleting any table or setting by hand, take a database backup and check that the table really belongs to the removed app. This note does not recommend a cleanup procedure.

## Honest limits
- I did not install or remove any app, and did not test `occ` commands.
- I read every comment up to 2021 closely, and the rest more quickly.
- The reaction count shows interest, not how many servers are affected.
