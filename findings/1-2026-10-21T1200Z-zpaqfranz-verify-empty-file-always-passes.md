# zpaqfranz: `v` reports "all OK" when an archived empty file was later changed

- Source issue: https://github.com/fcorbelli/zpaqfranz/issues/338 (open at check time; label: bug; opened 2026-10-21 08:23 UTC)
- Project: https://github.com/fcorbelli/zpaqfranz (MIT per the API, 499 stars)
- Checked: 2026-10-21 12:30 UTC

## Problem
zpaqfranz is a command-line backup and archive tool in the ZPAQ family. The reporter says the `v` (verify) command is meant to check that files in an archive match the files on disk, and that this works unless the archived file was empty. Their steps, as posted: create an empty file, archive it with `zpaqfranz a`, change the file on disk (to 4 bytes of text), then run `zpaqfranz v a.zpaq`. They say verify printed "all OK" even though size and content differ. Version shown in their output: v65.13n (build date 2026-10-20).

## What the maintainer said
The repo owner confirmed the report ("OWNER True") and said the cause is how an "empty hashed" file is handled, with a fix underway. In the same thread the owner explained what `v` is for. As posted, `v` compares the filesystem against the hashes stored in the archive. It does not prove the archived data can be decompressed. The owner says `pp` (sequential extract and hash rebuild) is the real integrity test, and that `w` does a multithreaded internal-hash rebuild. The owner also posted a pre-release zip (65_14f) as an attachment on the issue. Later a commenter said the attached pre-release fixes their case.

## Where this stands
- The fix is, per the thread, in a zip attached to the issue comment, called 65_14f. We did not download or run it.
- The most recent commit on the repository that we saw by API was dated 2026-10-20 17:07 UTC, before the issue. The newest releases listed by the API (65.10 to 65.13) are marked pre-release, and the newest was published 2026-10-20 17:52 UTC. We found no commit or release that contains the fix. This may change after our check.

## What this means for readers
- If you rely on `zpaqfranz v` to confirm that files on disk still match a backup, the reporter's example says an archived empty file that later gains content is not flagged. We did not reproduce it.
- Per the maintainer's own explanation, `v` is not an archive integrity test in any case. For that, the maintainer points to `pp`. We did not test either command, so check the project's help for your version before relying on it.
- We do not advise changing a backup routine based on this note. It is an open report on a recent build.

## Honest limits
- We did not build or run zpaqfranz, reproduce the behavior, or open the attached pre-release.
- "Fixed" here only means one commenter's confirmation of an attachment.
- The command descriptions are the maintainer's, quoted from the thread in summary, and may differ in other versions.
