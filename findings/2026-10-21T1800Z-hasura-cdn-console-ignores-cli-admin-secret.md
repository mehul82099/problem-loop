# Hasura CLI Console: the CDN console build ignored the admin secret passed by `hasura console`

- Source issue: https://github.com/hasura/graphql-engine/issues/10889 (open at check time; no labels; opened 2026-10-20 16:43 UTC; 4 comments, 7 reactions)
- Project: https://github.com/hasura/graphql-engine (Apache-2.0, 32,126 stars per the API)
- Commit the maintainers' reply points to: https://github.com/hasura/graphql-engine/commit/2d7c35e558 ("console: fix CLI admin-secret authentication bootstrap", 2026-10-21 11:06 UTC per the API)
- Checked: 2026-10-21 18:35 UTC

## Problem
`hasura console` starts a local web console and, by default, loads the console's JavaScript from Hasura's CDN. The reporter (Hasura v2.50.3 and CLI v2.50.3 in Docker, admin secret set) says that after a console build was published to the CDN on 2026-10-19 (22:29 GMT per the Last-Modified header they quote), the console stopped using the admin secret the CLI gives it. They saw GraphQL requests rejected, the built-in secret header not editable, and later a login page saying "Invalid admin-secret passed from CLI" with no way to log in, although the secret works with curl. Another commenter on v2.51 says the CDN's v2.51 channel got the same build, and that the console bundled with the v2.51.1 CE image is the same build too.

## Causes people proposed
The reporter and the second commenter read the minified console code and a CLI commit (d9b5cb8f6e, 2026-10-11, "remove URL prefix of hasura console command") and say the CLI passed an `isAdminSecretSet` value to its template data that none of its HTML templates print into the page, so the console treated the session as having no auth. These are their readings of the code. We checked that both commits exist by API. We did not read the code.

## What the maintainers said
- A contributor first asked whether the CLI had been upgraded to v2.51.1, saying the console had a large rewrite. The commenter replied that they had, with the same result.
- At 15:08 UTC a contributor wrote that they had "released the console hotfix to the CDN", asked the user to reload and clear the browser cache and try again, and said to remove the `HASURA_GRAPHQL_CONSOLE_ASSETS_DIR` setting because local console assets cannot be patched until the next version release.
- The commit 2d7c35e558 touches the CLI console templates, the console header, and an `AuthProvider` test, and its message matches the fix described. We did not verify that it is the one deployed.
- At the time we checked there was no reply from the reporter confirming the fix, and the issue was still open.

## What this means for readers
- If you use `hasura console` with an admin secret and saw this login error since 19 October, the maintainer says a CDN hotfix is out and a hard reload is needed. We could not test that.
- Do not treat the workarounds in the thread as advice. They involve running with local console assets or editing browser storage that holds the admin secret, and the maintainer says the local assets route is no longer the right setup.

## Honest limits
- We did not run Hasura or the console, did not fetch the CDN assets, and could not confirm which build is live now.
- The root-cause analysis belongs to commenters. We confirmed only that the cited commits exist and the maintainer statements were posted.
- The admin secret is a powerful credential. The thread does not describe a leak, and we claim none.
