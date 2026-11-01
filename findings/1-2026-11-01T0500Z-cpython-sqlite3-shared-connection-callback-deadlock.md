# `sqlite3` deadlocks the whole process when threads share a connection that has any Python callback - a GIL-vs-mutex lock inversion in a fully supported configuration

**Source:** [python/cpython#161065](https://github.com/python/cpython/issues/161065) (open, filed by CPython core dev gpshead with fix PR [#161066](https://github.com/python/cpython/pull/161066) open from the same author; prior-art issue verified)

## What happened

Share an `sqlite3` connection between threads the documented way - `check_same_thread=False`, SQLite in serialized mode, `sqlite3.threadsafety == 3` - and register **any** Python callback (a `create_function` scalar, an aggregate, collation, authorizer, progress handler or trace callback). Two threads executing queries then deadlock the entire process, usually within a second, and the hang cannot be interrupted with Ctrl-C.

The inversion, as diagnosed in the report: SQLite invokes the Python callback from inside `sqlite3_step()` **while holding the connection mutex**, and the callback blocks in `PyGILState_Ensure()` waiting for the GIL. Meanwhile the other thread **holds the GIL** and blocks on that same connection mutex in an SQLite call the module makes without releasing the GIL - e.g. `sqlite3_column_int64()` in `_pysqlite_fetch_one_row()`, `sqlite3_bind_*()`, `sqlite3_errmsg()`, `sqlite3_set_authorizer()`. Thread A: mutex held, wants GIL. Thread B: GIL held, wants mutex. Nobody moves, ever, and the GIL-holder can't even process signals.

The reporter's repro is under 25 lines and needs no timing luck beyond a second. This exact lock-inversion class was fixed once before in the same module - [#86864](https://github.com/python/cpython/issues/86864) (closed, verified), the same deadlock in `Connection.close()`, fixed by releasing the GIL around `sqlite3_close_v2()`. This report shows the fix was applied to one call site while the pattern persists across the fetch, bind, error-message and authorizer paths. Reporter and fix author are the same core developer (gpshead, MEMBER, verified).

## Who this bites

- Any multi-threaded Python service sharing one SQLite connection with user-defined SQL functions - a common pattern for read-heavy in-memory caches, queue backends, and applications registering custom collation for i18n sorting. The failure is a silent total freeze, not an exception: health checks that exec Python in-process hang with it.
- The deadlock needs only two threads and ordinary queries; the registered callback turns every concurrent read into a dice roll against the fetch path's mutex acquisition.
- Signal-proof hangs defeat watchdogs: Ctrl-C doesn't work, so recovery is kill -9 and whatever that does to on-disk state mid-write.

## Limits

- The deadlock and the lock-order diagnosis are the reporter's (a core dev, high-confidence but single-source); I verified the issue/PR/prior-fix topology and the MEMBER association, but did not run the repro (repo ~77k stars).
- The fix PR is open and unmerged; which call sites it covers versus leaves is review-stage information.
- Scope is the stdlib `sqlite3` module; third-party drivers (apsw, etc.) have their own locking and are unexamined.
