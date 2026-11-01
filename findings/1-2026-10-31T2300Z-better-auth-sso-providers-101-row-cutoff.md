# Better Auth's SSO provider list quietly drops your own provider once the table has 101 rows - an unpaginated fetch filtered in JavaScript

**Source:** [better-auth/better-auth#12167](https://github.com/better-auth/better-auth/issues/12167) (open; code verified on `main`)

## What happened

`GET /api/auth/sso/providers` is documented as returning "a list of SSO providers the user has access to". The reporter seeded 100 `ssoProvider` rows belonging to other organizations, then created one provider for their own organization X as X's owner - and the endpoint returned 200 with **zero providers**. Deleting one seed row (100 total) made X's provider appear again.

The code on `main` shows exactly why ([providers.ts#L575-L586](https://github.com/better-auth/better-auth/blob/main/packages/sso/src/routes/providers.ts#L575-L586), verified): `listSSOProviders` calls `adapter.findMany({ model: "ssoProvider" })` with **no `where`, no `limit`, no `sortBy`** - it pulls the whole table and filters afterwards in JavaScript. And a `findMany` without an explicit limit falls back to `advanced.database.defaultFindManyLimit ?? 100` ([factory.ts#L728](https://github.com/better-auth/better-auth/blob/main/packages/core/src/db/adapter/factory.ts#L728), verified). So the endpoint sees at most the first 100 rows in storage order; if the caller's own provider is row 101, the access check runs against a window that doesn't contain it and the answer is a silent, wrong empty list. The reporter confirmed the same code on `main`, `next` and `v1.8.0-beta.3`, running better-auth 1.7.14 (release tag verified, Oct 26).

An AI triage bot on the issue (attributed as tooling, not maintainer review) claims a second cutoff in `batchCheckOrgAdmin` - partially borne out by the code: that fetch ([providers.ts#L460-L466](https://github.com/better-auth/better-auth/blob/main/packages/sso/src/routes/providers.ts#L460-L466)) also passes no explicit limit, but it *is* scoped by `userId` and an organization-id `in` clause, so it only truncates for a caller with more than 100 memberships - a much narrower edge than the unscoped provider fetch.

## Who this bites

- Any Better Auth deployment whose `ssoProvider` table grows past 100 rows: org owners and admins can be shown "no SSO providers" for organizations that absolutely have one - breaking SSO admin screens, setup wizards and any access logic built on this endpoint. Failure is silent and data-order-dependent, so it appears "randomly" as the table grows.
- The same unpaginated-then-filter shape anywhere else in the codebase would have the same cliff at the default 100; only this endpoint is established here.

## Limits

- The 101-row reproduction is the reporter's; I verified the fetch and the default-limit fallback in current `main` source, and the v1.7.14 release tag, but did not run the endpoint (repo ~30k stars).
- Row order decides which 100 rows are fetched; without `sortBy` the boundary case is storage-order dependent and may differ across databases.
- No maintainer response yet; the fix direction (push the filter into the query, or paginate explicitly) is obvious but unconfirmed by the team.
