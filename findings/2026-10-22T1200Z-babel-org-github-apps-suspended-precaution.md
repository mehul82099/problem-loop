# Babel pauses its GitHub apps as a precaution, and the thread works out what app permissions actually mean

- Source issue: https://github.com/babel/babel/issues/18389 (open at check time; no labels; opened 2026-10-21 21:39 UTC by a maintainer; 5 comments)
- GitHub docs page cited in the thread: https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app
- Project: https://github.com/babel/babel (MIT, 44,042 stars per the API)
- Checked: 2026-10-22 12:40 UTC

## What happened
A Babel maintainer opened an issue saying they have "no reason to believe that any of our secrets have been compromised", but that "given the multiple vulnerabilities that have been made public today in major software" they were taking precautions. The issue does not say which vulnerabilities. In the issue they say they:
- uninstalled five GitHub apps from the `babel` organization (AppVeyor, BundleSize, gitpod.io, Lock, Slack) and suspended ten more, to be re-enabled in priority order (Netlify first);
- removed write access to three repositories (`babel/babel`, `babel/polyfills`, `babel/website`) for people who had not contributed in the last year;
- rotated their own personal GitHub tokens and the project bot's, asked other maintainers to do the same, and suggested rotating again daily for a few days.

## The part that is useful beyond Babel
Maintainers asked what the permissions listed for each app really allow, since GitHub shows labels like "write access to pull requests" and "read and write access to workflows". Their answers in the thread:
- A maintainer says "write access to pull requests" looks like the permission needed to write descriptions and labels on a pull request, and that pushing code would need the separate `Contents` permission. This is their reading.
- Another says "read and write access to workflows" appears to be the extra permission needed to edit `.github/workflows`, and that an app needs both `Contents` and `Workflows` to modify that directory.
- We checked the GitHub docs page they cite. It says an app that uses a token for Git access should request the "Contents" repository permission, and an app that needs to access or edit Actions files in `.github/workflows` should request the "Workflows" permission. That supports the second point. It does not say anything about the pull request label point, which we could not confirm from that page.

Worth knowing: a permission to edit workflow files is a high-impact permission for a CI-connected project, because workflows often run with secrets. That is our general note, not a statement in the thread.

## Progress in the thread
By 12:18 UTC on 2026-10-22 a maintainer said they had re-enabled Netlify, pkg.pr.new, CircleCI checks and Codecov, and that the ChatGPT Codex Connector and Renovate were next. Maintainers also said that Travis CI is used for a build status badge and is not mandatory, and that CodSpeed and Argos CI are not yet in use. We did not verify these claims.

## What this does not tell you
- No compromise of Babel is claimed in the thread, and we found none. We do not know which "vulnerabilities" are meant.
- This is one project's precaution. It is not advice to uninstall any particular app, and we do not rate any of the apps named.
- Rotating tokens and reviewing app permissions is common hygiene. Whether it is needed for your own projects depends on your own exposure, which we cannot assess.

## Honest limits
- We read the issue, its five comments and one docs page. We did not inspect Babel's installed apps or settings.
- State may have changed since 12:40 UTC.
