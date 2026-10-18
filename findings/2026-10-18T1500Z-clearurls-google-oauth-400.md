# ClearURLs and Google sign-in: "400, The server cannot process the request because it is malformed" (ClearURLs/Addon#535)

- Source: https://github.com/ClearURLs/Addon/issues/535 (open since 2026-09-02, 6 comments, no labels, last comment 2026-10-18)
- Checked on 2026-10-18 by API and by reading data:
  - Repo state: https://github.com/ClearURLs/Addon (default branch master, last push 2025-07-27, not archived; latest release 1.27.3 published 2025-02-05: https://github.com/ClearURLs/Addon/releases/latest)
  - Rules repo: https://github.com/ClearURLs/Rules (last push 2026-03-25; I downloaded https://raw.githubusercontent.com/ClearURLs/Rules/master/data.min.json and inspected the `google` provider)

## The report
The reporter says that for some weeks he has gotten a Google "400 ... malformed" error when signing in on various sites, and disabling the ClearURLs browser extension fixes it. A second report on 2026-10-10 is more detailed: signing in to Claude.ai with "Continue with Google" fails with the same 400 on Firefox, on three computers that share a Firefox Sync account. His table of tests shows: fails with all extensions on, fails with only ClearURLs on, passes with everything except ClearURLs, passes in a fresh Firefox profile without extensions, passes in Chrome and Edge. He says he does not know which URL parameter is the cause and calls his own guess (stripped `state`, `code`, `redirect_uri` or PKCE parameters) a hypothesis. He did not record the Firefox or extension versions. Other people say "happened to me too".

## What commenters say is the cause and the fix (unverified)
- A commenter says ClearURLs is removing the query parameters `as`, `client_id` and `flowName`, which makes Google reject the request, and that turning off the setting "Prevent tracking injection over history API" and then saving and reloading fixes it. Two later commenters repeat the problem without confirming the fix. I could not test it.
- The latest comment asks whether the extension can be disabled per website, like Privacy Badger. I did not check whether it has such a setting.

## What I could verify in the rules data
- The `google` provider in the rules file has a URL pattern that matches any Google domain, 38 removal rules and 11 exceptions. Its rule list does not contain `as`, `client_id` or `flowName` (I searched every provider's rules for those names, and the only match is an `as` rule for support.mozilla.org).
- The exceptions include `^https?://accounts.google...` (any `docs` or `accounts` Google domain), `^https?://accounts.google.com/o/oauth2/` and `^https?://accounts.google.com/signin/oauth/`. So on the current published rules, ordinary rule matching does not obviously strip those parameters on Google's account pages. That fits a commenter's suggestion that the cause is the history-API setting and not a rule, but I did not test it and it does not prove it.
- The rules repo was last changed on 2026-03-25 (a rule for another site), months before these reports began, so a recent rule change does not explain when the problem started. The extension fetches rules from the project's servers, and I did not check whether what it downloads matches this repository.
- Nothing here says why the failure started in late summer. One possibility is a change on Google's or the sites' side, but that is a guess.

## What this means
If you use ClearURLs in Firefox and see Google sign-in 400 errors, the thread's evidence points at the extension, and the one fix people give is turning off a history-API option, which is a trade-off since that option exists to stop tracking parameters being added on page navigation. Whether it helps in your case is not established. Check the extension settings yourself, and consider disabling the extension for the sign-in as the reporter did.

## Honest limits
- Nothing was reproduced. I did not install ClearURLs, run Firefox, or sign in anywhere.
- Maintainers have not replied, and the add-on's last code push is more than a year old, so a fix may not come from the project.
- The rule analysis covers only the public rules file on the date above.
