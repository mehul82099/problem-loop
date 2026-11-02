# Bun leaves `O_NONBLOCK` set on an inherited stdout/stderr pipe after exit - the *next* process on that pipe fails with `EAGAIN`

**Source:** [oven-sh/bun#47710](https://github.com/oven-sh/bun/issues/47710) (open; no fix PR at publish time)

## What happened

The first touch of `process.stdout`/`process.stderr` on a pipe - even just reading `.isTTY` - puts `O_NONBLOCK` on the dup'd descriptor, and nothing restores the original file-status flags at exit. File-status flags live on the **open file description**, which is shared by every process holding that pipe, so after Bun exits the flag is still set: the next writer on the same pipe (`exec > >(tee log) 2>&1` patterns, `{ bun a.ts; other; } | less`, CI log collectors) gets `EAGAIN` and fails - in *its* process, with nothing pointing back at Bun. The reporter's one-line repro shows `head` failing with "Resource temporarily unavailable" after Bun ran, while Node in the same setup restores flags via `ResetStdio()` and `head` exits 0. The source-level mechanism is laid out against v1.4.3 (verified release): `FileSink::setup` sets `O_NONBLOCK` without recording the fd, so the synchronous-restore path never fires for process stdio, and `bun_restore_stdio()` restores termios only. The history makes it sting more: PR [#33827](https://github.com/oven-sh/bun/pull/33827) implemented a Node-style restore and was closed as superseded by [#43868](https://github.com/oven-sh/bun/pull/43868) - which only clears the flag for spawned children, not the inherited parent pipe; [#47408](https://github.com/oven-sh/bun/issues/47408) (open) is the in-process symptom of the same flag. All three verified.

## Who this bites

- Anyone running Bun inside shell pipelines or process-substitution logging (`exec > >(tee log) 2>&1` is a standard deployment/CI incantation): one Bun invocation poisons the pipe for every later command in the script, and the failure is misattributed by construction - the victim process reports the error, the culprit already exited cleanly.
- Bun-compiled CLIs are especially exposed since they're deployed exactly into these pipeline shapes; the reporter ships an FFI workaround that snapshots and restores the flag around signals, which is more than users should need.

## Limits

- Single-source report (repo ~85k stars, reporter association NONE) with source-level mechanism against 1.4.3 and a minimal repro I did not run; demonstrated on Linux/WSL2, POSIX-general in principle.
- The workaround (FFI snapshot/restore) is reporter-shipped, not maintainer-endorsed; repeated in this finding as context, not advice.
- No maintainer comment or fix PR yet; whether the fix lands as exit-time restore or not setting the flag for stdio is unresolved.
