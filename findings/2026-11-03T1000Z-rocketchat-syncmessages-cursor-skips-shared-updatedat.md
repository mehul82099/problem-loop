# Rocket.Chat: chat.syncMessages cursor pagination silently drops messages that share the same _updatedAt (mobile clients never see them again)

**Source:** [RocketChat/Rocket.Chat#43457](https://github.com/RocketChat/Rocket.Chat/issues/43457) - opened 2026-11-03 by 5meter (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

When a mobile client catches up on a room via `chat.syncMessages` with cursor pagination (`next` + `count` + `type=UPDATED`), messages are silently skipped if several messages share exactly the same `_updatedAt` timestamp. The client's sync cursor then advances past the gap, so the missing messages are never requested again. Restarting the app does not help; only "Clear local server cache" or re-login restores them. Desktop and web clients are not affected because they use `fromTs`/`lastUpdate` without pagination.

Identical `_updatedAt` values are common in practice, per the reporter: with read receipts enabled, marking a room as read updates all unread messages in a single `updateMany`, so they receive the same timestamp. On their ~20-user server they found 128 same-timestamp groups within 14 days, the largest containing 429 messages.

Reproduction (from the issue): enable read receipts, have user A offline while others post 60+ messages, user B reads the room (all messages get one shared `_updatedAt`), then user A opens the room on mobile. The app pages through `chat.syncMessages` with `count=50`; when the page boundary lands inside the shared-timestamp group, the rest of the group is never returned.

## Root cause (reported, verified against current source)

The reporter points at the `chat.syncMessages` handler's pagination helpers (`mountCursorQuery` / `mountNextCursor` / `handleCursorPagination`). I checked them on the `develop` branch (`apps/meteor/server/publications/messages.ts`); the mechanism is exactly as described:

- `mountCursorQuery` sorts by `{ _updatedAt: 1 }` with `limit: count + 1`, and a `next` cursor becomes the query `{ _updatedAt: { $gt: extractTimestampFromCursor(next) } }`.
- `mountCursorFromMessage` builds the cursor as `` `${message._updatedAt.getTime()}` `` - a bare millisecond timestamp with no tiebreaker.
- `extractTimestampFromCursor` parses that integer back into a Date.

So when the `count + 1` window ends inside a group of messages with identical `_updatedAt`, the returned `next` cursor equals that shared timestamp, and the following page's strict `$gt` filter excludes every remaining message in the group. The `previous` direction (`$lt` with reversed sort) has the same shape of problem.

The reporter's claim that a room-read fans out into one bulk update also checks out: `Messages.setVisibleMessagesAsRead` in `packages/models/src/models/Messages.ts` is a single `updateMany` over `{ rid, unread: true, ts: { $lt: until } }`. (Whether every matched document ends up with byte-identical `_updatedAt` depends on the model's update stamping, which I did not trace further - the reporter measured 128 groups on their own server.)

## Status of the fix

The issue links PR [#43255](https://github.com/RocketChat/Rocket.Chat/pull/43255) ("fix: avoid skipping messages that share a timestamp in chat.syncMessages cursor pagination"), which replaces the bare timestamp with a compound `<ms>_<id>` cursor. Per the GitHub API, that PR was **closed unmerged on 2026-10-31** by its author (jeanfbrito), and the pagination code on `develop` still builds bare-timestamp cursors, so no fix has landed. Note: an automated CodeRabbit comment on the issue lists the PR as "[open]", which is stale - the PR API shows it closed. The reporter also notes that because the compound cursor would be opt-in, the mobile apps would additionally need to adopt it.

## Limits

- Behavior statements come from the issue and the reporter's server logs; I did not run a Rocket.Chat server to reproduce. The pagination-code mechanism is verified verbatim on `develop` as of 2026-11-03.
- The reporter's association is NONE, so the production observations (128 groups, 429-message group, iOS app versions) are self-reported. As of writing the issue has no maintainer response - the only comment is CodeRabbit automation, which is tooling output, not maintainer triage.
- Reported against server 8.9.0 (released 2026-10-05; the 9.0.0 line is still at RC tags, e.g. 9.0.0-rc.0, at check time). The reporter's workaround - a job that rewrites each message in a same-timestamp group to its own `_updatedAt` - mutates server data; this finding reports it as their approach and does not recommend running it.

## Sources

- Issue: <https://github.com/RocketChat/Rocket.Chat/issues/43457>
- Pagination helpers (develop): <https://github.com/RocketChat/Rocket.Chat/blob/develop/apps/meteor/server/publications/messages.ts>
- Closed compound-cursor PR: <https://github.com/RocketChat/Rocket.Chat/pull/43255>
- Bulk mark-as-read update: <https://github.com/RocketChat/Rocket.Chat/blob/develop/packages/models/src/models/Messages.ts>
