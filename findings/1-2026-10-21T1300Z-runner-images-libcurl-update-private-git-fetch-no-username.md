# GitHub runner images: private repo fetch fails with "could not read Username" after a libcurl security update

- Source issue: https://github.com/actions/runner-images/issues/15014 (open at check time; labels: bug report, needs triage, Area: Git, OS: Ubuntu; opened 2026-10-21 08:55 UTC; 5 comments)
- Related report in another project: https://github.com/renovatebot/renovate/discussions/47071 (closed; opened 2026-10-15)
- Checked: 2026-10-21 13:30 UTC

## Problem
The reporter says jobs on the `ubuntu-24.04` runner image `20261018.339.1` fail to fetch a private GitHub repository over HTTPS when the token is injected with a git `url.<base>.insteadOf` rule of the form `https://<token>@github.com/` (token as username, no password). The log shows `warning: redirecting to https://github.com/<org>/<repo>/` followed by `fatal: could not read Username ... terminal prompts disabled`. The same job passes on the older image `20261012.334.1`. Their table: 0 of 4 runs passed on the newer image, 5 of 5 on the older one, and both images were in rotation, so one job could pass and then fail minutes later. The git version (2.55.0) is the same on both. The curl package differs (`8.5.0-2ubuntu10.15` versus `8.5.0-2ubuntu10.16`).

Two other commenters say they see the same, one of them on an Azure DevOps Microsoft-hosted agent with `ubuntu-latest`. Another says many workflows are affected and asks whether a fix and an automatic runner update are planned. At check time we saw no reply to that question.

## What a project contributor said
A contributor reply (10:55 UTC) says the team reproduced it, that it affects Ubuntu 22.04, 24.04 and 26.04 (x64 and arm) and `ubuntu-slim`, and that it only occurs on images with the newer libcurl security update. They describe it as an upstream libcurl behavior change: after GitHub redirects the `.git` URL to `.git/`, curl no longer re-sends credentials when the URL has a username and an empty password. They say a new image is rolling out, which explains pass and fail on the same job, and they suggest a form that uses a non-empty username with the token as the password (`x-access-token:<token>`). They say that worked on every image where the original form failed.

## Cross-check
The Renovate discussion above describes the same symptom from another direction. A self-hosted Renovate version stopped cloning private repositories with a personal access token after its base image picked up the same `8.5.0-2ubuntu10.16` libcurl. A Renovate member there confirmed the same cause and the `x-access-token:` form, and said a fix was on the way (PR #47073). A commenter reported it fixed in a later release. That thread is the evidence that this is not specific to GitHub's runner images. We did not compare the two diagnoses beyond reading them.

## What this does not tell you
- It does not say when GitHub will update the runner images or whether the problem will clear on its own. The thread had no answer to that.
- We did not check Ubuntu's security notices or the libcurl change. The libcurl explanation is the contributors' statement.
- Putting a token in a git URL stores it in git config and can show it in logs. If you change how you pass a token, review how it is stored and masked. This note does not recommend a specific change for your setup.

## Honest limits
- We did not run any workflow, reproduce the failure, or test the suggested URL form.
- Counts in the table are the reporter's.
- The issue was open and untriaged at check time, so details may have changed.
