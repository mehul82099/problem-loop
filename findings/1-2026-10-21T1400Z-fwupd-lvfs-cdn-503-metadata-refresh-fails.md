# fwupd / LVFS: `fwupdmgr refresh` fails because the metadata CDN returns 503

- Source issue: https://github.com/fwupd/fwupd/issues/11234 (open at check time; no labels; opened 2026-10-21 11:21 UTC; 10 comments)
- Earlier, possibly related report (a different symptom, a metadata checksum mismatch on 2026-09-24): https://github.com/fwupd/fwupd/issues/11050 (open)
- Checked: 2026-10-21 14:30 UTC

## Problem
fwupd is the Linux firmware update daemon (LGPL-2.1, 4203 stars per the API). The reporter says `fwupdmgr refresh --force` and KDE Discover fail on 21 October 2026 with `Transient failure to download, server response was 503 ... Error 54113 ... Varnish cache server`. Their curl table, taken about 11:00 UTC: on `cdn.fwupd.org`, the signature file `firmware.xml.zst.jcat` times out after 30 s while the metadata file `firmware.xml.zst` returns 200; the same two files served directly from `fwupd.org` both returned 200. They were served from the Fastly Vienna point of presence. A second commenter reports the versioned metadata file also fails on the CDN with a 503 and that the CDN copy of `firmware.xml.zst` is older than the origin copy. A third says Frankfurt shows it too, and a fourth says the fwupd.org home page looks broken for them.

## What the project said
- A project member (11:40 UTC) said they were debugging it and saw no requests from Fastly on the origin at all.
- At 12:28 UTC a member said, from Cloudflare logs, that it appeared to have started about 04:15 local time for them (later said down since about 04:30), and that they had filed a ticket with the Linux Foundation team that runs the infrastructure.
- At 13:21 UTC a member explained that the website and the metadata use Fastly, while popular firmware uses explicit Cloudflare R2 redirects. They said the Fastly side "seems to be down" and that the origin backend request "is maybe looping", adding they have no Fastly login to check. That is a guess from the member, not a confirmed cause.
- A commenter warned against pointing clients straight at the origin with `fwupdmgr modify-remote`, because it would add load to the origin, and the reporter then removed that suggestion from the issue. This note does not advise it either.

## Our own check
At about 14:26 UTC we sent a header request for `https://cdn.fwupd.org/downloads/firmware.xml.zst.jcat` with a 20 second limit and got no response. The same file from `https://fwupd.org/downloads/firmware.xml.zst.jcat` returned 200 in about 0.1 s. This is one probe from one network at one moment. It agrees with the reports and does not tell us where the fault is or whether it affects every region.

## What this does not tell you
- No one has stated a root cause or an expected fix time. The issue was still open at check time.
- It says nothing about the safety of firmware or the signing of metadata. The failure is a download problem: a client cannot fetch the signature file.
- It is not advice to change your fwupd remote configuration or to skip signature checks. Waiting for the service to recover is the lowest-risk option the thread supports.

## Honest limits
- We did not run `fwupdmgr`. Command output and numbers are the commenters', apart from our single probe.
- Dates and times are as posted; the member's local time zone was not given.
- The state of the service may have changed since 14:30 UTC.
