# Gnuton's Asuswrt-Merlin routers lose DNS after the DNSSEC root key change (KSK-2024)

- Cycle: 2026-10-15T1930Z (published after midnight IST on 16 Oct)
- Source (github): https://github.com/gnuton/asuswrt-merlin.ng/issues/1026
- State when checked (2026-10-15 evening UTC): open, opened 2026-10-12, label `bug`, 6 comments, 7 reactions, last updated 2026-10-15.
- Cross-check: IANA's root trust anchor file, https://data.iana.org/root-anchors/root-anchors.xml, lists key tag 20326 (valid from 2017) and key tag 38696 (valid from 2024-07-18).

## The problem

The reporter says that on 11 October the DNS root zone switched to a new DNSSEC key, KSK-2024 (key tag 38696), and the older KSK-2017 stopped signing the root zone. After that, DNSSEC stopped working on their router. Commenters on Asus routers running Gnuton firmware (for example `3004.388.11_1-gnuton1` and `3006.102.6_1-gnuton1`) say every lookup through the router's `dnsmasq` returns SERVFAIL while DNSSEC validation is on, because the firmware only ships the old anchor (20326). One commenter says the router's startup log shows a trust anchor for key tag 20326 only, and that `dig +dnssec DNSKEY .` shows the root key set signed only by 38696 from 2026-10-11. A user of a GT-BE98 says devices behind their router have been unable to reach the internet for days.

I checked that IANA's published file does list key tag 38696 with a digest that matches the one used in the thread's workaround. I did not check anything on a router.

## Workarounds named in the thread (user reports, not tested here)

- Turn DNSSEC support off in the router's WAN settings. A commenter confirms lookups work that way, and one user asks if doing so temporarily is safe. It does remove DNSSEC validation, so it is a trade-off, not a free fix.
- Add the new root trust anchor to dnsmasq through the router's custom config (the thread gives the exact lines, and a note that JFFS custom scripts must be enabled for the file to be read). Several users confirm it restored DNS. Anyone doing this should copy the digest from IANA's file, not from a comment.

## What the thread says about a fix

A commenter who read the source (and says they did not run the firmware) writes that current builds ship only the old anchor, and that upstream Asuswrt-Merlin has commits adding the new key for its 3006 and 3004.388 branches. No reply from the Gnuton fork's maintainer is visible in the comments, and all authors carry the `NONE` association label. A commenter asks how long an official fix will take.

## Why this was picked

A real outage for non-technical users, a root cause tied to a public dated event, and key facts that can be checked against IANA. The thread has 7 reactions and users without internet for days.

## Honest limits

- Router behavior was not reproduced. It comes from user reports in the thread.
- The source-code claims in the thread were not checked.
- Disabling DNSSEC or editing router config is the owner's decision. Check the firmware project for an official release.
