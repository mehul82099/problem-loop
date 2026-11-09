# executescript can cross the transaction boundary before its script fails

Date: 2026-11-10. Mode-specific Python sqlite3 contract, not a new SQLite defect.

## Research

The Python 3.13 and 3.14 sqlite3 references qualify executescript's entry behavior: when autocommit is LEGACY_TRANSACTION_CONTROL and a transaction is pending, it issues an implicit COMMIT first. Other required transaction control belongs to the script. Original developer questions report successful earlier statements surviving later script errors and rollback calls. SQLite's own transaction reference explains implicit versus explicit transactions and notes that ordinary BEGIN transactions do not nest. PyMOTW provides independent commit/rollback background, not authority for modern Python autocommit modes.

Old examples that say executescript always commits must not be generalized across the newer autocommit settings. This probe explicitly chooses each mode rather than relying on a default or treating isolation_level as the only relevant setting.

## Discussion

In legacy mode, insert row 1 in a pending transaction, then call a script containing `BEGIN; INSERT row 2; invalid statement`. Script entry commits row 1 first. BEGIN starts a later transaction; rollback after the error removes row 2, not row 1. Omitting BEGIN from this toy legacy script leaves row 2 outside a persistent explicit transaction as well, so the subsequent rollback removes neither row.

Even the script text `SELECT 1;` can cross this boundary if the calling legacy connection already has pending work. The SELECT is not what commits: executescript's entry behavior is. A read-only-looking script is not proof that invoking it has no transaction effect.

| Explicit mode and script | After failed script, then rollback in this probe |
| --- | --- |
| Legacy, pending prefix, no script BEGIN | Prefix and first successful script insert remain |
| Legacy, pending prefix, script BEGIN | Prefix remains; script insert is rolled back |
| autocommit=False, no transaction commands in script | Prefix and script insert are rolled back together |

A connection context manages relevant pending transactions at exit. It cannot reverse a completed COMMIT. A later BEGIN cannot pull earlier committed work back into its new transaction. Conversely, adding BEGIN indiscriminately to a connection with an open modern transaction can itself fail because BEGIN transactions do not nest. This is not a universal migration template.

## Conclusion

Identify the connection's selected mode, pending state and commit timeline before declaring a multi-statement operation atomic. Keep the script's own transaction commands in that review. Do not split an arbitrary SQL script on semicolons to work around the issue: statements can contain semicolons within their grammar.

The earlier sqlite-context finding already distinguishes transaction handling from connection lifetime, using autocommit=False and explicitly excluding legacy mode. That overlap is acknowledged. This increment tests legacy script entry, failed script prefixes and explicit-mode contrasts. No connection-lifetime novelty or blanket SQLite atomicity failure is claimed.

## Action

Original standard-library-only diagnostic under this repository's MIT license. On actual CPython 3.13.17 and 3.14.9, both linked to SQLite 3.53.1, each run passed 98 checks including a 15-case failed-script grid, read-only script entry and failed-context cases. All databases are private `:memory:` connections, with no application files, network or user data. Connections always close in finally.

The grid uses five prefix lengths and three mode/script combinations. It deliberately does not combine modern autocommit=False with script BEGIN. Rows are inspected on the owning connection before and after rollback. This tests transaction membership and rollback behavior, not disk persistence, crash durability or second-connection isolation. Run without optimization so assertions remain active.

```python
import sqlite3
import platform
import json

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def rows(con):
    return [row[0] for row in con.execute('SELECT id FROM events ORDER BY id')]

def connection(mode):
    con = sqlite3.connect(':memory:', autocommit=mode)
    con.execute('CREATE TABLE events(id INTEGER PRIMARY KEY)')
    con.commit()
    return con

legacy = sqlite3.LEGACY_TRANSACTION_CONTROL
cases = 0
for mode in (legacy, False):
    for prefix in range(1, 6):
        for script_begin in (False, True):
            # BEGIN inside an already-open modern transaction is separately
            # invalid, so do not combine those cases here.
            if mode is False and script_begin:
                continue
            con = connection(mode)
            try:
                con.executemany('INSERT INTO events VALUES (?)', [(n,) for n in range(prefix)])
                check(con.in_transaction)
                statements = ('BEGIN; ' if script_begin else '')
                statements += 'INSERT INTO events VALUES (100); INSERT INTO absent VALUES (999);'
                try:
                    con.executescript(statements)
                except sqlite3.OperationalError:
                    check(True)
                else:
                    raise AssertionError('missing table was accepted')
                check(rows(con) == list(range(prefix)) + [100])
                check(con.in_transaction == (mode is False or script_begin))
                con.rollback()
                expected = [] if mode is False else list(range(prefix)) + ([] if script_begin else [100])
                check(rows(con) == expected)
                check(con.in_transaction == (mode is False))
                cases += 1
            finally:
                con.close()

# Even a read-only script string can cause the legacy entry precommit.
for mode in (legacy, False):
    con = connection(mode)
    try:
        con.execute('INSERT INTO events VALUES (7)')
        con.executescript('SELECT 1;')
        check(con.in_transaction == (mode is False))
        con.rollback()
        check(rows(con) == ([] if mode is False else [7]))
    finally:
        con.close()

# A failed connection context can only roll back what is still pending.
for mode in (legacy, False):
    con = connection(mode)
    try:
        try:
            with con:
                con.execute('INSERT INTO events VALUES (1)')
                con.executescript('INSERT INTO events VALUES (2); INSERT INTO absent VALUES (3);')
        except sqlite3.OperationalError:
            check(True)
        else:
            raise AssertionError('missing table was accepted')
        check(rows(con) == ([] if mode is False else [1, 2]))
    finally:
        con.close()
print(json.dumps({'python': platform.python_version(), 'sqlite': sqlite3.sqlite_version,
                  'checks': checks, 'failure_grid_cases': cases, 'status': 'passed'}))
```

## Publisher checks and limits

- Published bytes are compared with the tested draft; committed code is extracted and rerun on both named builds.
- Only one synthetic missing-table OperationalError, simple INSERTs and the stated modes are tested. No locking, concurrent writers, disk-full errors, conflict-resolution clauses, savepoints, PRAGMAs, triggers, user functions or crash recovery tested.
- The examples are a diagnostic, not production migration advice, a transaction wrapper or a guarantee that arbitrary script failures leave the same state. Determine current state and error policy before reusing a connection.
- Historical questions show a real recurring usage problem, not a current unresolved CPython regression. Independent older isolation-level descriptions are not substituted for current mode-specific official documentation.

## Sources

1. Python 3.13 sqlite3 reference, executescript entry and transaction control: https://docs.python.org/3.13/library/sqlite3.html
2. Python 3.14 sqlite3 reference, same applicable contract: https://docs.python.org/3.14/library/sqlite3.html
3. Original transactional-script question: https://stackoverflow.com/questions/38948407/how-to-executescript-in-sqlite3-from-python-transactionally
4. Original November 2021 multi-script transaction question: https://stackoverflow.com/questions/69990481/python-sqlite3-executescriptsql-script-without-commit-transaction
5. SQLite primary transaction reference, implicit/explicit transaction boundaries and no nested BEGIN: https://www.sqlite.org/lang_transaction.html
6. PyMOTW independent commit/rollback background and script examples: https://pymotw.com/3/sqlite3/
