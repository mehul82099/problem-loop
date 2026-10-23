# Codex Windows desktop: resuming or creating chats fails after an update with an MXC "missing SYSTEMROOT" error

- Source issue: https://github.com/openai/codex/issues/56264 (open at check time; labels "bug", "windows-os", "sandbox", "app", "session"; opened 2026-10-22 21:00 UTC; 6 comments)
- Source files a commenter points at, on `main`:
  - https://github.com/openai/codex/blob/main/codex-rs/exec-server/src/fs_sandbox.rs
  - https://github.com/openai/codex/blob/main/codex-rs/mxc-sandbox/src/transport.rs
- Project: https://github.com/openai/codex (Apache-2.0, about 130k stars per the API)
- Earlier findings on other Codex topics: `2026-10-21T1100Z-codex-desktop-26-1016-worktree-chat-cannot-serialize.md`, `2026-10-17T1600Z-codex-weekly-quota-drops.md`
- Checked: 2026-10-23 05:00 UTC

## Problem
The reporter says that after updating the Codex Windows desktop app (desktop `26.1016.62342`, bundled CLI `codex-cli 0.163.0-alpha.11.2`, Windows 11 Pro), an existing local chat cannot be resumed. The error says the filesystem sandbox helper failed because the MXC launcher was given a `process.env` of only 5 variables, missing `SYSTEMROOT`, which Windows requires to be present. They stress this is a suspected post-update regression based on timing, not proven causality.

## What the thread says
- In follow-ups the reporter says the failure is not limited to old threads: a brand-new non-fork chat in the same project failed the same way once a restricted permission profile was selected, and a same-directory `fork_thread` also failed before any child was created. They say three normal recovery paths (resume, fresh successor, fork) all fail.
- They tried setting `SYSTEMROOT` through the documented `shell_environment_policy.set` config and restarting the app; the same error occurred. They also tried `prefer_mxc = false` with `windows.sandbox = "elevated"` and say the helper still invoked MXC. We did not verify these settings against current docs.
- They describe a partial workaround for new replacement chats only: setting `project_doc_max_bytes = 0` in the project config to skip automatic AGENTS.md loading, then loading instructions manually. They say it does not fix the missing-`SYSTEMROOT` environment and does not recover chats already in the failure state. We did not test this; treat it as the reporter's own experiment, not advice.
- A second user reports the same missing-SYSTEMROOT error on Windows, including for new desktop sessions, on the same desktop build. They note the separately installed stable npm CLI (`0.163.0`) works in the same directories with the same config, with the sandbox active.

## What we checked
- A commenter proposed a cause from public source, labeled by them as a hypothesis: `exec-server/src/fs_sandbox.rs` filters the helper environment without retaining SystemRoot, while `mxc-sandbox/src/transport.rs` adds SystemRoot only when `default_child_env` is true.
- We read both files on `main`. `fs_sandbox.rs` line 49 defines the helper environment allowlist as `["PATH", "TMPDIR", "TMP", "TEMP"]`, with no SystemRoot. `transport.rs` line 18 adds "SystemRoot" only when `command.default_child_env` is true. That is consistent with the commenter's reading. It does not prove the installed build matches this source, which the commenter also says they could not verify.
- No maintainer reply was in the thread when we checked.

## What this does not tell you
- There is no confirmed root cause, no fix, and no maintainer statement in the thread.
- The affected versions come from the two reporters' own installs; we cannot confirm which desktop or CLI builds carry the problem.
- The reporter's workaround is unvetted. If you hit this, the second reporter's note that the stable npm CLI worked for them is also just their report, not a recommendation from us.

## Honest limits
- We did not run Codex, Windows, or any reproduction. We read the issue and the two cited source files on `main`.
- Thread state may have changed since 05:00 UTC.
