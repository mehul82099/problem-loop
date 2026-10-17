# Zellij: `new-pane --cwd` is ignored unless you also pass a command

- Source: https://github.com/zellij-org/zellij/issues/2766 (open, label `suspected bug`, opened 2023-09-02, last comment 2026-10-17)
- Latest release per the GitHub API on 2026-10-17: v0.45.1 (2026-08-28)
- Code read: https://github.com/zellij-org/zellij/blob/main/zellij-utils/src/input/actions.rs (main as fetched on 2026-10-17, lines around 1405 to 1510)

## The problem
The reporter (dchinmay2) ran `zellij action new-pane --cwd /home/p00f/foo` on 0.38.1 and expected a pane in that directory. The pane opened in the directory where Zellij was started. Others report the same for `new-tab` (KasimKaizer, 2024), on 0.41.2 (bennyyip, Feb 2025) and on 0.43.1 (DarioDarko, Nov 2025). On 2026-10-17 Virgil-N wrote "The error is still here". The version of that last report is not stated.

## Cause, from the thread and checked against current code
In 2023 marianomarciello and dchinmay2 pointed to the branch of the CLI action conversion that handles panes without a command: it builds the pane action with `command: None`, so the `cwd` value is never passed on. bennyyip linked the same branch in v0.41.2.

I fetched the file on main today. The branch that handles a non-empty `command` builds a `RunCommandAction` that includes `cwd`. The final `else` branch (no command), for floating, in-place, stacked and tiled panes, passes `command: None` and I found no `cwd` in the part I read (about lines 1463 to 1510). That fits the reports: `--cwd` only takes effect when a command is given.

## Workarounds reported (not run here)
- Give a command so the working directory is honoured: `zellij action new-pane -c --cwd /tmp -- $SHELL` (bennyyip, DarioDarko confirms it on 0.43.1).
- For a new tab: run `zellij action new-tab`, then `write-chars "cd <dir> && clear"` and `write 10` (Sawangg).

## Honest limits
- I did not run Zellij. The behaviour is from commenters' reports across several versions.
- I read one part of one function. I did not trace how `new-tab --cwd` is handled, and other code paths, such as layouts or plugins, may set the directory in other ways.
- The last comment gives no version, so I cannot say whether 0.45.1 is affected. The code on main reads as unfixed for the no-command branch, but that is my reading, not a test.
- The thread has no maintainer reply in the comments I read. Whether the behaviour is a bug or by design is not stated.
