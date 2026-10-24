# Alexa Media Player fails to load: "cannot import name 'wrap' from 'aiofiles.base'" - an aiofiles version conflict, root cause already fixed upstream

- Source issue: https://github.com/alandtse/alexa_media_player/issues/3641 (open at check time; label "bug"; opened 2026-10-23 14:29 UTC; several comments)
- Root-cause issue: https://github.com/alandtse/alexa_media_player/issues/3617 (closed; "alexapy pins aiofiles<25, which breaks the import of alexa_media (and others)")
- Fix PR: https://github.com/alandtse/alexa_media_player/pull/3637 (merged; bumps alexapy to 1.33.0)
- Checked: 2026-10-24 03:10 UTC

## Problem
After updating Alexa Media Player (a HACS custom integration) to v5.18.0, Home Assistant fails to load it: the config flow dies with `ImportError: cannot import name 'wrap' from 'aiofiles.base'`, leaving the config entry in "not_loaded". The reporter is on HA 2026.10.2 with Python 3.14. Several other users confirmed.

## What the thread says
- A frequent contributor to the project explains the mechanism: it is not that aiofiles 25.1.0 removed `wrap` - the symbol moved between modules, and the real failure is a version conflict. AlexaPy (the library AMP depends on) used to pin `aiofiles<25`; Home Assistant can end up with a mixture of aiofiles 24.1.0 and 25.1.0 loaded in the same Python process, and imports then resolve against the wrong one. Their explanation, which matches the public record:
  - Issue #3617 documented that alexapy's `aiofiles<25` pin broke alexa_media's import; it is now closed.
  - PR #3637, bumping alexapy to 1.33.0 (which corrected the constraint), is merged.
  - alexapy 1.33.0 and aiofiles 25.1.0 both exist on PyPI.
- The same contributor notes that after updating, an additional Home Assistant restart may be needed so the corrected dependency set is what actually loads. One user reported rolling back to a previous AMP version as their workaround.
- A bot commenter flagged #3617 as a possible duplicate and #3637 as the related PR - consistent with the above.

## What we checked
- The issue, the closed root-cause issue, and the merged PR all exist as described.
- PyPI confirms aiofiles 25.1.0 and alexapy 1.33.0 are current releases.
- We did not verify the exact location of `wrap` across aiofiles versions or run Home Assistant; the module-move and mixed-version mechanism is the contributor's account, though it is consistent with the pin/conflict history in #3617.

## What this does not tell you
- Whether updating to the fixed alexapy resolves every case: the thread is hours old, and the mixed-version loading behavior can depend on install order. The contributor's restart advice is ordinary operational guidance, but we did not test it.
- Users on the broken state should not hand-edit installed packages; nothing in the thread requires that.

## Honest limits
- We read the issues, the PR, and PyPI metadata. Nothing was executed.
- Issue state may have changed since 03:10 UTC.
