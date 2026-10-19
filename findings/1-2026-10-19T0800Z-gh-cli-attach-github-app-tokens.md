# gh --attach and GitHub App tokens: the upload endpoint rejects them (cli/cli#14309)

- Source: https://github.com/cli/cli/issues/14309 "`--attach` cannot work for GitHub App installation tokens - the upload endpoint 404s them even with write access". Opened 2026-09-01, open, 28 comments, 116 reactions on the post, labels blocked, enhancement, platform, attachments. Last comment 2026-10-19.
- Related, checked by API on 2026-10-19: https://github.com/cli/cli/issues/14186 (the `--attach` work, closed), https://github.com/cli/cli/issues/14302 (`--attach` needs write access so outside reporters can't attach, open), https://github.com/github/roadmap/issues/1324 (roadmap item for CLI image upload, open), https://github.com/cli/cli/issues/14194 (file attachments request, open).
- Latest `gh` release at the time: v2.102.0.

## What was reported
The new `--attach` option in `gh` uploads images and files to issues and pull requests. It only accepts OAuth tokens, classic personal access tokens and fine-grained tokens, and it refuses GitHub App installation tokens (`ghs_` prefix) with "unsupported authentication type". The reporter tested whether that is just the CLI being cautious. He says that calling the upload endpoint on uploads.github.com directly from a GitHub Actions run, with the workflow token and write permission on a private repo, returned 404, while the same request with an OAuth token on the same repo succeeded. If that is right, the limit is in GitHub's endpoint and not in the CLI. This is his test and I did not repeat it.

## What the project said
- A bot triaged it as a legitimate enhancement or documentation request.
- On 2026-09-02 a cli team member (BagToad) says: "This is intended behavior for now, but we may re-evaluate in the future based on demand." A standard bot comment then says the request is in the backlog with no commitment, and to add a thumbs up to help prioritization.
- There has been no further comment from a team member in the thread that I saw.

## What users said
- About two dozen comments agree, many just "+1". The reasons given: bots and agents produce screenshots and visual diffs for pull requests, security policy at some companies bans long-lived personal tokens for automation (one commenter's claim about his own company), and installation tokens are the recommended automation identity. These are the commenters' own statements.
- Workarounds users describe, which I did not test and do not recommend: pushing images to a separate assets branch and linking the raw files, a third-party tool that uses a web session token from a dedicated bot account, and a third-party service that hosts the file and posts a normal comment. The session-token approach in particular relies on a web login, so check GitHub's terms and your security rules before considering anything like it.

## What can be said
- By the maintainers' one reply, the limit is deliberate for now and demand is the stated reason it might change. By the reporter's test, it would need a change on GitHub's side, not only in the CLI. The issue is labeled "blocked", which fits that, but I do not know what it is blocked on.
- If you want it, the stated route is a thumbs up on the issue, not more "+1" comments.

## Honest limits
- I did not run `gh --attach` or call the upload endpoint, so the 404 behavior is the reporter's claim.
- I did not check the workaround tools or their terms.
- I do not know GitHub's internal plans. The roadmap issue linked does not, per the reporter, mention token types, and I did not read it in full.
