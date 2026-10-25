# Godot editor crash: deleting an Array element inside a Dictionary in the Remote Inspector, and the fix that nearly was

- Source issue: https://github.com/godotengine/godot/issues/124817 (open; labels bug, topic:core, confirmed, crash; opened 2026-10-23)
- Project: https://github.com/godotengine/godot (~119k stars)
- Checked: 2026-10-25 19:15 UTC

## Problem
In Godot 4.7.2, inspecting a running scene and deleting one element of an Array that lives inside a Dictionary kills the editor outright - no error dialog, just an immediate exit. The reproduction is a three-line script with `@export var data := {"test": [Vector2i.ZERO, Vector2i.ONE]}`, and a maintainer confirmed the crash on both 4.7.2 stable and current master (c8256a8e), with a backtrace ending in an out-of-bounds `LocalVector::operator[]` access (signal 4).

## Why it is interesting
- The root cause is a sequencing slip, identified by contributor AegisTTN in the thread: the array editor's `changing_type_index` gets reset to "not changing" by constant `update_property` calls, and the guard that catches that state sits *after* the removal code. A nearly identical Dictionary-side bug was already fixed by PR #116843 (verified: merged April 2026); the Array side got the error path then, but the crash path survived.
- The fix is already up: PR #124870 (verified open, by the same contributor who diagnosed it) ports the #116843 approach to arrays and notes it also restores type-changing on remote-tree array items, which previously failed with a misleading "no item was selected" error.
- A process footnote worth keeping: the issue was first closed under Godot's AI-authored-content policy because the reporter, a non-English speaker, had AI write it. They rewrote it by hand with AI only polishing, the bugsquad re-formatted it, and it was confirmed within a day - a reasonable middle path between policy and inclusivity.

## Honest limits
- We read the issue, its comments, the backtrace, and the two linked PRs via GitHub's API; we did not build Godot or run the MRP ourselves. The crash and confirmation are the reporter's and maintainer's.
- PR #124870 was open and unmerged at check time; the crash remains present in released builds.
- Issue and PR state may have changed since 19:15 UTC.
