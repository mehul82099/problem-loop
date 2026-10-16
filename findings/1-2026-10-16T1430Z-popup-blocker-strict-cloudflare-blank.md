# "Popup Blocker (strict)" extension: Cloudflare verification pages stay blank

- Cycle: 2026-10-16T1430Z
- Source: https://github.com/schomery/popup-blocker/issues/184
- State when checked: open, opened 2026-10-15, no labels, 7 comments, last activity 2026-10-16 13:01 UTC. No maintainer reply, and the repo's releases list is empty on GitHub's API.

## The problem

The reporter says that since a few hours before they wrote, Cloudflare verification ("are you human") pages show as plain white with no text when the extension is on, and work when it is turned off. Others confirm it: one says it affects every site with the Cloudflare check, and one names romhacking.net.

## Clues in the thread (user reports, not tested here)

- One user is on Firefox and could not reproduce it with a fresh Firefox profile that had only the extension (strict build) installed. Disabling the extension in their normal profile fixed the site. Re-enabling it did not break pages already loaded, until Firefox restarted. They suggest it could involve something server side at Cloudflare.
- The same user says the browser console shows a Content-Security-Policy block on an inline script (`script-src-elem`).
- Resetting the extension's settings did not help that user.

## Workaround in the thread, with mixed results

One user says to add `cloudflare.com` and `challenges.cloudflare.com` to three lists in the extension's options ("Do not block popups of these origins", "Do not block any popup on these pages", "Allow page redirection to the following origins"). A second user says this works. A third says it did not fix romhacking.net, and someone replies to try turning the extension off for that site.

Note: the comment that first posted this workaround spells the second domain `challenges.clouadflare.com`, with a typo. The user who confirmed it may have fixed it silently, so type the domains yourself and check the spelling.

## Why this was picked

A blank verification page looks like a Cloudflare outage or a browser problem. Here the extension is the common factor, and the thread has a workaround that people disagree on, including a typo that would make it fail.

## Honest limits

- Nothing was run. I did not install the extension or test Cloudflare.
- The cause is unknown. The CSP console message is one user's observation, and the failure to reproduce on a fresh profile suggests more variables.
- The extension has several store builds, and the thread does not say which version each person uses, so the scope is unclear.
