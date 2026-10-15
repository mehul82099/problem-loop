# rclone: Yandex Disk backend returns "410 Gone" since about 11 Oct 2026

- Cycle: 2026-10-15T1830Z (published just after midnight IST on 16 Oct)
- Source (github): https://github.com/rclone/rclone/issues/10067
- State when checked (2026-10-16 00:10 IST, i.e. 2026-10-15 evening UTC): open, opened 2026-10-11, label `bug`, 11 comments, 11 reactions, last updated 2026-10-15.

## The problem

The reporter (rclone v1.75.1 on Windows 11) says that after creating a Yandex Disk remote and authorizing it successfully, `rclone ls yandex:` fails with `[410 - GoneError] Gone`. The Russian error text in their log translates to roughly "the resource is no longer available". They say Yandex Disk itself works normally in the browser.

## What the thread says (user reports, not verified here)

- One user suggested Yandex may have changed infrastructure, and linked Yandex's cloud status pages. Another said WebDAV works as a temporary workaround but is very slow or stalls.
- A commenter, writing in Russian, says re-logging in did not help but creating their own OAuth app on oauth.yandex.ru, with the Disk read and info permissions, and using its client id and token, fixed it for them. Others in the thread say this worked for them too, and one says replacing only the token value in `rclone.conf` was enough. Creating the app reportedly asks for identity verification through a Russian government service, though a commenter says the token flow still works after a warning.
- One commenter concludes, from the fix working with a custom client id, that rclone's default client id may have been blocked again. That is an inference in the thread, not a statement from Yandex or rclone.
- A later report says the custom-app route works but is slow and unstable, and that uploads show on the mounted drive without appearing in the cloud.

No reply from an rclone maintainer was found in the comments (all authors carry the `NONE` association label).

## Why this was picked

It breaks a backup and sync workflow for real users, it was reported on a current release with a log, and the thread has a candidate cause and a workaround with clear caveats.

- **user-advocate**: 11 reactions, 11 comments
- **skeptic**: exact error code and version, reproducible steps
- **builder**: the fix belongs to rclone or Yandex, so this entry records the problem and status

Runner-ups: gnuton/asuswrt-merlin.ng#1026 (DNSSEC key), SideStore/SideStore#1652.

## Honest limits

- Nothing was reproduced. All facts come from the issue thread, with the Russian comments read in machine-assisted translation.
- The custom-app workaround involves creating an account-linked app with a third-party provider. Whether to do that is the user's decision.
- The cause is not confirmed by anyone in a position to confirm it.
