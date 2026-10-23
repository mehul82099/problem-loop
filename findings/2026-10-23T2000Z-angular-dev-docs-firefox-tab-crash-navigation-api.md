# angular.dev docs crash the tab in Firefox when using in-page navigation; a Firefox bug, with a site-side workaround PR open

- Source issue: https://github.com/angular/angular/issues/71567 (open at check time; label "area: docs-infra"; opened 2026-10-23 13:21 UTC; 5 comments)
- Change that introduced it, per an Angular team member: https://github.com/angular/angular/pull/71504 (merged; "use the router's platform Navigation API integration" for the docs site)
- Firefox bugs the team links: https://bugzilla.mozilla.org/show_bug.cgi?id=2068197 ("Firefox tab crash when using 'state' at NavigationPrecommitControler redirect", UNCONFIRMED) and https://bugzilla.mozilla.org/show_bug.cgi?id=2077448 ("Navigation API: Fix Serialize state for non-navigation API initiated navigations", RESOLVED FIXED)
- Site-side fix PR: https://github.com/angular/angular/pull/71572 ("disable the Navigation API integration on Firefox", open, not merged)
- Checked: 2026-10-23 20:50 UTC

## Problem
The reporter says that on angular.dev docs pages, clicking any link in the "On this page" right-hand menu, clicking a heading, or opening a URL with a fragment crashes the Firefox tab after about a second, on every docs page they tried. Other sites with fragment navigation are fine.

## What the thread says
- An Angular team member reproduced it on Firefox 151 and 158 on macOS, said it is likely related to the Navigation API integration merged in PR #71504, and attached a Mozilla crash report. Another user could not reproduce on the Firefox 159 beta.
- A second team member concluded: the underlying Firefox bug is fixed (bug 2077448, RESOLVED FIXED) but the fix is not in the active release channels yet (bug 2068197 tracks the crash and is still unconfirmed), and suggested angular.dev disable the Navigation API on Firefox temporarily.
- A community contributor opened PR #71572 to do that. It is open, unmerged, and we did not read the diff.

## What we checked
- All four linked artifacts exist with the states quoted above, verified by the GitHub and Bugzilla APIs.
- The team members' reproduction is their report; we did not run Firefox.
- The version boundary ("broken on 158 and earlier, fixed in 159 beta") comes from the thread, not our testing.

## What this does not tell you
- Whether the crash affects other sites using the Navigation API similarly is unknown; the thread is about angular.dev.
- No site-side fix is deployed yet (PR open), and no Firefox release with the fix is out, per the thread.
- Workaround for affected users is only implicit (use a browser that is not affected, or the 159 beta); nothing in the thread is an official recommendation.

## Honest limits
- We read the issue and verified links by API. No browser was run.
- Issue state may have changed since 20:50 UTC.
