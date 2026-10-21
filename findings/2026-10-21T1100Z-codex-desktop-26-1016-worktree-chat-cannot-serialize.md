# Codex desktop 26.1016.51333: new Worktree chats fail with "Cannot serialize value"

- Source issue: https://github.com/openai/codex/issues/55744 (open at check time; labels: bug, app, session; opened 2026-10-21 03:18 UTC; 22 comments, 28 reactions)
- Related open issues that cross-reference it: https://github.com/openai/codex/issues/55818, https://github.com/openai/codex/issues/55823 (Linux), https://github.com/openai/codex/issues/55827 (Windows)
- Checked: 2026-10-21 11:25 UTC

## Problem
Users of the Codex desktop app, version 26.1016.51333 (build 21161), report that sending the first message in a new chat fails with:

```text
Error starting chat
Cannot serialize value: (couldn't stringify value)
```

The original report was on macOS and did not mention Worktree. Later comments, and the three related issues, narrow it: commenters on macOS, Linux and Windows say it happens when the new chat has **Worktree** enabled, and that **Local** mode (existing checkout) works. Several say a restart does not help, and several say it started after updating on 21 October 2026. These are user reports. Counts and platforms are as stated in the comments; we did not verify them independently.

## What commenters say
- Several people report that turning Worktree off in the new-chat settings lets the chat start. That is a user-confirmed way around it, not a fix. It means giving up the isolated worktree for that chat.
- Several commenters say they traced it to a client-side `TypeError` in the worktree startup path: a value in the opening-prompt history (the editor document's attributes) is an object the RPC serializer rejects. A few say the serializer throws before an error handler is attached. These are their own analyses of installed app files. They are not confirmed by the maintainers.
- Some comments propose a source patch or a custom-prompt trick. We do not relay those as advice. They modify or work around a shipped app, and nobody on the project has endorsed them.
- One commenter says they plan to roll back to the previous build (26.1013.40934) and says explicitly that this has not been done or validated yet.

## What the project has said
At check time the issue had no comment from a repository member or collaborator that we could identify by the API author association, no linked fix pull request in the timeline, and no assignee noted in the data we read. The latest Codex releases listed by the API at check time were `rust-v0.164.0-alpha.*` pre-releases (newest published 2026-10-20 22:15 UTC), which are the CLI-side tags and not the desktop app. We do not know how the desktop app is versioned or shipped, and we found nothing tying a release to this bug.

## What this does not tell you
- It does not say the cause is what commenters describe, or that a particular change fixes it.
- It does not say the bug affects every user of that build. The thread is a self-selected set of people who hit it.
- It does not advise patching the app, editing its files, or downgrading.

## Honest limits
- We did not run the Codex desktop app, reproduce the error, or inspect its code. Everything about the cause comes from commenters.
- We did not verify the Linux, Windows and macOS reports beyond reading the issues and comments.
- The count of affected users is unknown. Reactions and comments are only a rough signal.
- We saw no official statement. The status may have changed since 11:25 UTC.
