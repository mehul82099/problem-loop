# Jellyfin web: HLS playback freezes or times out, often fixed by turning off "Prefer fMP4-HLS"

- Source: https://github.com/jellyfin/jellyfin-web/issues/7546 (open, labels `bug` and `playback`, opened 2026-01-28, 12 comments, last activity 2026-10-17; a stale-bot warning dated 2026-09-27 says it closes in 21 days without new comments, and a new comment followed on 2026-10-16)
- Firefox bug cited in the thread, status read from the Bugzilla API on 2026-10-17: https://bugzilla.mozilla.org/show_bug.cgi?id=2026875 "Firefox 149 regression: HLS playback starts only after manual seeking" - RESOLVED, FIXED, verified for Firefox 150, marked `wontfix` for 149.
- Latest Jellyfin server release per the GitHub API: v12.2 (2026-10-05).

## What was reported
The title (by uncaney) is about 10.11.6: a file with AC3 audio, which browsers cannot decode, went through HLS remux with audio transcoding, and the browser player timed out before the first segment. Turning off the client setting "Prefer fMP4-HLS Media Container" restored playback. The report says 10.10.7 direct played the same file.

Later commenters describe a related but different symptom: playback freezing a few seconds in (Kuvwert, 10.11.7), cured by the same setting. Others (sp0ker, katerberg, Jaxx7594) see HLS errors in Chrome, Firefox and the desktop client, and sp0ker says the setting makes no difference for them. On 2026-10-16 WolfRamiO74 reported that, on 12.2, every user with the fMP4 option on has subtitle problems after seeking.

## What helped and what did not (commenters' reports)
| Item | Result |
|---|---|
| Turn off "Prefer fMP4-HLS Media Container" | fixes it for uncaney, Kuvwert, keckrich (Firefox). Not for sp0ker |
| Firefox 150 | keckrich says it fixed it. sp0ker (April 29) and katerberg (Firefox 151 beta, May 14) say it did not |
| Reverse proxy check | nyanmisaka (a Jellyfin contributor in the thread, role not verified here) says wrong proxy settings can break HLS, and suggests testing on `http://localhost:port` |

## Reading the thread
Several issues are mixed together, and the thread does not separate them:
1. A confirmed Firefox 149 bug (Mozilla bug 2026875), now fixed in Firefox 150 per Bugzilla. Theguymadmax pointed to it and keckrich confirmed.
2. Cases that continued after Firefox 150, in other browsers, or on the desktop client, with a different HLS.js error. sp0ker linked hls.js issue 7761. I checked it: it is titled "Some frames not rendered on Firefox when seeking frame by frame", a different symptom, so it is at best a loose lead.
3. The original timeout from FFmpeg probing a large file, which nobody has shown to be the same as the freezes.
4. Proxy or network setup problems, per nyanmisaka.

## Honest limits
- I did not run Jellyfin or a browser. All playback results are commenters' reports.
- I verified the Bugzilla bug's title and status. I did not verify that it is the cause for anyone besides what keckrich reports.
- The thread offers no Jellyfin-side fix. I do not know whether newer releases changed the fMP4 default.
- The stale warning means the issue may close on its own around 2026-10-18 to 2026-10-19 unless the new comment resets it. That is my reading of the bot's text.
