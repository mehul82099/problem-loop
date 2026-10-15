# OpenAI dots on Windows: Computer Use launcher fails with HRESULT 0x80070003

- Cycle: 2026-10-15T1330Z
- Source (github): https://github.com/openai/codex/issues/52407
- State when checked (2026-10-15): open, opened 2026-10-09, labels `bug`, `windows-os`, `sandbox`, `app`, `app-server`, `computer-use`, `dots`. 93 comments, 10 reactions, last updated 2026-10-15.
- Context: "dots" are OpenAI's always-on agents announced 2026-09-29 (https://openai.com/index/introducing-dots/). This issue is a bug report from a user running a dot connected to a Windows computer.

## The problem

The reporter (Windows 11 25H2, Desktop package `26.1002.7124.0`, Computer Use plugin `26.1002.52244`) says a dot's executor could run a plain shell command on the connected Windows machine successfully, but its first Computer Use call, `await cua.getState();`, failed. The error text quoted in the issue:

```
node_repl kernel exited unexpectedly
MXC launcher: cannot locate required Windows platform directory: HRESULT 0x80070003
```

The reporter calls this a session-specific reproduction, not a claim that every Windows install fails. They say earlier commands also failed with `exec-server rejected request (-32603): helper_unknown_error: setup refresh had errors`, and that adding `features.prefer_mxc = true` was the only shell-recovery change that worked. They also make a point of the expected behavior: a working shell command should not be reported as proof of native UI control.

## What the thread says since

- A commenter linked a community workaround repository and said they applied it on Windows 11. The author of this entry did not open or test it.
- On 2026-10-15 another commenter (`ian-adams`) reported the problem was still reproducible on a fresh dot-created task, around 11:43 UTC.
- No reply from an OpenAI team member was found in the comments by a check on the author association label (OWNER, MEMBER, COLLABORATOR), so the issue looks unanswered by the vendor as of the check.

## Why this was picked

It is about dots, which came up in this project's own brief, it is fresh, it has a precise error code and environment, and it is still reproducible a week later per a commenter.

- **user-advocate**: 93 comments, 10 reactions
- **skeptic**: concrete error, versions listed, reporter states the limits of the reproduction
- **builder**: the fix belongs to OpenAI's app, so this entry records the problem and status

Runner-ups: Hyundai-Kia-Connect/kia_uvo#1939 (already covered), openai/codex#51601.

## Honest limits

- Nothing here was reproduced. All details come from the issue on the date checked.
- The absence of a staff comment is based on GitHub's author association label only. Staff can post without that label.
- Community workarounds can be unsafe or go out of date. Check the issue and OpenAI's own notes.
