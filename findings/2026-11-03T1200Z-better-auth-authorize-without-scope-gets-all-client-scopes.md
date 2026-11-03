# better-auth oauth-provider: an authorize request without scope gets every persisted client scope, not the default scopes

**Source:** [better-auth/better-auth#12194](https://github.com/better-auth/better-auth/issues/12194) - opened 2026-11-03 by birbprophet (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

When an OAuth2 authorize request carries no `scope` parameter, `authorizeEndpoint` falls back to the client's *entire persisted scope list* - not the operator-configured default scopes. Concretely: with `clientRegistrationDefaultScopes: ["openid", "files:read"]` and `clientRegistrationAllowedScopes: ["openid", "files:read", "members:write"]`, a client registered with `scope: "openid files:read members:write"` that later calls `/oauth2/authorize` without `scope` is asked to consent to `members:write` - a scope the operator configured as opt-in only. Per the reporter, clients that simply follow discovery get prompted for write scopes that were meant to stay available only on explicit request.

Expected behavior per the reporter: with no `scope`, the request should get the client's scopes that are among `clientRegistrationDefaultScopes`; anything beyond the default should require an explicit request. Their suggested fix filters the fallback: `requestedScopes = (client.scopes ?? opts.scopes ?? []).filter((s) => opts.clientRegistrationDefaultScopes?.includes(s) ?? true)`.

## Verification (checked during this finding)

- In `packages/oauth-provider/src/authorize.ts` on `main` at the commit the reporter names (`0e75ddcf36`, 2026-11-01; the commit exists), lines ~644-648 read exactly:

  ```ts
  // Always set default scopes if not originally sent
  if (!requestedScopes) {
      requestedScopes = client.scopes ?? opts.scopes ?? [];
      query.scope = requestedScopes.join(" ");
  }
  ```

  So the fallback is the client's full persisted scope list, with no intersection against `clientRegistrationDefaultScopes` - the reported behavior. The reporter says the same code is in release 1.7.15; release v1.7.15 exists (published 2026-11-01).

- An automated reply on the issue (the repo's Dosu bot - tooling output, not maintainer triage) points out the case is broader than the repro: `resolveClientRegistrationScopes` (`packages/oauth-provider/src/register.ts:54-61`) persists the *union* of `clientRegistrationDefaultScopes` and `clientRegistrationAllowedScopes` as the client's scope set for dynamic / client-metadata-document registration (register.ts:892-899). I verified both line ranges at the same commit: the union and the unconditional persistence for those registration sources are as described. Under that reading, even a client registered with only the default scopes hits the same omitted-scope fallback to the full allowed set. The reporter's narrower repro (explicitly requesting the wide scope at registration) is a subset of this.

## Limits

- The reproduction was not executed here against a live better-auth server; the behavior statements rest on the issue text plus the verified source lines above. Whether persisted union-of-scopes is intended as a capability set rather than a grant - the framing in the automated comment - is a design question for the maintainers; the reporter explicitly frames the omitted-scope consent prompt as unexpected.
- The reporter's association is NONE, so their account is self-asserted. As of writing there is no maintainer response; the only comment is the repository's automation bot, which is tooling output and not maintainer triage or approval.
- Scope-consent UX and the actual access granted also depend on how downstream resource servers validate scopes, which is outside this report.

## Sources

- Issue: <https://github.com/better-auth/better-auth/issues/12194>
- authorize.ts at 0e75ddcf36: <https://github.com/better-auth/better-auth/blob/0e75ddcf36489aa3a191ea902a82d1892034dc74/packages/oauth-provider/src/authorize.ts>
- register.ts at 0e75ddcf36: <https://github.com/better-auth/better-auth/blob/0e75ddcf36489aa3a191ea902a82d1892034dc74/packages/oauth-provider/src/register.ts>
- Release v1.7.15: <https://github.com/better-auth/better-auth/releases/tag/v1.7.15>
