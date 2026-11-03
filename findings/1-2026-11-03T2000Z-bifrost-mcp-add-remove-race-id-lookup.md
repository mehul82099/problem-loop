# Bifrost: MCP add/remove race lets a failed or removed AddClient delete, recreate, or take over the client

**Source:** [maximhq/bifrost#9582](https://github.com/maximhq/bifrost/issues/9582) - opened 2026-11-03 by Xytronix (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

When an MCP client is removed and a client with the same ID is added again while the first `AddClient` is still connecting, the first add can damage the new entry, because each step looks the client up by ID instead of by the entry that add created. Three distinct failure shapes:

1. **Failed add deletes the re-added client.** On a dial failure, the API path of `addClient` runs `delete(m.clientMap, config.ID)` without checking the map still holds its own placeholder. If the client was removed and re-added during the dial, the first add's failure deletes the new entry. The reporter notes boot dials are already protected (`keepAfterFailedBootDial` compares `current != entry`) but the API path is not.
2. **A removed add recreates or takes over the entry.** `connectToMCPClient` resolves the client by ID at its first manager lock. If `RemoveClient` ran after the placeholder was published but before that lock, the add either recreates an entry for the removed ID or adopts whatever entry now holds it - for a disabled re-add with the same ID it overwrites that entry's `ExecutionConfig` with the stale config and dials it.
3. **The restore guard ignores the connection (latent).** `failConnectAttempt` restores the old connection whenever the entry is the same pointer and not disabled, without checking the entry still holds `oldConn`. The reporter marks this one as hardening rather than an observed failure, since the per-client exclusive-operation slot makes it unreachable through public APIs today.

Reproduction (from the issue): add an HTTP MCP client whose server stalls during initialize, `RemoveClient(id)` while the add is in flight, re-add with the same ID (e.g. `disabled: true`), then let the first dial fail - the re-added client is gone from `GetClients()` (case 1), or the removed client comes back / the disabled re-add is adopted and dialed with the old config (case 2). The reporter relates it to #9573 (RemoveClient leaving the in-flight connection running), which widens the window.

The reporter has a proposed fix implemented and tested in a fork: pass the placeholder pointer into the dial and bail if `clientMap[id] != expectedEntry`; delete on failure only when the map still holds the placeholder; mark removal with an `errors.Is`-able sentinel; and restore in `failConnectAttempt` only when the entry also still holds `oldConn`. They report deterministic channel-gated regression tests and `core/mcp` passing with `-race -count=3`, and offer to open a PR.

## Verification (checked during this finding)

All cited anchors verified at the named dev commit (`5a751175ff2c`, 2026-11-03 - the commit exists):

- `core/mcp/clientmanager.go` ~1224-1235: the API-path dial-failure branch runs `delete(m.clientMap, config.ID)` with no ownership check, and `keepAfterFailedBootDial` immediately below (~1247-1253) does the `current != entry` comparison the API path lacks - the asymmetry is exactly as described, including the code comments about not keeping a client an admin removed.
- ~3125-3145: `connectToMCPClient`'s first manager lock resolves `m.clientMap[config.ID]`, adopts the existing entry, and overwrites `existingClient.ExecutionConfig = config` before dialing - the takeover path as described.
- ~3738-3742: `failConnectAttempt` restores `clientState.Conn = oldConn` when `clientState == entry` and not disabled, with no `clientState.Conn == oldConn` check - the latent case as described.
- Related issue #9573 exists and is open.

## Limits

- The race sequences were not executed here; they are timing-dependent and rest on the reporter's tests (which live in their fork, not in this repo). The mechanism is consistent with the verified code paths.
- The reporter's association is NONE. As of writing the only comment is a CodeRabbit automation plan (tooling, not maintainer triage); no maintainer position on the bug or the proposed fix yet.
- Case 3 is explicitly latent per the reporter; cases 1-2 require API-driven remove/re-add overlapping a dial, so boot-only deployments are much less exposed.
- The fork fix and its race-test results are the reporter's claims, not independently run.

## Sources

- Issue: <https://github.com/maximhq/bifrost/issues/9582>
- clientmanager.go at 5a751175ff2c: <https://github.com/maximhq/bifrost/blob/5a751175ff2c5904ffd6543ecca54c61ac1b1d5e/core/mcp/clientmanager.go>
- Related: <https://github.com/maximhq/bifrost/issues/9573>
