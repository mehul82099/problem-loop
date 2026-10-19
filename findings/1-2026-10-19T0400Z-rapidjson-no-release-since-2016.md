# RapidJSON: no official release since 2016 (Tencent/rapidjson#2321)

- Source: https://github.com/Tencent/rapidjson/issues/2321 "No new official release since 2016". Opened 2024-11-18, open, 17 comments, 39 reactions on the post, last comment 2026-10-19.
- Checked by GitHub API on 2026-10-19:
  - Releases: https://github.com/Tencent/rapidjson/releases. The newest is v1.1.0, published 2016-08-25. Before it: v1.0.2 (2015-05-14) and v1.0.1 (2015-04-25).
  - Master is 763 commits ahead of v1.1.0 (compare API, status "ahead").
  - The latest commit on master is "Fix out of bounds read with kParseValidateEncodingFlag", dated 2025-02-05. A commits query for the 12 months before 2026-10-19 returned no commits.
  - Open pull requests: 118 (the last page of a one-per-page listing). The repo's counter shows 804 open issues, but that number includes PRs. Stars: 15,143. The repo is not archived.
  - Related open issues linked in the thread: https://github.com/Tencent/rapidjson/issues/2284 "New version release" and https://github.com/Tencent/rapidjson/issues/2202 "Release version 1.2.0".

## What the opener asked
A user of a vulnerability scanner (Snyk) says it can track only official releases, and the last one is over 8 years old. He asks what the release process is and whether a release can be cut at a specific 2021 commit. I checked that commit (fd3dc29) is a merge of pull request #1944 from November 2021.

## What the thread says
- Many comments ask for a release. Reasons given: Linux distributions package from release tags, so v1.1.0 is what they ship, and a commenter says v1.1.0 fails to build with GCC 14 and Clang 19 while a fix exists on master. I did not build it. The commit he names (3b2441b) is a 2016 commit "Removed non-compiling assignment operator. Fixed #718" and I cannot tell from that whether it is the fix he means for GCC 14.
- Another commenter says master's CMake interface differs a lot from 1.1.0 while both report the same version number, so CMake projects cannot tell them apart.
- A commenter asks why a project from a big company has 100 pull requests, 600 open issues and few recent commits. Another says no one is moderating the repo. These are opinions.
- Some users say they moved to other libraries (nlohmann/json, yyjson) and one proposes an "official fork". One commenter replies that nlohmann/json is slower. Nothing came of the fork idea in the thread.
- No comment from the project's owner or any member of the project's organization appears in the thread (all 17 comments are marked NONE or CONTRIBUTOR by the API).

## What can be said
- By the API, the project has had no tagged release for over ten years and no commit for about twenty months, with a large queue of open PRs. Whether it is abandoned is not something the project has said.
- For anyone who depends on it: distribution packages follow the 2016 tag, and master has diverged by 763 commits, so "RapidJSON 1.1.0" can mean quite different code depending on source. Pin an exact commit if you depend on master, and check your scanner's data source.

## Honest limits
- I did not build either version or test with any compiler. Compiler problems are from commenters.
- I did not read all 763 commits, and I do not know which matter.
- I do not know the maintainers' plans, and I cannot tell whether anyone has private contact with them.
