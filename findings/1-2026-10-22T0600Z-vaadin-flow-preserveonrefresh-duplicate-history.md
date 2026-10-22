# Vaadin Flow: @PreserveOnRefresh adds duplicate history entries with the React router

- Source issue: https://github.com/vaadin/flow/issues/26593 (open at check time; labels: routing, "Impact: Low", "Severity: Major"; opened 2026-10-21; 5 comments)
- Draft PR with the proposed fix: https://github.com/vaadin/flow/pull/26594 (open, draft, not merged)
- Draft follow-up PR: https://github.com/vaadin/flow/pull/26597 (open, draft, stacked on #26594)
- Earlier related issues (both closed): https://github.com/vaadin/flow/issues/19701 and https://github.com/vaadin/flow/issues/19718
- Project: https://github.com/vaadin/flow (Apache-2.0, 758 stars per the API)
- Checked: 2026-10-22 06:35 UTC

## Problem
The reporter says that in an app using the default React router, a layout annotated with `@PreserveOnRefresh` makes every in-route navigation that only changes query parameters add two browser history entries instead of one. The visible effect: Back seems to do nothing every other press, and Forward is lost. They give a table of `history.length` readings (6 after two link clicks with the annotation, 4 without) and say the view's `beforeEnter` sees `NavigationTrigger.REFRESH` for every navigation, including Back, where it sees `ROUTER_LINK` and `HISTORY` without the annotation. Versions given by the reporter: Vaadin 25.2.3 and 25.3.3, Spring Boot 4.1.0, Java 21, Chromium via Playwright. They say the code is unchanged on `main`.

## Cause as described in the thread
The reporter and a contributor who traced the code both say: when a preserved chain is found, the navigation event is rewritten with the trigger `REFRESH` whatever the original trigger was, and the chain is matched on the path only, so a query change on the same route matches. In React mode the server then pushes a history entry that the React router already made. The contributor adds that `REFRESH` is documented as a reload-only trigger, and says the earlier fix for #19701 (shipped via #19718, both closed, which we confirmed by API) is why the React push branch exists. We did not read the Vaadin source ourselves, so the cause is their account.

## Status
- Maintainer response: a member told the contributor to try the suggested approach and iterate in a PR.
- #26594 (draft, opened 2026-10-22, 3 files changed per the API) is described by its author as turning an event into `REFRESH` only when the original trigger is a page load, with a unit test and an integration test that, per the author, fails without the fix. #26597 (draft) is a stacked follow-up about not pushing history on reload of a preserved view.
- The contributor posted a snapshot build for testers and asked the reporter to try it. No test result was posted at check time.
- Note on authorship: the contributor account that posted the analysis and PRs is not a project member. We cannot say how the work was produced and do not treat it as maintainer-confirmed beyond the member's reply above.

## Trade-off mentioned in the thread
The contributor says that after the change, `isRefreshEvent()` would return `false` for in-route link, Back and programmatic navigations on a preserved view, where it returns `true` today. An app that relied on the current behavior to skip re-initialization might notice. Reviewers have not yet decided on it, as far as the thread shows.

## What this does not tell you
- No fix is merged or released. Both PRs are drafts.
- We do not advise running the snapshot build in production, and have not run it. It is a pre-release build on the 25.4 line.
- We did not reproduce the bug.

## Honest limits
- All technical claims are from the reporter, a contributor, and the PR descriptions. We verified only that the issues and PRs exist with the stated state, that #19701 and #19718 are closed, and the repo facts.
- Status may have changed since 06:35 UTC.
