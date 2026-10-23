# bootc composefs: the Type 1 kernel path on the ESP is too long for HP G10 laptop firmware, and boot hangs

- Source issue: https://github.com/bootc-dev/bootc/issues/2585 (open at check time; no labels; opened 2026-10-22 00:38 UTC; 8 comments)
- Downstream report it cites: https://github.com/projectbluefin/dakota/issues/1648 ("System isn't bootable on some HP laptops", open)
- Related composefs-rs issue a commenter links: https://github.com/composefs/composefs-rs/issues/159 (open; titled "Mitigate generics")
- Code read at commit 298b404b: https://github.com/bootc-dev/bootc/blob/298b404b1d02aecbdefe3abf54079dfa7d6b5eaf/crates/lib/src/bootc_composefs/boot.rs (`get_type1_dir_name` at lines 552 to 554)
- Project: https://github.com/bootc-dev/bootc (about 2.3k stars per the API)
- Checked: 2026-10-23 11:55 UTC

## Problem
The reporter says that on several HP G10 business laptops (EliteBook 845 G10, EliteBook 840 G10, ZBook Firefly 14 G10 A), the firmware hangs - black screen, hard lock - when systemd-boot loads the kernel from the Type 1 directory the composefs backend writes to the EFI system partition. Stock installs produce a path like `/EFI/Linux/bootc_composefs-<128 hex characters>/vmlinuz`, 163 characters. Reporters downstream hand-truncated the directory name to bisect: 160 characters boots, 163 hangs, with kernel, initrd and arguments unchanged.

## What the thread says
- A commenter linked composefs-rs#159 and suggested the verity hash could be configurable (sha256 instead of sha512) to shorten the name.
- A bootc maintainer replied that a Base32-style encoding would be simpler, or that the entry need not be named after its digest at all, while noting rollback compatibility concerns. No decision was stated.
- The maintainer's automation posted a triage comment (marked as bot-generated) that traced the 163 characters to the code and cited `get_type1_dir_name`. The maintainer then publicly told the bot to slow down and hide outdated comments. We treat the bot's analysis as unverified assistance, and we checked its central claim ourselves: at the cited commit, `get_type1_dir_name` returns the Type 1 prefix plus the deployment verity string, so the directory name does embed the full 128-hex digest. We did not check whether anything else reads identity back out of that name.

## What this does not tell you
- The 160/163 boundary is a hand-bisect by downstream reporters on specific HP firmware. Other machines and firmware versions may differ; there is no maintainer confirmation of the exact limit.
- No fix is merged or released, and the approach (encoding, shorter hash, or not using the digest) is undecided.
- Renaming ESP directories by hand was a diagnostic done by the downstream reporters, not a safe workaround: it desynchronizes the entry from what bootc wrote and can break future updates. We do not recommend it.

## Honest limits
- We read the issue, the cited source file at the named commit, and the linked issues. We have no HP G10 hardware and ran nothing.
- Issue state may have changed since 11:55 UTC.
