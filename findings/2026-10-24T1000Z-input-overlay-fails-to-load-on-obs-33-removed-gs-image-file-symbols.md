# input-overlay fails to load on OBS Studio 33.0.0 - OBS removed the gs_image_file_* symbols the plugin imports

- Source issue: https://github.com/univrsal/input-overlay/issues/541 (open at check time; opened 2026-10-24 03:12 UTC)
- Projects: https://github.com/univrsal/input-overlay (latest stable 5.0.6, 2024-10-24; 5.1.0 is a 2025-04-06 pre-release) and https://github.com/obsproject/obs-studio (33.0.0 released 2026-10-23)
- Checked: 2026-10-24 10:15 UTC

## Problem
Right after upgrading to OBS Studio 33.0.0, the popular input-overlay plugin (shows keyboard/mouse/controller input on stream) fails to load with a plugin error dialog. Reproduced with both plugin 5.0.6 and the 5.1.0 pre-release, in normal and portable installs, old and new plugin locations.

## Root cause (verified in OBS source)
A commenter (arkus7) identified it: OBS 33.0.0 removed the `gs_image_file*` exports (including `gs_image_file4_init`, `gs_image_file4_init_texture`, `gs_image_file4_free`) in favor of a new `gs_image_file_ex_*` family in libobs. Since input-overlay.dll imports the removed symbols, Windows LoadLibrary fails with ERROR_PROC_NOT_FOUND. We confirmed this against the current obs-studio source: libobs/graphics/image-file.h on master declares only the `gs_image_file_ex_*` functions - the old names are gone. So the mechanism is not just the commenter's claim; the symbol removal is visible in the source.

## What the thread says
- The maintainer (univrsal) responded the same morning with a patched test build; the reporter confirms it loads and works.
- The reporter notes a packaging wrinkle for any fixed release: OBS 33 changed the plugin layout, so builds targeting 33.0.0 should be packaged the new way (a breaking change for users on older OBS, linking OBS' own KB on legacy plugin locations).
- No fixed numbered release exists yet - the working build is a zip attached to the issue.

## What we checked
- The issue, the maintainer's test build, and the confirmation exist as described.
- OBS 33.0.0's release date (2026-10-23) and the symbol removal in libobs source are verified.
- We did not run OBS or the patched build; "the test build works" is the reporter's confirmation.

## What this does not tell you
- Whether other OBS plugins importing the old gs_image_file_* symbols break the same way - plausibly yes, but the thread covers only input-overlay.
- When a proper fixed release ships. Until then, the maintainer's attached build is the only fix; it comes from the maintainer's own account in the official repo, but it is still a test build - the usual caution about running binaries from issue attachments applies, and staying on OBS 32.x until a release is the conservative alternative. Neither is a recommendation from us.

## Honest limits
- We read the issue and the OBS source file. Nothing was executed.
- Issue state may have changed since 10:15 UTC.
