# Every extra `:filter` wins the argument and loses the memory: Neovim's overwrite-without-free

- Source issue: https://github.com/neovim/neovim/issues/42563 (open; opened 2026-10-27)
- Project: neovim/neovim (~103k stars)
- Checked: 2026-10-28 00:12 UTC

## Problem
Chain two `:filter` modifiers on one command - `:filter /a/ filter /b/ ls` - and Neovim's command-modifier parser overwrites the first pattern and its compiled regexp without freeing them. The code happily strdup's the new pattern over the old pointer and compiles a new regprog over the old one (ex_docmd.c, cited with line numbers); cleanup (`undo_cmdmod()`) frees only the last one. Behavior is unaffected - the last filter wins, as designed - but every extra filter leaks one pattern string plus one compiled regexp. Measured: 200,000 runs of the two-filter command grew RSS by about 68 MB, roughly 355 bytes per call. And it leaks even when the command is never executed: pure parsing via `nvim_parse_cmd()` / `parse_cmdline()` hits the same path, so Lua plugins and RPC clients can drip-feed the leak without running a single command.

## Why it is interesting
- A textbook overwrite leak in a place nobody thinks to look. Command modifiers feel stateless - parse, apply, done - so "the last one wins" reads as correct. It is correct, semantically. The leak lives in the gap between "the last value wins" and "the previous value still needed a free." The report is the ideal form of this finding: two lines of source, the cleanup function that only frees the last, and a measured cost per call.
- The reachability detail is what elevates it from trivia. A leak that requires a user to type a weird command is a curiosity; a leak reachable through `nvim_parse_cmd()` is an API-surface problem. Any plugin that parses user-influenced command strings - or an RPC client talking to a long-lived embedded nvim - can accumulate it silently. Long-running hosts make small leaks into uptime bugs.
- The measurement is honest and modest: ~355 bytes per call is nothing for a one-off, 68 MB for a loop of 200k, and the reporter says so without drama. That calibration - here is the exact cost, decide if it matters to you - is rarer than the bug itself.
- Provenance worth noting: found by fuzzing the Ex command parser (`nvim_parse_cmd()`) with libFuzzer + ASan/LSan - the leak was caught by tooling, not a human noticing slowdowns. And the bug is inherited: Vim carries the same ex_docmd.c code and leaks the regprog the same way, so one fix here likely means a second bug report there.
- No maintainer comment yet at check time; the reporter even supplies the fix (free the old pattern/regprog before overwriting), but nobody has claimed it.

## Honest limits
- Single reporter, no maintainer engagement at check time; the leak is unconfirmed by the project.
- The RSS figures come from the reporter's local loop; not independently reproduced.
- Real-world impact depends on how often plugins/RPC clients parse multi-filter commands - likely rare, as the reporter implies.
- Issue state may have changed since 00:12 UTC.
