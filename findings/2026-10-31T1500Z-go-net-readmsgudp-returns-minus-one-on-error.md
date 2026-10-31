# Go's `ReadMsgUDP` returns `n = -1` on error on Linux - a failed read that looks like a packet, and a panic if you slice with it

**Source:** [golang/go#82746](https://github.com/golang/go/issues/82746) (open, unlabeled; code anchors verified on `master`)

## What happened

Every Go read API returns `n = 0` with an error when a read fails. Not `ReadMsgUDP`/`ReadMsgUDPAddrPort` on Unix: the reporter (vnxme, association NONE) shows a read that fails by deadline and one that fails by `Close` both return `n=-1, oobn=0` on Linux, on go1.28-devel, go1.27 and go1.26 (their [playground repro](https://go.dev/play/p/gHl4Ny-SBrx?v=gotip), link verified). Windows returns `n=0` for the same program, and so do Linux's own `Read`, `ReadFrom`, `ReadFromUDP*`.

The cause is a long-standing TODO. Verified on `master` in `src/internal/poll/fd_unix.go`: the three `ReadMsg*` functions (`ReadMsg` line 302, `ReadMsgInet4` line 329, `ReadMsgInet6` line 356) all carry `// TODO(dfc) should n and oobn be set to 0` and return the raw `recvmsg` result on error - which is -1. In the same file the `Read`/`ReadFrom`/`ReadFromInet4`/`ReadFromInet6` functions set `n = 0` on error (lines 172, 199, 221, 248, 275). `net` passes the -1 straight through to the caller.

The trap is real Go code: a caller that tests `n == 0 && err != nil` to detect a failed read - the convention everywhere else - sees `n=-1` and treats the failed read as a packet with a negative length; slicing `buf[:n]` panics. A negative count from a read is exactly what the oldest open-era net bug said should never happen ([#200](https://github.com/golang/go/issues/200), closed), and the write side of the same inconsistency was already litigated in [#19073](https://github.com/golang/go/issues/19073) (closed; both verified).

## Who this bites

- UDP servers using the `ReadMsg*` family (chosen for out-of-band data / `netip` addresses) with deadlines or graceful shutdown via `Close`: both normal control flows hit the -1, so any error-handling that assumes the usual `n == 0` contract misbehaves on exactly the paths operators exercise.
- Cross-platform code: the same check works on Windows and silently breaks on Linux, so tests pass on one OS.

## Limits

- The playground outputs are the reporter's; I verified the three TODO sites, the contrasting `n = 0` assignments in the sibling functions on `master`, and both related issues, but did not run the program. Repo ~139k stars.
- The issue is hours old, unlabeled, no maintainer response; the proposed fix (`n, oobn = 0, 0` in the three functions) mirrors what `ReadFrom*` already does but has no maintainer endorsement. Changing it is technically a behavior change for anyone who already special-cases -1.
- `ReadMsgUnix` and `ReadMsgIP` are affected "presumably" per the reporter - the same TODO pattern suggests yes, but only the UDP path was demonstrated.
