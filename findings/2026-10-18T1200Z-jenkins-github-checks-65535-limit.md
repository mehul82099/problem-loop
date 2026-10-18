# Jenkins GitHub Checks plugin: publishing fails with "Only 65535 characters are allowed; 65537 were supplied" (github-checks-plugin#345)

- Source: https://github.com/jenkinsci/github-checks-plugin/issues/345 (open since 2023-06-05, 9 comments, no labels, last comment 2026-10-18)
- Code read on 2026-10-18 from the default branch (master):
  - https://github.com/jenkinsci/github-checks-plugin/blob/master/src/main/java/io/jenkins/plugins/checks/github/GitHubChecksDetails.java
  - https://github.com/jenkinsci/checks-api-plugin/blob/master/src/main/java/io/jenkins/plugins/checks/api/TruncatedString.java
  - https://github.com/jenkinsci/checks-api-plugin/blob/master/src/main/java/io/jenkins/plugins/checks/api/ChecksOutput.java

## The report
A user with a failing React Native build in Kubernetes agents says the final check is not published to GitHub, and the log shows a 422 from the GitHub API: `Only 65535 characters are allowed; 65537 were supplied` (docs link: Update a check run). He notes that 65537 is only 2 over the limit and suspects the plugin's truncation logic. His workaround is the organisation folder option "Suppress log output in checks".

On 2026-10-18 another user says he sees it often with a very large pipeline (even the list of stage names can be large), and not always by 2: a recent failure was 65546 supplied. He suggests the plugin be more conservative, or read the number from the error message and truncate by that much, and to truncate characters, not bytes, so a multi-byte character is never cut in half.

## What the code shows today
- `GitHubChecksDetails` has `MAX_MESSAGE_SIZE_TO_CHECKS_API = 65_535` and calls `checksOutput.getSummary(MAX_MESSAGE_SIZE_TO_CHECKS_API)` and `getText(...)` with it.
- Those call `TruncatedString.build(maxSize)`, which is marked `@Deprecated` and is documented to truncate to bytes (it calls the same code as `buildByBytes`). A 2023 commenter (KalleOlaviNiemitalo) pointed this out, and said the limit should be chosen by the plugin as bytes or chars. A maintainer (timja, MEMBER) replied in 2023 that a few characters of extra buffer might work around it.
- The deprecated method is still the one called in the current default branch. I did not look at release history to see when that changed or whether a buffer was ever added.

## What I could and could not work out
- I checked this with a small script: any string that is at most N bytes in UTF-8 also has at most N characters and at most N UTF-16 units. So if the plugin truncates to 65535 bytes, the text it sends should never exceed 65535 characters. That means the overage in these reports must come from something other than the text field's own length: the count may include other parts of the payload, the summary and text may be counted together, or the service may count differently (for example converting newlines to CRLF would add one character per line, which could produce small overages like 2 or 11, but that is only my guess, I have no evidence for it).
- GitHub's error message wording has changed over time: a 2021 issue linked in the thread said "summary exceeds a maximum bytesize of 65535", this one says "characters". I could not fetch GitHub's current docs page to confirm the exact unit, so I cannot say whether bytes or characters is right.
- I did not reproduce the failure, and I do not know the real cause.

## What this means for people hitting it
- The thread's only workaround is the plugin's "Suppress log output in checks" setting. Another commenter proposes retrying with a smaller cut based on the error message. That is an idea, not an existing feature.
- A maintainer's 2023 suggestion of an extra buffer would be a guess without the real cause, as the numbers in the 2026 report (11 over) show a fixed 2 or 3 character buffer might not be enough.

## Honest limits
- Not run, not reproduced, and I did not read the whole plugin, just the three files above on the default branch.
- No maintainer has commented in 2026 on the thread, so there is no plan I can report.
- The CRLF idea is my own hypothesis and not supported by anything in the thread.
