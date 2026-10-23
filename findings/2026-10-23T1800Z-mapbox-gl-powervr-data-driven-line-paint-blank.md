# mapbox-gl-js: data-driven line and symbol paint renders nothing on PowerVR GPUs (Pixel 10) from 3.32.0

- Source issue: https://github.com/mapbox/mapbox-gl-js/issues/13742 (open at check time; label "bug"; opened 2026-10-22 03:21 UTC; 6 comments)
- Reporter's proposed fix: https://github.com/mapbox/mapbox-gl-js/pull/13743 ("Cap UBO size to 1KB on PowerVR GPUs with ANGLE on OpenGL ES", open, not merged)
- Reporter's upstream report: https://issues.chromium.org/issues/577092653 (Chromium issue; they also link https://issues.chromium.org/issues/527094637 as possibly related)
- Versions per npm: 3.32.0 (2026-09-29), 3.33.0 (2026-10-13, current latest); the reporter says 3.31.0 works
- Project: https://github.com/mapbox/mapbox-gl-js (about 12k stars per the API; note the repo's license field is nonstandard since the 2.x license change)
- Checked: 2026-10-23 18:50 UTC

## Problem
The reporter says that on a Pixel 10 Pro (PowerVR DXT-48-1536 GPU, Chrome 155, ANGLE on OpenGL ES), any `line` layer with even one data-driven paint property (for example a `feature-state` expression) draws nothing from version 3.32.0 on, while constant paint renders and `queryRenderedFeatures` still returns the features. The same page renders fine on desktop. They show a version table: 3.31.0 works, 3.32.0, 3.33.0 and 3.34.0-rc.1 all fail on that device.

## What the thread says
- The reporter's deeper analysis: the trigger is the size of the line paint uniform block - above roughly 3 KB the driver reads the whole block as zeros. They later showed the same for symbol layers on a production map, and that it depends on the ANGLE backend, not the GPU alone: forcing Chrome's Vulkan backend on the same phone renders correctly, and they reproduced the misread with a minimal WebGL 2 page without Mapbox, then filed the Chromium issue. All of this is the reporter's testing, not ours.
- A Mapbox engineer engaged, initially could not reproduce on Chrome 152, and the reporter explained the backend difference (Chrome versions driving the GPU through ANGLE-on-OpenGL-ES vs Vulkan).
- The reporter opened PR #13743 capping the uniform buffer size to 1 KB on the affected path, and reports their failing layers render with it. It is open and unmerged; we did not read the diff or test it.

## What we checked
- The issue, the PR, and the npm release timeline exist as described. The Chromium issue URL resolves to a real issue page (its contents require sign-in to read).
- We did not run a browser or touch a Pixel 10, so the entire device-specific mechanism is the reporter's evidence: detailed, internally consistent, and partly acknowledged by the maintainer's questions, but unverified by us.

## What this does not tell you
- Which devices and Chrome versions are affected beyond the reporter's Pixel 10 Pro setup is unknown; the maintainer could not reproduce on their device/Chrome combination.
- No fix is released, and whether Mapbox will take the 1 KB cap approach is undecided.
- If your maps do not use data-driven paint, or your users are not on PowerVR-with-ANGLE-OpenGL-ES, this likely does not affect you - that boundary is inferred from the thread, not surveyed.

## Honest limits
- We read the GitHub thread and registry data only. Device behavior claims are the reporter's.
- Issue state may have changed since 18:50 UTC.
