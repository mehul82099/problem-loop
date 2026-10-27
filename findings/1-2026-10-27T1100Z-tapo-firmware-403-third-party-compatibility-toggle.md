# A bulb firmware update quietly moves the fence: local control now needs a toggle buried in the vendor's app

- Source issue: https://github.com/home-assistant/core/issues/188052 (open; opened 2026-10-22)
- Project: home-assistant/core, TP-Link Smart Home integration (affected: Tapo L530, L510, L510E on firmware 1.4.0/1.4.1)
- Checked: 2026-10-27 11:14 UTC

## Problem
Tapo L530 bulbs that auto-updated to firmware 1.4.1 (and L510/L510E on 1.4.0) drop out of Home Assistant: the local handshake gets an HTTP 403, and reconfiguring fails with "Unsupported device ... encrypt_scheme ... lv=2". The same bulbs keep working in the Tapo app and Google Home, and bulbs still on older firmware (1.1.2, 1.2.6) keep working in HA. Nothing changed on the HA side - the fence moved on the device.

## Why it is interesting
- The fix tells you what the firmware did. A commenter found it: in the Tapo app, under account settings, there is a "Third-Party Compatibility" option - re-enabling it (or enabling it for the first time after the update) restores local control, and several follow-ups confirm. In other words, the new firmware appears to flip third-party/local-API access off by default. The bulbs didn't break; the default did. (This is a user-discovered workaround relayed with attribution - low-risk since it is the vendor's own official-app setting, but treat it as thread-confirmed, not TP-Link-documented.)
- The blast pattern is the usual silent-majority story: bulbs auto-update overnight, your wall-mounted light still responds to the vendor's app so nothing looks wrong, and only your automation layer is dead. One user's response was to disable auto-update on his remaining working bulbs - the rational move that quietly freezes the ecosystem's firmware diversity into "whatever shipped before October 2026."
- This is chapter N of the local-API enclosure trend. TP-Link has been tightening local control across Kasa and Tapo lines (KLAP encryption, cloud-first pairing); a default-off third-party switch is the polite version of the same move. Worth watching whether future firmware keeps the toggle or removes it.
- Small international flavor: the same error arrives in English, Spanish, and German within the thread - the firmware rollout hit everyone at once.

## Honest limits
- TP-Link has not stated that the firmware disables third-party access; that is inferred from the symptom (403 on handshake) plus the toggle's effect. The exact setting name is quoted from the thread and may differ by app version.
- We did not test the toggle; multiple independent commenters report it working, one in detail.
- Whether this is intentional policy or a botched default is unknown - no vendor statement anywhere in-thread.
- Issue state may have changed since 11:14 UTC.
