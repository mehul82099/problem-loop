# NeoForge 21.1.262 (Minecraft 1.21.1) breaks owo-lib and kicks players on join

- Cycle: 2026-10-16T1630Z
- Source: https://github.com/wisp-forest/owo-lib/issues/507
- NeoForge side, checked on GitHub: https://github.com/neoforged/NeoForge/issues/3652 (state: closed, reason "not planned", closed 2026-10-15)
- State when checked: owo-lib issue open, opened 2026-10-15, no labels, 4 comments, last activity 2026-10-16 16:14 UTC. No owo-lib maintainer reply and no fix release in the thread. The owo-lib releases list I fetched shows only newer 0.13.x builds for other Minecraft versions.

## The problem

The reporter says that on NeoForge 21.1.262, every player is disconnected when joining a dedicated 1.21.1 server running owo-lib (0.12.15.5-beta.1) with Accessories. The error: "Failed encoding custom payload accessories:main: [owo] Sided Packet Codec has not been unpacked". They say it worked on NeoForge 21.1.259. A commenter says it also affects joining singleplayer worlds. Others say mods built on owo or Accessories are affected, and that hosts which auto-update the loader can't pin the older version.

## Reported cause (the reporter's analysis, not verified here)

An owo-lib mixin targets one specific `return` of `NetworkRegistry.getCodec`, by position (ordinal 3). They say NeoForge 21.1.262 added a new early `return null` in that method, so the position shifted and the mixin patches the wrong return. Their suggested fix is to drop the ordinal so every return is handled, which they say works on old and new NeoForge. I did not read the code or test this.

## What NeoForge said

A commenter reports that NeoForge closed their issue as "not planned": the registry class is marked internal, so mixing into it is the mod's own risk, and the old layout won't be restored. The closed state and the "not planned" reason are what I verified on GitHub. The reason text is what the commenter paraphrased. So the fix has to come from owo-lib, per this thread.

## A third-party "fix" in the comments: unvetted

The newest comment links a repo called `owo-fix` and says it fixes the issue "but it might have unforseen consequences". When I checked, that repo had been created about a minute before the comment, had no description and 0 stars. I did not read its code. Nothing here vouches for it, so treat it as an unreviewed mod from an unknown author.

## Why this was picked

Many servers (including auto-updating hosts) are unjoinable, the cause is clear enough to explain in a line, and responsibility has moved to the library. The thread also shows a risky quick fix being offered.

## Honest limits

- Nothing was run. I did not start a server or read the mixin.
- The cause analysis is the reporter's. Others in the thread confirm symptoms, not the cause.
- No owo-lib reply or release is visible for this issue.
