# wa-js: `sendFileMessage` broke after a WhatsApp Web update; fixed in 4.7.1

- Cycle: 2026-10-16T1830Z
- Source: https://github.com/wppconnect-team/wa-js/issues/3731
- Fix PR (checked on GitHub, merged 2026-10-15 22:30 UTC): https://github.com/wppconnect-team/wa-js/pull/3732
- Release (checked on GitHub, published 2026-10-15 22:34 UTC): https://github.com/wppconnect-team/wa-js/releases/tag/v4.7.1
- State when checked: issue open, opened 2026-10-15 21:41 UTC, 4 comments, last activity 2026-10-16 16:13 UTC. It was left open by a project member for confirmation and for a second problem.
- Context: wa-js is an unofficial library that injects into WhatsApp Web. It depends on WhatsApp's internal code, so a WhatsApp update can break it without notice.

## The problem

The reporter says `WPP.chat.sendFileMessage()` fails for every media type (audio, image, video, document) with `Cannot read properties of undefined (reading 'prepRawMedia')`. Text messages still work. With WhatsApp Web `2.3000.1050509545` and wa-js 4.7.0 (4.5.0 too), the console says a module named MediaPrep "was not found". Three users added "same".

## The reporter's diagnosis (not tested here)

wa-js looked for one module that exported both `uploadProductImage` and `MediaPrep`. The reporter says WhatsApp split them, so no module matches, and `prepRawMedia` now sits in a separate module (`WAWebPrepRawMedia`). Of about 193 modules wa-js resolves, they say only `MediaPrep` and `UploadUtils` failed. They included a short in-page workaround that redefines the missing property, and say audio delivery worked end to end with it.

## The fix (project member's statements)

A member says the fix merged in #3732 and shipped in 4.7.1 resolves `prepRawMedia` separately and handles named and default exports. They say they ran all 197 unit tests and TypeScript on it, and that the maintainer also tested carousel and media sending before merging. They ask users to retest with the 4.7.1 bundle actually injected, since a stale copy would still fail. As of my check nobody had replied that it worked. I only verified that the PR is merged and the release exists, not that it works.

## An open second problem

The reporter also says `WPP.loader.injectFallbackModule("MediaPrep", ...)` had no effect, because the property was already resolved. The member asks for a minimal call sequence if it still happens on 4.7.1.

## Why this was picked

The gap from report to fixed release was under an hour, and it shows how this class of break works: a rename inside the host app. Anyone running an old bundle needs to update and check that the new file is what's loaded.

## Honest limits

- Nothing was run, and I did not use WhatsApp Web.
- Fix confirmation by users is still missing in the thread.
- Using unofficial automation on WhatsApp can break WhatsApp's terms. This entry only records a bug report.
