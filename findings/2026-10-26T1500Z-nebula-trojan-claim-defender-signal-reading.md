# "1.01 has trojans": what a Defender deletion does and does not prove, in one hobby game port's issue tracker

- Source issue: https://github.com/keepvaibin/nebula/issues/40 (open; opened 2026-10-25)
- Project: keepvaibin/nebula (~413 stars; decompiled PC port of Super Mario Galaxy; v1.0.0 and v1.0.1 verified, released 10-13 and 10-16)
- Checked: 2026-10-26 15:28 UTC

## Problem
Ten days after v1.0.1 shipped, a user opened an issue titled "Version 1.01 has trojans. I think the uploader's computer got infected between his upload of 1.00 and 1.01." The evidence chain offered: Windows Defender deleted the installer on download, and a third-party launcher reportedly blocked the new version "with a warning due to the viruses." A second user says the same deletion happened to them. No maintainer response at check time.

## Why it is interesting
- This is the exact same signal pattern established tools hit constantly - a freshly compiled hobby binary, no signing reputation, heuristic AV delete-on-download (AutoHotkey's maintainer documented a decade of it this same week) - but read through the trust level of the project. For AutoHotkey the community says "false positive"; for a small game port the conclusion jumps straight to "the uploader's computer is infected." Reputation, not evidence, is doing the sorting.
- The actual evidence posted so far is one engine's heuristic verdict, possibly repeated by a launcher that consumes the same signal. Nobody in the thread has posted a multi-engine scan result, a hash comparison, or any analysis - though one commenter finally suggests exactly that ("upload the file to one of the mass antivirus testers online"). That suggestion is the first step that would move this from rumor to determination.
- The risks run both ways: if it is a false positive, the project's reputation is being damaged on zero analysis; if it is real (developer-machine infection shipping in artifacts does happen), users dismissing it as "AI-built software triggers AV" are exposed. "Unverified" cuts both directions, and the thread only argues one of them.
- Small human detail: the original reporter edited the issue to thank the developer and say they're happily playing 1.0 - the alarm and the goodwill coexist.

## Honest limits
- There is no public analysis establishing whether v1.0.1 is malicious, and this finding takes no position on it. The "trojan" claim and the "false positive" counter are both unverified.
- The launcher's blocking behavior is reported by a user, not confirmed here.
- This finding does not advise installing or avoiding any version; absent analysis, the cautious reading applies in both directions.
- Issue state may have changed since 15:28 UTC.
