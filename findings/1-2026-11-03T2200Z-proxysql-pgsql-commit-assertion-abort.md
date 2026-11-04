# ProxySQL: PgSQL keyword-tracker drift makes a client COMMIT abort the whole process (3.0.11)

**Source:** [sysown/proxysql#6581](https://github.com/sysown/proxysql/issues/6581) - opened 2026-11-03 by chromonav (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

ProxySQL 3.0.11 running the PostgreSQL protocol aborted with signal 6 from `PgSQL_ExplicitTxnStateMgr::commit()`:

```
PgSQL_ExplicitTxnStateMgr.cpp:79:commit(): [WARNING] Received COMMIT command. There is no transaction in progress
proxysql: PgSQL_ExplicitTxnStateMgr.cpp:80 ... Assertion `session->NumActiveTransactions() == 0' failed.
```

The line-79 warning shows the keyword tracker thought no transaction was open; the line-80 assertion shows the session still counted an active backend transaction. The two disagreeing on a client-sent `COMMIT` crashes the release build, disconnecting every client on the instance. The client was an ordinary web app - Frappe over psycopg2 (libpq), autocommit off - with multiplexing on and a single-server hostgroup. Before the crash the instance logged, about every 4-8 minutes, "Unable to parse unknown SET query ... Setting lock_hostgroup ... SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL READ COMMITTED" for that client. The reporter's probable cause (self-marked unconfirmed): a transaction-opening form the tracker does not recognise (psycopg2 sends an implicit `BEGIN` when autocommit is off), or the `lock_hostgroup` path taken after the unparsed `SET SESSION CHARACTERISTICS`. They cross-reference #6417, where the same tracker-versus-backend drift caused `DISCARD ALL` to be rejected rather than a crash, and suggest forwarding the unmatched COMMIT to the backend or resyncing the tracker from `ReadyForQuery` - and not asserting on client-reachable state in a release build.

## Verification (checked during this finding)

- On tag `v3.0.11` (published 2026-08-27), `lib/PgSQL_ExplicitTxnStateMgr.cpp` `commit()` runs exactly the reported sequence: when the tracker's transaction stack is empty it logs `proxy_warning("Received COMMIT command. There is no transaction in progress\n")` and immediately `assert(session->NumActiveTransactions() == 0)` - an abort the client can reach if the two views of transaction state drift.
- `lib/PgSQL_Session.cpp` (~line 6320) contains the "Unable to parse unknown SET query ... Setting lock_hostgroup" warning path the logs show firing repeatedly before the crash, confirming that code path exists and logs as quoted.
- Cross-referenced issue #6417 exists (now closed) with the title "PgSQL: DISCARD ALL trusts the keyword transaction tracker; a stale tracker ..." - matching the same drift theme.
- Crash backtrace symbols (`PgSQL_ExplicitTxnStateMgr::handle_transaction`, `PgSQL_Session::handler`) match real symbols in that codebase.

## Limits

- The crash sequence itself was not reproduced here; it depends on live traffic against a PostgreSQL backend. The mechanism rests on the verified assert being reachable when the tracker and session disagree.
- The root cause of the drift is the reporter's hypothesis (implicit BEGIN vs lock_hostgroup), not established - the issue says "not confirmed".
- Reporter's association is NONE; as of writing the only comment is a CodeRabbit automation plan (tooling, not maintainer triage), so no maintainer position yet.
- Environment specifics (Kubernetes, Patroni/Spilo, TLS, exact pgsql_variables) are the reporter's; whether a simpler config triggers the same drift is unknown.

## Sources

- Issue: <https://github.com/sysown/proxysql/issues/6581>
- PgSQL_ExplicitTxnStateMgr.cpp at v3.0.11: <https://github.com/sysown/proxysql/blob/v3.0.11/lib/PgSQL_ExplicitTxnStateMgr.cpp>
- PgSQL_Session.cpp at v3.0.11: <https://github.com/sysown/proxysql/blob/v3.0.11/lib/PgSQL_Session.cpp>
- Related: <https://github.com/sysown/proxysql/issues/6417>
