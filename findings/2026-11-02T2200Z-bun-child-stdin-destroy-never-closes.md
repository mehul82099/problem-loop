# Bun: destroying a child process's stdin while a write is pending never emits 'close', so finished() waits forever

**Source:** https://github.com/oven-sh/bun/issues/47807 (opened 2026-11-02, open, no maintainer reply yet)

## The problem

On Bun 1.4.4 (macOS arm64), if you destroy a child process's stdin stream while a large write is still pending - easy to arrange with any child that never reads stdin, since the pipe fills and the write queues - the stream reports `destroyed: true` but never emits `'close'`, and `closed` stays `false` forever. Node 24 emits `'close'` and sets `closed: true` in the same situation. The reporter's repro is 15 lines: spawn `sleep 600` with piped stdin, fill the pipe with 64 KiB chunks until backpressure, destroy the stream, and check a second later. Bun: `{ closed: false, destroyed: true, closeEvent: false }`. Node: all three true.

## Why it matters

`'close'` is the contract that cleanup code waits on. Anything that awaits a destroyed writable - `stream.finished()`, or a poll of `.closed` - hangs forever, and the failure has a real downstream victim: the reporter links Effect-TS/effect#10314 (verified open), where interrupting a child process on Bun hangs in a busy loop because Effect's stdin release polls `closed` and it never flips. So a one-line runtime divergence turns into a user-visible hang in a major TypeScript ecosystem library, with the loop burning CPU as a bonus. Node-compat gaps in lifecycle events are especially costly because nothing throws - the program just never finishes.

## Caveats

- Open with no maintainer response; reporter association NONE. The repro is self-contained and the Node comparison output is the reporter's; this finding verified the linked downstream issue and the bun-v1.4.4 release tag, but did not re-run the repro.
- The report is specific to macOS arm64; whether other platforms behave the same is untested there.
- This finding does not propose a fix.
