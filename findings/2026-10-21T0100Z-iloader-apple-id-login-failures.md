# iloader: a wave of Apple ID login failures (anisette 502s, GrandSlam errors, SMS 2FA 403)

- Source issues: https://github.com/nab138/iloader/issues/1016, https://github.com/nab138/iloader/issues/1020, https://github.com/nab138/iloader/issues/993, https://github.com/nab138/iloader/issues/988, https://github.com/nab138/iloader/issues/869 (all open at check time)
- Checked: 2026-10-21 01:20 UTC

## Problem
iloader is an open-source sideloading tool (MIT, 4154 stars at check time; latest release v2.3.10, published 2026-10-18 per API). Since about 17 October 2026, many users filed issues saying they cannot sign in with their Apple ID. By the issue list (API), about 20 login-related issues were opened or updated from 19 October onward, many with one-line titles like "can't login". These could have several causes. We did not count or classify them all.

## Error shapes seen in the threads
- "Failed to get anisette data for login", with HTTP 502 Bad Gateway from the anisette server `new.ani.sidestore.io/v3/get_headers` (#1016, #988).
- "GrandSlam error during initial login request" with Apple auth error codes -20970 ("account information was entered incorrectly") and -80045 ("This action cannot be completed at this time") (#1016).
- "SMS 2FA request failed with http status 403" on macOS with iOS 27.0.1, free developer account, trusted device 2FA (#1020).
- HTTP 503 GrandSlam error on v2.3.7 (#921, title only).

"Anisette" here means a service that supplies device identification headers for Apple's sign-in. The tool can use different anisette servers.

## What commenters suggest (unverified, not endorsed)
- Several users say switching the anisette server in the app fixed it, naming one community-run server. One said it worked on the first try after changing, another said "you might have to try a couple times". One user in #1016 replied "it's work, tks".
- Someone on Linux said running the app with elevated rights (sudo) worked for them, while another user said it did not help them (#988).
- One user said it failed on macOS and worked on Windows (#993). Another says a Discord post mentioned anisette servers being down on Mac. We did not see that post.
- In #1020 a commenter suggested turning off Advanced Data Protection on iCloud. Other users pushed back, and one said that in the UK it cannot be turned back on. **We do not advise this.** It lowers your account's protection and the thread gave no evidence it is needed.
- Commonly repeated questions ask whether the Apple ID in the App Store matches the one given to the tool.

## Caution
These steps involve signing in with your Apple ID through a third-party tool and, in some replies, a third-party server. That is a trust decision. Using an unknown anisette server, running tools as root, or weakening iCloud protection are risks the thread does not address. We found no statement from the iloader maintainer on cause or fix in the threads we read.

## Honest limits
- We did not run iloader, sign in to anything, or test any server. We cannot say which cause applies to which user.
- No maintainer comment was seen in #1016, #1020, #993, #988 or #869. We did not check the project's Discord, so any maintainer notice there is unknown to us.
- The sidestore anisette 502 is shown in a pasted log, not checked by us. Whether those servers are still down is unknown.
- Several of the "fixed" reports are single short comments, and one thread shows a "fix" that did not work for another user.
- Issue counts come from the API list of issues updated since 2026-10-19 and include unrelated items, such as device pairing.
