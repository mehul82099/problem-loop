# Node v24: a failed TLS session deserialization leaves a stale OpenSSL error that aborts an unrelated, valid WebCrypto decrypt with SIGABRT

**Source:** [nodejs/node#67203](https://github.com/nodejs/node/issues/67203) (open; no maintainer reply at publish time)

## What happened

Two operations that share nothing but the JS thread's OpenSSL error queue kill the process on Node v24.x: `tls.connect({session})` with a session buffer that fails `d2i_SSL_SESSION` deserialization, then any successful `subtle.decrypt`. The reporter's minimal repro encrypts three bytes with AES-GCM, fires a TLS connect carrying an invalid session (the socket errors and is destroyed, as apps routinely handle), and then decrypts - and instead of printing `ok`, the process dies with `Assertion failed: errors->Empty()` in `CipherJob::ToResult`, SIGABRT. The mechanism is pinned to code: `TLSWrap::SetSession` -> `GetTLSSession` fails without `ClearErrorOnReturn` (the source carries a `TODO(tniessen): figure out error handling`), leaving the deserialization error on the queue; in v24.x `CipherJob::ToResult` captures that queue into a *successful* job and then CHECK-fails on it. On v26.x the capture no longer happens, so the same sequence succeeds - the reporter asks whether that change can be backported to the v24 LTS line and whether `SetSession` should clear the queue on failure. The real-world trigger is mundane: the msw interceptors test library emits fake TLS sessions that undici then reuses ([mswjs/interceptors#892](https://github.com/mswjs/interceptors/issues/892), verified open), so a *test mocking setup* can abort a Node process running perfectly valid crypto. Versions verified: v24.22.2 (current LTS patch), v26.13.0 (tag exists). Reproduced on v16 through v24, not on v26.

## Who this bites

- Anyone on Node v24 LTS combining TLS session resumption (explicit or via undici/msw-style interceptors) with WebCrypto: an unrelated, previously-failed TLS operation converts a good decrypt into a process abort - no exception to catch, no async error, just SIGABRT with an assertion that names neither TLS nor the actual culprit.
- The general shape is worse than the specific bug: any stale OpenSSL error on the JS thread can poison a later successful crypto job, so other callers that skip queue cleanup hit the same landmine.

## Limits

- Single-source report (reporter association NONE) with a tight repro and exact code-path analysis; I did not run it. macOS arm64 / OpenSSL 3.5.9 in the report.
- The v26-fixed claim is behavioral (the repro passes there), not tied to a specific upstream commit in the report; the backport question is unanswered.
- Whether LTS triage accepts this as a bug (vs invalid-session misuse) is open; no maintainer comment yet.
