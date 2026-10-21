# PcapPlusPlus: use-after-free in `GtpV1Layer::addExtension` when the layer is attached to a Packet

- Source issue: https://github.com/seladb/PcapPlusPlus/issues/2322 (open at check time; label: bug; opened 2026-10-21 02:23 UTC)
- Fix pull request (open, not merged): https://github.com/seladb/PcapPlusPlus/pull/2323 (base branch `dev`, opened 2026-10-21 06:35 UTC)
- Checked: 2026-10-21 10:25 UTC

## Problem
PcapPlusPlus (Unlicense, 3158 stars; latest release v26.07 published 2026-07-23 per API) is a C++ library for parsing and building network packets. The reporter says that when a GTPv1 layer belongs to a `Packet` that already has one GTP extension, `GtpV1Layer::addExtension` keeps a pointer into the packet buffer, then grows the layer, which can reallocate and free that buffer, and then writes through the old pointer. They report a heap use-after-free caught by AddressSanitizer (a read in `getTotalLength()` and a write in `setNextHeaderType()`), with a control capture that does not trigger it, and attached a reproducer package.

Versions in their table: master at commit 43e9eeeb (reproduced with ASan), plus `dev` and v26.07 where they say the vulnerable code is present by reading it. They state exploitability has not been assessed, and that an application has to call `addExtension()` on a parsed message for it to matter.

## Relation to an older fix
The report says it is a residual variant of issue #1711 ("Segmentation fault (Heap use after free) in GtpV1Layer.addExtension()", closed). We checked by API: #1711 is closed, and PR #1749 ("Fix segmentation fault in `GtpV1Layer.addExtension()`") was merged on 2025-04-03. The reporter's reading is that #1749 refreshed two header pointers but not the saved last-extension object, and that the new case is in the other branch (a layer that already has an extension, attached to a Packet). They also list other related but different reports. We did not read the code, so we do not confirm that analysis.

## What the project and reporter did
- The repo owner thanked the reporter at 06:03 UTC and asked if they would open a fix PR. The reporter replied that they would, with a plan: do not use the extension object across the second `extendLayer()` call, re-walk the extensions after reallocation, and add a regression test for a Packet-attached message with an existing extension.
- PR #2323 ("Fix GTPv1 addExtension use-after-free after packet buffer reallocation") was opened about 30 minutes later against `dev`. At check time it had no comments or reviews and was not merged.
- Three more PRs (#2324 to #2326) were opened by the same stream of work for other parser and serializer issues (ICMPv4 router advertisement read, PcapNG packet block over-read, a DNS generic RDATA stack overflow), matching open issues #2319 to #2321. We only checked that those PRs and issues exist and are open; we did not review their content.
- The owner encouraged more PRs for the other issues.

## What this does not tell you
- It is not a statement about whether released software built on PcapPlusPlus is exploitable. No exploit is claimed in the thread.
- A fix is not available in a release. The PR was unreviewed when we checked. If you use `addExtension()` on Packet-attached GTPv1 layers, watch the PR and the next release.

## Honest limits
- We did not build or run PcapPlusPlus, run the reproducer, or inspect the attached files. The ASan result and the code analysis are the reporter's.
- The fix in #2323 was not reviewed by us. We cannot say it is correct.
- We did not check whether other projects that bundle PcapPlusPlus are affected.
