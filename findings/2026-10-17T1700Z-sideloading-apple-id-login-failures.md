# iloader and SideStore: Apple ID sign-in failing since October 14 (503, 403, -80045, -22411)

- Sources:
  - https://github.com/SideStore/SideStore/issues/1652 "Apple ID login fails with error 80045" (open, opened 2026-10-14, about 30 comments when read)
  - https://github.com/nab138/iloader/issues/932 "Apple ID log in failed 403" (open, opened 2026-10-15, 10 comments)
- Related, state checked through the GitHub API on 2026-10-17:
  - https://github.com/nab138/iloader/issues/920 and https://github.com/nab138/iloader/issues/921 (open, 503 login errors, opened 2026-10-14)
  - https://github.com/nab138/iloader/issues/928 (open, -80045 on iloader 2.3.8)
  - https://github.com/SideStore/SideSign/pull/5 "Fix 2FA failing" (merged 2026-10-13)
- Latest iloader release shown by the API when I read: v2.3.9 (published 2026-10-16). Reporters in these threads mostly used 2.3.7 or 2.3.8. SideStore's latest non-prerelease is 0.7.0-alpha (2026-09-15); a rolling "nightly" prerelease also exists.

These are tools that install apps on iPhones using a user's own Apple ID. This finding is only about the sign-in failure, not about what anyone installs.

## The symptom
Starting about 2026-10-14, users report that signing in with an Apple ID fails in both tools, with different errors depending on the setup:
- HTTP 503 from Apple's sign-in service (iloader #920 and #921).
- HTTP 403 when completing the SMS two-factor step (iloader #932, which quotes `isideload-0.4.6` in the error trace).
- Error -80045 (SideStore #1652, iloader #928).
- Error -22411 after the 2FA step starts.
Reporters are on Windows and macOS, with iOS 18 to 27.

## What commenters said (attributed, mostly untested by me)
- A commenter (kisnner26) wrote that since about 20:50 UTC on 2026-10-14 Apple's sign-in server answers 503 when the tool presents an Android "Pixel 7" device identity, which was the usual setting. He said a Windows identity from an anisette server works instead. He later separated the failures: 503 means the identity was rejected, -80045 means the sign-in itself was rejected and may depend on account or IP, and -22411 means the identity was accepted but 2FA handling in the app is missing. He wrote that he has not tested SideStore himself and corrected himself that the account/IP dependency is only his reading.
- The same commenter pointed to SideSign pull request #5 (merged 2026-10-13) as a 2FA fix present in nightly SideStore builds but not in the September alpha. I confirmed the PR exists and is merged. I did not check which builds contain it. One of his links labelled as a SideStore issue (#921) actually points to a closed 2025 issue about slow installs, so that link is wrong; the matching report is iloader #921.
- One commenter said installing through iloader's "Import IPA" worked for him. Others in the same thread said it did not work for them.
- A commenter (ppcharbo) posted a long multi-step procedure with a VPN app and a device pairing tool, and several people replied it worked for them, while others said it failed or that parts did not apply to their device or OS. Another commenter pointed people to an unofficial SideStore fork. I do not relay any of these steps and have not vetted the fork or the tools.
- In iloader #932 a user says a different Apple ID worked at first and then failed again. Another said an Apple device signed in to the same Apple ID must be available to receive the 2FA code.
- No maintainer (GitHub marks every commenter in both threads as having no association with the repos, as far as I checked for #932) has posted a diagnosis in the comments I read.

## What this does and does not show
- It shows many independent reports of sign-in failures starting at the same time, which fits a change on Apple's side. That is a reading of the pattern, not something anyone in the threads has confirmed.
- It does not show a single cause. Several different error codes are mixed together, and the thread says so.
- Some commenters warn that retrying many times may trigger rate limits. That is also unconfirmed.

## Honest limits
- I did not sign in with any Apple ID, run either tool, or test any identity, server or workaround.
- I read the opening posts and the first part of each comment. Later comments may add facts.
- Third-party servers, forks and VPN setups are unvetted. If you use any of them, you decide what to trust with your Apple ID.
