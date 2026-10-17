# vrc-get: how a project is relicensing from MIT to MPL-2.0 by asking each contributor (vrc-get#3230)

- Source: https://github.com/vrc-get/vrc-get/issues/3230 "Change project license from MIT to MPL-2.0" (open, opened 2026-10-17 by anatawa12, marked MEMBER; 20 comments when read, last edit of the issue text 2026-10-17 14:54 UTC)
- Project: https://github.com/vrc-get/vrc-get, a command line and graphical client for the VRChat Package Manager. The GitHub API still shows its license as MIT on 2026-10-18, and the `LICENSE` file's last commit it lists is dated 2023-01-19. So the change had not been applied to the repository when I looked.

This is a procedure worth reading if you maintain an open source project and are thinking about changing licenses. I did not review any legal text.

## What the maintainer proposes
- Change the project licence from MIT to the Mozilla Public License 2.0.
- He says MIT-licensed code could technically stay in the project next to MPL code if the MIT notices are kept, but he wants to avoid maintaining both notices, so he asks contributors with non-trivial contributions for permission to relicense.
- Releases published before the change, and the commits in them, stay under MIT and remain available under it.
- Each contributor is asked to comment with a fixed sentence confirming they have the right to relicense their contributions and consent to MPL-2.0. The permission covers their contributions to this project and "does not transfer copyright ownership".
- If someone cannot be reached or does not agree, he says he will rewrite the affected code where feasible. If rewriting is not practical, that code stays under MIT with its original notice retained next to the MPL-2.0 text.
- The issue includes a table built from the Git history as of commit 89a99aef, listing each author's commits and lines changed and a status of Approved, Awaiting, or Not Affected. Bots and trivial or legacy changes are marked Not Affected.

## Where it stood when I read it
I counted rows of that table in the issue text (a person can have several rows): 23 rows Approved, 5 rows Awaiting, 21 rows Not Affected. The Awaiting rows belong to three people: @lonelyicer (three rows), @yelandiealma and @xaeky. In the table, @lonelyicer's three rows add up to about 14,000 changed lines, which is much more than the other two. The 20 comments are all consent comments from 20 different accounts. I saw no objection or question in the comments.

## What this shows and does not show
- It shows one concrete way to relicense: publish the contributor list with sizes of contribution, collect an explicit consent comment from each, and keep a fallback for people who do not respond.
- It does not tell us why the maintainer chose MPL-2.0. The issue does not give a reason beyond simplifying the notices, and I did not look for one elsewhere.
- It does not tell us whether the Awaiting contributors will respond, or what happens to the code if they do not.
- Whether the stated fallback is enough from a legal point of view is something I did not assess and this is not legal advice.

## Honest limits
- The counts come from the issue's own table at the time I fetched it. It is edited by hand or by a script as comments arrive, and may be out of date by the time you read it. I did not check each consent comment against the table.
- I did not check that the commenters' accounts match the commit authors.
- I did not read the project's contributing guide or any discussion outside this issue.
