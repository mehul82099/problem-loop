# Immich: metadata edits on a read-only external library fail without telling you (immich-app/immich#10538)

- Source issue: https://github.com/immich-app/immich/issues/10538 "Read-only external library metadata edits silently fail". Opened 2024-06-22, open, labels "server" and "external-library". 28 reactions on the post, 30 comments, last updated 2026-10-19.
- Docs, read 2026-10-20: https://docs.immich.app/features/libraries . Its volume example says the `ro` flag gives read-only access, which "will disallow the images from being deleted in the web UI, or adding metadata to the library (XMP sidecars)".

## The problem
If an external library is mounted read-only, and you edit an asset's date (or location) in the web UI, the change does not stick. The reporter (Immich server v1.106.3, 2024) saw the date in the info pane not change and two warnings in the server log, which show Immich failing to create a `.xmp` sidecar file next to the photo. The reporter's suggested fix was a popup saying the file system is read-only and the edit was not saved.

## What the thread says
- Several users hit the same thing, some after hours of confusion. One said it went away after loosening folder permissions.
- A project member (2024-09-02) said that tags are also written to the XMP sidecar and replaced on the next metadata extraction. Another member explained that date and location are overwritten by extraction from the file because an asset can have only one of each. Users reported tags that appear and then vanish a few seconds later. Another member said in 2024-12 that re-running metadata extraction would silently overwrite a value in the database that was never written to an XMP file.
- Asked whether sidecars could be written somewhere else, a member answered (2024-09-28) that they are sidecar files, and storing them away from the media "doesn't really make sense". A 2026-10-19 comment from a contributor argues for a configurable separate writable folder, as Immich already uses separate folders for thumbnails and transcodes. Many users, with 12 to 19 reactions each, say metadata for read-only assets should go in the database instead.
- 2025-02: a user shared an overlay file system mount as a workaround, so Immich sees a writable view of the library and sidecars land in a separate folder. A later user reported a side effect where rescans did not see added or removed photos until a restart. Both are user reports, not tested by me, and they change how storage is mounted, so check your own setup first.
- A 2026-04 comment says the success popup is misleading, because the change failed but the UI says it worked and the update is "not in a transaction". A 2026-05 comment says the API returned 204 though nothing was saved, and the failure shows only at WARN level in the log.
- 2025-11-09: a Immich member added a struck-through note that this "is no longer relevant with the new implementation" and asked for a new issue if it persists. The issue was not closed, and the 2026 comments above say the behavior still occurs. A 2026-01-30 comment says tags now stay on a read-only library in a newer version, and a reply says tags were always in the database, so I cannot tell whether anything changed. I did not test a current version.

## What can be said
- By the docs and the comments through October 2026, a read-only external library means no XMP sidecars, and so edits that depend on them are lost on the next extraction. The open question in the thread is whether Immich should warn, store edits in the database, or write sidecars elsewhere, and a project member's position (sidecars next to the file) has not changed in what I read.
- This is a limit of how the library is set up, not data loss in the original photos. This note does not say which setup to use.

## Honest limits
- I did not run Immich or reproduce the failure. The log lines are from the original report.
- I did not check what the newest Immich version does, and the "new implementation" the member mentions is not described.
- I read the first and last parts of the thread closely and skimmed the middle.
