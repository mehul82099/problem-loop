# CPython asyncio: one failed `setsockopt(TCP_NODELAY)` during accept leaves a zombie transport - `wait_closed()` hangs and the fd is poisoned for every later connection

**Source:** [python/cpython#161076](https://github.com/python/cpython/issues/161076) (open, CONTRIBUTOR reporter, discloses AI-assisted investigation with author-run repro and review; no fix PR at publish time)

## What happened

`_SelectorSocketTransport.__init__` (and the Proactor equivalent) calls `_set_nodelay(sock)` *after* the transport has already registered itself - `server._attach(self)` and `loop._transports[fd] = self`. Since the accept-path hardening in gh-155934 (closed, verified), a `setsockopt` failure there closes the socket and logs "Error on transport creation", but the half-built transport stays registered: `Server._clients` keeps a strong reference so `Server.wait_closed()` never returns, and the entry in `loop._transports` is never cleaned up, so the next connection that gets the same fd number fails with `RuntimeError: File descriptor ... is used by transport ...`. One failed accept effectively wedges the server. The reporter's repro monkeypatches `_set_nodelay` to raise once (simulating what macOS does for a socket the peer reset before `accept()`): the first connection dies, every subsequent connection fails on fd reuse, and `wait_closed()` hangs forever. Control run without the fault passes cleanly.

The real-world trigger is not hypothetical: macOS `setsockopt(TCP_NODELAY)` returns `EINVAL` on a dead accepted socket - the exact bug Cap'n Proto hit in its accept loop (bitcoin-core/libmultiprocess#319, verified). asyncio is shielded on macOS today only because it skips `TCP_NODELAY` for accepted sockets there (gh-148783, open); the pending fix for *that* (gh-148784, open PR) would remove the shield and expose this path to any client that resets before accept.

## Who this bites

- Any asyncio server on a platform where a post-accept `setsockopt` can fail: a single aborted connection - not an attack, just a client that hung up fast - degrades the whole listener into a state where new connections get fd-collision errors and graceful shutdown hangs. The pending gh-148784 fix would put macOS servers directly in this path.
- It's a subtle interaction shape: three individually reasonable changes (accept hardening, nodelay set after registration, nodelay skipped on macOS) compose into a latent wedge that only activates when the third is fixed.

## Limits

- Reporter-run repro only (repo ~77k stars); Linux can't trigger it natively (setsockopt succeeds there even on dead accepted sockets), and macOS is currently masked - so this is a latent, not yet widespread, production bug. I verified the linked issues/PRs but did not run the repro.
- The reporter discloses AI assistance in the investigation; the repro and control were run by the author on current main, and the analysis reads as human-reviewed - treat accordingly.
- Two candidate fixes are proposed (ignore OSError in `_set_nodelay`, or set nodelay before registration); no maintainer has picked one yet.
