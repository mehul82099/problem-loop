# Flutter web: removing the default `flutter_service_worker.js` (flutter/flutter#156910)

- Source issue: https://github.com/flutter/flutter/issues/156910 "[web] Deprecate and remove `flutter_service_worker.js`". Opened 2024-10-15 by a Flutter team member (ditman) as a design-doc tracking issue. Open, labels include "platform-web", "P2", "design doc". 61 reactions on the post, 32 comments, last updated 2026-10-19.
- Merged pull request: https://github.com/flutter/flutter/pull/176834 "[web] Self-cleaning service worker", merged 2025-10-17 (state and date from the GitHub API).
- Related issue on cache busting of files in `build/web`: https://github.com/flutter/flutter/issues/149031 (I read only a comment about it, not the issue).
- Docs, read 2026-10-20: https://docs.flutter.dev/platform-integration/web/initialization . It says Flutter "no longer generates a service worker by default", and describes a `{{flutter_service_worker_version}}` token for custom service worker setups, and a deprecation warning for a `serviceWorkerVersion` variable in `index.html`.

## What is changing
By default a Flutter web build includes a service worker that caches the app's assets. The design doc says it is not a good fit for all apps, confuses developers who believe it is required, and the plan is to replace it with a cleanup worker that removes the old one from users' browsers, and later to stop generating any service worker so each app can pick its own approach.

## What the thread says
- Early comments (2024) are split. One commenter argues most developers want a PWA that just works, and the default should stay in some form. Another points out that a PWA no longer needs a service worker to be installable, linking web.dev's install criteria. The team member answered that the main problem is people thinking it is mandatory, and that he would prefer to use existing tools like Workbox for any generated one. These are comments, and I did not check the web.dev criteria.
- Caching concern: commenters asked how updates and cache busting would work without it. The team member said the new default moves the app to the browser cache, controlled via the CDN, and recommended `ETag` headers, and renaming assets with a version string as a workaround. A commenter replied that `max-age` can show stale versions, `must-revalidate` needs a server round trip, and Flutter's generated bootstrap files cannot be renamed by developers. The team member added that inlining `flutter_bootstrap.js` into `index.html` saves one round trip. Cache busting for generated files was called "down our priority list" by another Flutter team member on 2026-03-17.
- Status: a triage bot removed the original assignee in 2025-08 for lack of updates. The cleanup-worker PR merged in 2025-10. In 2026-03 a contributor reported that `--pwa-strategy none` now prints a deprecation warning that points at this issue, and that without the flag the generated bootstrap code contains a note that "Flutter's service worker is deprecated and will be removed in a future Flutter release". Per his comment, the answer to his question about producing no bootstrap logic was not given in the thread I read.
- 2026-07-09 (ditman): removal is slow because of Flutter's deprecation policy. The warning is there "to draw your attention to this issue", the flag keeps working as before for now, and once the service worker machinery is removed the flag will stop working and can be dropped. He says he is no longer on the web team, and others are driving it.

## What can be said
- As of these comments the default worker is deprecated, with a cleanup worker shipped, and full removal has no date in the thread. This note is not a migration guide. Check Flutter's own docs and release notes for your version before changing build flags or hosting cache headers, since wrong cache settings can leave users on stale app versions.
- If you rely on the default worker for offline use, the thread says you will need your own.

## Honest limits
- I did not build a Flutter web app or test any flag.
- I read about half the comments in detail and the last eight fully.
- I did not verify the PR contents, only its state and title.
