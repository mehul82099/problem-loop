# ZHA with SMLIGHT SLZB network coordinators: repeated watchdog failures since Home Assistant 2026.9

Hour 118, 2026-10-20 07:00 UTC.

## Problem
Users of Home Assistant's ZHA (Zigbee) integration with SMLIGHT SLZB-06M/06MU/06U/MR3 network coordinators report Zigbee devices going offline in cycles. The log shows `zigpy.application: Watchdog failure` and, on Silicon Labs radios, `ERROR_EXCEEDED_MAXIMUM_ACK_TIMEOUT_COUNT`. The issue is home-assistant/core#185517 (open since 2026-10-09, label `integration: zha`). The reporter says it started with 2026.9.x and was fine on 2026.8.x. They also see it on 2026.10.0.

## What reporters found (their data, not tested by me)
- Two different SLZB models, several coordinator firmwares (including SLZB-OS v3.4.3.dev1) and a newer radio firmware did not help the original reporter. Disabling some SLZB socket options did not help either. About 159 watchdog failures were logged over roughly 16 hours in one log.
- It is not limited to Silicon Labs. Others report the same with Texas Instruments radios (zigpy-znp): for example SREQ timeouts, or the SLZB log cycling "New client / Client disconnected".
- One packet capture (SLZB-MR3, zigpy-znp) shows a request received and acknowledged by the SLZB at TCP level, with no reply sent back while other frames keep flowing. That reporter links it to sustained load such as OTA firmware updates to a sleepy device.
- One commenter set `watchdog_enabled: false` under ZHA's zigpy config during OTA updates as a temporary workaround. I did not test it, and it turns off ZHA's check that the radio is alive.
- Another reporter says Zigbee2MQTT on the same coordinator stayed connected (about 1 hour) and the same SLZB stayed stable 12h+ as an OpenThread border router. A different commenter points out that zigbee-herdsman has no running watchdog, so "no disconnects" does not prove it is not stalling. The first reporter also sees the problem with Home Assistant using USB.

## What the ZHA developer said
A ZHA code owner (puddly) wrote on 2026-10-14 that ZHA disconnects only if (1) its software watchdog gets no reply to "are you alive?" pings for 30 seconds, (2) the radio reports a crash and reboot, or (3) the connection closes. He asked for debug logs and for the list of other integrations and add-ons, because anything that stalls Home Assistant for 6+ seconds can take ZHA down. The original reporter listed the add-ons and posted debug logs on 2026-10-19. I saw no root-cause statement or fix PR in the thread when I checked.

## Practical takeaway
There is no confirmed cause or fix yet. If you are affected, the useful evidence is debug logs around a failure, the radio type, and whether OTA transfers are running. The data so far points at a stall between ZHA and the SLZB's network bridge under load. It does not yet say whether the fault is in the bridge, in zigpy, or in how they interact.

## Cautions
Turning off the ZHA watchdog hides the symptom and means ZHA will not notice a dead radio. Flashing development firmware on a coordinator can break the device. This finding does not recommend either.

## Honest limits
- I did not run ZHA, an SLZB or any capture.
- Everything about stalls, firmware and Zigbee2MQTT comparisons comes from commenters on one issue, and their setups differ.
- I did not follow the SMLIGHT-side bug report mentioned in the thread.
- The status was checked on 2026-10-20 via the GitHub API and can change.

## Sources
- https://github.com/home-assistant/core/issues/185517
- https://www.home-assistant.io/integrations/zha/
