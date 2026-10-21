# Badger 1.8.0 (Pangolin's Traefik plugin): "plugin integrity check failed", the third time

- Source issue: https://github.com/fosrl/badger/issues/38 (open at check time; opened 2026-10-21 15:36 UTC; 4 comments)
- Upstream report: https://github.com/traefik/traefik/issues/14115 (open; opened 2026-10-21 16:08 UTC; 0 comments at check time)
- Earlier cases: https://github.com/fosrl/badger/issues/31 (closed, v1.6.0 and v1.6.1 in August) and https://github.com/traefik/traefik/issues/13771 (closed 2026-08-27 with an explanation)
- Project: https://github.com/fosrl/badger (MIT, 167 stars per the API); latest release v1.8.0 published 2026-10-21 13:56 UTC
- Checked: 2026-10-21 21:35 UTC

## Problem
Badger is a Traefik middleware plugin used with Pangolin. A user says that after changing the Badger version in `traefik_config.yml` from 1.7.0 to 1.8.0 (Pangolin 1.24.0, Traefik 3.7.16), Traefik logs `Plugins are disabled because an error has occurred ... unable to check archive integrity of the plugin github.com/fosrl/badger: plugin integrity check failed`, and resources become unreachable. They say going back to 1.7.0 fixes it. The Traefik report by the Badger team shows the same log and adds that routers using the plugin then fail with `invalid middleware "badger@http" configuration`.

A second user says 1.8.0 with Pangolin 1.25.0 worked on one machine and then failed on another two minutes later. They later wrote that the working machine was in fact still on 1.7.0. We treat their report as unclear.

## Why it looks familiar
In August, Badger 1.6.0 and 1.6.1 failed the same check. A Badger member first guessed it was caused by an older tag, then re-released as 1.6.1, which did not help, and the team reached out to Traefik. On 2026-08-27 a Traefik member explained in traefik#13771 that the catalog stores a SHA-256 of the archive the first time a plugin version is downloaded, and Traefik compares it with the hash of the archive it downloads. For badger 1.6.0, 1.6.1 and 1.7.0 the stored value did not match the archive the catalog served (same content, different compression). They said the problem was on Traefik's side, corrected the stored hashes, and the three versions installed again. The thread also contains comments from owners of other plugins reporting the same error message.

## What the project said this time
A Badger member said on 2026-10-21 that they "will notify Traefik", later said they are not sure what causes it, linked the new Traefik issue, and recommended staying on 1.7.0 for now. The Traefik issue says, based on the August outcome, that the likely fix is for someone at Traefik to correct the stored hashes. That is the Badger team's reading, not a statement from Traefik. We saw no reply from Traefik at check time, and the issue had no comments.

## What this does not tell you
- It does not establish the cause for 1.8.0. The similarity to August is the Badger team's inference.
- It does not say the 1.8.0 archive is bad or tampered with. The integrity check is there to catch altered archives, so a failure should be taken seriously until the project says what it is. In August the explanation was a mismatch in the catalog's stored value.
- This note does not recommend switching off or working around the integrity check. One comment in the August Traefik thread mentions setting a hash in plugin config. We did not evaluate that and do not suggest it.

## Honest limits
- We did not run Traefik, Pangolin or Badger, and did not download the plugin archive or compute hashes.
- Versions and logs are the users' and the project's. We confirmed that the cited issues exist and checked their states and dates by API.
- The state of the Traefik catalog may have changed since 21:35 UTC.
