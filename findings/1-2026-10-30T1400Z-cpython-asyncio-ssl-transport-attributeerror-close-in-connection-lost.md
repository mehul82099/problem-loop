# Closing an asyncio SSL transport twice doesn't say "already closed" - it detonates the next call with AttributeError

**Source:** [python/cpython#160964](https://github.com/python/cpython/issues/160964) (open, labeled `type-bug`, `topic-asyncio`, `stdlib`, ~77.7k stars; reporter association CONTRIBUTOR; cause verified against `main`)

## The problem

Closing a transport twice should be a no-op. For asyncio's SSL transport, the second `close()` does something worse than nothing: it erases the transport's own guts. From `Lib/asyncio/sslproto.py` on `main`, inside `_SSLProtocolTransport.close()` (verified at lines 106-118):

```python
if not self._closed:
    self._closed = True
    self._ssl_protocol._start_shutdown()
else:
    self._ssl_protocol = None
```

The common pattern that triggers it: a protocol closes its transport in `connection_lost()` - the normal place to clean up. But the transport is already marked closed by then, so the `else` branch runs and sets `_ssl_protocol = None`. From that moment, every subsequent method on the transport explodes with `AttributeError: 'NoneType' object has no attribute ...`: `write()` fails on `_write_appdata`, and `set_protocol()`, `get_write_buffer_size()`, `get_extra_info()` fail the same way. The reporter's repro shows the AttributeError where plain TCP transports handle the identical sequence cleanly.

It gets more systemic than a stray exception: this also breaks `loop.sendfile()` over SSL. If the peer disconnects mid-transfer, the fallback path calls `restore()` -> `set_protocol()` and raises `AttributeError` instead of the expected connection error - so a code path meant to *handle* a disconnect crashes on the same disconnect. A fix is proposed (python/cpython#160069, "Keep the SSL protocol of a closed transport after connection loss", open at publication) but not merged.

## Why this matters

**Idempotency is a contract, not a courtesy.** "Close" is the operation most likely to be called twice - once by the happy path and once by cleanup - which makes the double-close branch the *most* traveled second call in the API. Designing it as "free the internals" instead of "no-op" turns defensive cleanup into a self-inflicted null-pointer. Any API where the second call is the expected one (close, cancel, dispose, release) should treat that call as sacred.

**One class's quirk becomes a protocol for everyone.** Plain TCP transports tolerate the double close; SSL transports don't. Callers write to the *transport interface*, not to `_SSLProtocolTransport`, so code that works perfectly over TCP corrupts its peer the moment TLS is switched on - the worst kind of regression, because it arrives disguised as a security upgrade.

**Error paths are where error paths go to die.** The `sendfile` failure is a nested case: the recovery code for "peer disconnected" is itself broken by "peer disconnected." Cleanup and fallback handlers run exactly when the world is already on fire, and they get the least testing because the happy path never reaches them. The bugs that live there are the ones production meets first.

## Caveats and limits

- The failing call sequence and the `close()` else-branch are verified against `main` (lines 106-118); the exact exception text (`_write_appdata` etc.) and the `sendfile` fallback breakage are the reporter's observations. We did not run the repro.
- A proposed fix exists (PR #160069, which references gh-159875) but is open and unmerged at publication; the issue may consolidate with the earlier report.
- Scope: asyncio's SSL transport on current CPython `main`; plain TCP transports are unaffected per the report.

## Hour's takeaway

Make the second `close()` the boring one. Cleanup code is the most-executed, least-tested path in any API - it deserves the no-op, not the null.
