# Qtile does not start on Arch after python-xcffib 1.7.0 (qtile#6075)

- Source: https://github.com/qtile/qtile/issues/6075 "Qtile fails to start after upgrading python-xcffib to 1.7.0-1 on Arch Linux" (open, label status: unconfirmed, opened 2026-10-15, 9 comments when read)
- xcffib releases, read through the GitHub API on 2026-10-18:
  - https://github.com/tych0/xcffib/releases/tag/v1.7.0 (published 2025-01-12; its commit list includes "cffi api mode", pull request 169)
  - https://github.com/tych0/xcffib/releases/tag/v1.7.1 (published 2025-01-13; its commit list includes `Revert "cffi api mode"`)
  - The newest release the API lists is v1.12.0 (2025-12-14). PyPI also shows 1.12.0 as the current version.
- Arch Linux package data, read from archlinux.org on 2026-10-18: `python-xcffib` in the `extra` repository is 1.7.0-1, last updated 2026-10-15; `qtile` is 0.37.1-1; `python-cairocffi` is 1.7.1-2. The packaging repository's log shows "upgpkg: 1.7.0-1" on 2026-10-15 and before that 1.6.2-1 on 2026-06-24.

## The symptom
After the Arch update on 2026-10-15, Qtile 0.37.1 fails to start. A commenter's traceback ends in `cairocffi/ffi.py` with `TypeError: ffi.include() expects an argument that is also of type cffi.FFI, not 'FFI'`. The reporter and others say downgrading `python-xcffib` from 1.7.0-1 to 1.6.2-1 restores Qtile with no other change.

## What was said (attributed)
- tych0 (marked MEMBER) wrote that it is a known problem with that xcffib version, which is quite old, and that 1.7.1 or any newer major release should fix it. He later asked the Arch package maintainer, felixonmars, whether the package could move to 1.7.1 or newer. As of my reading the issue shows no reply from that account.
- jrwrigh (CONTRIBUTOR) asked why a rolling-release distribution upgraded to a version that old, when 1.12 existed. He has no answer, and I have none.
- A user who got "target not found" from `pacman -S python-xcffib=1.6.2-1` was told by another commenter (smsjr) to install the `downgrade` tool from the AUR, pick 1.6.2, and accept the offer to add `IgnorePkg = python-xcffib` to pacman.conf.

## What I could check
- The xcffib release notes match tych0's statement in outline: version 1.7.0 added a change titled "cffi api mode", and version 1.7.1 the next day reverted it. The traceback is a mismatch between two cffi objects. I cannot say from this that the "cffi api mode" change is the cause. That is my inference from the titles, not something the maintainers wrote.
- Arch's current `python-xcffib` was 1.7.0-1 when I looked, so the problem should still be present for anyone who updates to it. I did not test it.

## For someone affected (general package practice, not from the thread)
A downgrade to 1.6.2-1 is the workaround people report. Using the downgrade tool or the pacman cache, and pinning the package with `IgnorePkg`, is a normal way to do that. Remember to remove the pin when Arch ships a fixed version, or the package will not update. I did not test these steps.

## Honest limits
- I did not run Arch, Qtile or xcffib.
- I read two release pages and the commit titles in them, not the code.
- I do not know whether Arch has since changed the package. Check the package page before acting.
