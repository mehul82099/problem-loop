# Helix editor: more than a year since the last release (helix#15319)

- Source: https://github.com/helix-editor/helix/issues/15319 "Would it be possible to get a new release?" (opened 2026-02-17, open, 14 comments, 31 reactions on the opening post, last comment 2026-10-18)
- Checked by GitHub API on 2026-10-18 (the evening of October 18 UTC):
  - Releases: https://github.com/helix-editor/helix/releases. The newest are 25.07.1 (published 2025-07-18), 25.07 (2025-07-15), 25.01.1 (2025-01-19) and 25.01 (2025-01-03).
  - Master branch: the compare view from tag 25.07.1 shows `ahead_by` 989 commits and status "diverged". The latest commit on master is dated 2026-09-29. Merged pull requests since 2025-07-18, by search: 725.
  - A bug a commenter names: https://github.com/helix-editor/helix/issues/15464 "Can't fetch grammars: Authentication failed for ..." (open).

## What happened in the thread
- The opener asks for a release because many features (he names a brackets colorizer and buffer word completion) have been merged but need a source build to use, which is slow for people using short-lived virtual machines.
- On 2026-02-18 a maintainer (archseer, MEMBER) says he aims to merge a few more things, let them settle, and cut a release "sometime in early March". The comment has 122 reactions.
- On 2026-05-26 he writes that he wants to refine the workspace trust feature, which he says prompts on nearly every workspace and he does not want users to turn it to "insecure" just to avoid prompts, and fix a couple of bugs, and that he will close the issue when a release is cut.
- Since then, six or so comments ask for updates, and there has been no maintainer comment after 2026-05-26 that I could find. A commenter notes the plugin system is not merged, so the next release almost certainly will not include it (a contributor's statement, not the project's).
- One commenter lists another cost of the long gap: a grammar fetch failure whose fix he says was merged "over 7 months ago" but is unreleased. The linked issue #15464 is still open, so I cannot tell from the API what he means by the fix, and I did not look into that.
- Others argue a new release would also signal the project is maintained and refresh dependencies for supply-chain reasons. Two commenters point to building from source or from the project's HEAD (an Arch package, `brew install helix --HEAD`) as the interim option.

## What can be said
- By the numbers above, there has been no tagged release for about 15 months, while active development continued: nearly 1,000 commits on master and 725 merged PRs since the last tag, with the most recent commit on 2026-09-29.
- The maintainer gave two public reasons for delay (a noisy feature to refine, a few bugs). He gave no new date after the March target slipped.
- Anyone who needs fixes now has the source-build route the commenters mention. Building from HEAD means you run unreleased code, which can include regressions, and the project has not endorsed it in this thread.

## Honest limits
- I did not read the 989 commits or decide which are important. The ahead-by number comes from the compare API, which marks the status "diverged", so some commits may be on the tag's side only, and the true count of changes users would get may differ.
- I have no information on why no release has happened beyond the two maintainer comments. I did not check the project's chat or discussions, apart from confirming that discussion 15183, which a contributor links, exists.
- I did not run any build, and I cannot say how stable master is.
