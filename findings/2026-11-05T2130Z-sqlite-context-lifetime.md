# sqlite3 connection contexts manage transactions, not connection lifetime

Date: 2026-11-06. A documented lifecycle distinction, not a new SQLite defect.

## Research

The [Python 3.14 sqlite3 reference](https://docs.python.org/3.14/library/sqlite3.html) says the connection context manager commits or rolls back open transactions and does not close the connection. Its transaction behavior depends on the selected autocommit mode. The [contextlib reference](https://docs.python.org/3.14/library/contextlib.html) documents closing as calling close on exit, including when the body raises.

[Documentation issue 34580](https://bugs.python.org/issue34580) records this confusion and the addition of explicit close calls to examples. Two independent community questions, [October 2024](https://stackoverflow.com/questions/79047539/python-not-automatically-closing-a-connection-to-sqlite3-after-exiting-with-stat) and [January 2024](https://stackoverflow.com/questions/77827942/connection-and-cursor-still-usable-outside-with-block), show callers expecting file-like cleanup. A [2026 independent article](https://anthonyrisinger.com/sqlite-close/) discusses the same distinction. These establish a recurring usage problem, not a regression or measured application leak.

## Discussion

There are two separate boundaries: whether changes commit or roll back, and when the connection closes. With autocommit=False, a successful connection context commits the current transaction, then a new transaction opens. A raised exception rolls back the current transaction. Neither outcome closes the connection.

Wrapping only in closing is not a replacement for transaction management: closing calls close, and a pending transaction with autocommit=False rolls back on close. If both behaviors are wanted, put closing outside an inner connection context. The inner context finishes the transaction before the outer context closes the connection. Explicit commit/rollback plus try/finally is another option; this finding does not provide a universal database wrapper.

## Conclusion

Choose transaction policy and resource lifetime separately. Do not generalize file context-manager behavior to every object supporting with. This probe explicitly selects autocommit=False instead of relying on the default. It does not test legacy transaction mode, autocommit=True writes, nested connection contexts, commit failures, pools, concurrency or descriptor counts.

## Action

Run the following original MIT-licensed probe with Python 3.12 or newer. It creates only one owned database in a temporary directory, uses independent reader connections to check persistence, and closes every connection. No application databases are opened.

```python
import json
import platform
import sqlite3
from contextlib import closing
from pathlib import Path
from tempfile import TemporaryDirectory

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def closed(con):
    try:
        con.execute('SELECT 1')
    except sqlite3.ProgrammingError:
        return True
    return False

def rows(path):
    with closing(sqlite3.connect(path, autocommit=True)) as reader:
        return reader.execute('SELECT value FROM sample ORDER BY value').fetchall()

with TemporaryDirectory() as temp:
    path = Path(temp) / 'owned.sqlite'
    with closing(sqlite3.connect(path, autocommit=True)) as setup:
        setup.execute('CREATE TABLE sample(value INTEGER)')

    con = sqlite3.connect(path, autocommit=False)
    try:
        with con:
            con.execute('INSERT INTO sample VALUES (1)')
        check(con.execute('SELECT value FROM sample').fetchall() == [(1,)])
        check(con.in_transaction)  # False autocommit opens the next transaction.
        try:
            with con:
                con.execute('INSERT INTO sample VALUES (2)')
                raise RuntimeError('controlled rollback')
        except RuntimeError:
            pass
        check(con.execute('SELECT value FROM sample').fetchall() == [(1,)])
        check(con.execute('SELECT 1').fetchone() == (1,))
    finally:
        con.close()
    check(closed(con))
    check(rows(path) == [(1,)])

    # closing owns lifetime, but does not commit the pending insert.
    with closing(sqlite3.connect(path, autocommit=False)) as con:
        con.execute('INSERT INTO sample VALUES (3)')
    check(closed(con))
    check(rows(path) == [(1,)])

    # Outer lifetime management; inner transaction management.
    with closing(sqlite3.connect(path, autocommit=False)) as con:
        with con:
            con.execute('INSERT INTO sample VALUES (4)')
    check(closed(con))
    check(rows(path) == [(1,), (4,)])

    try:
        with closing(sqlite3.connect(path, autocommit=False)) as con:
            with con:
                con.execute('INSERT INTO sample VALUES (5)')
                raise RuntimeError('controlled nested rollback')
    except RuntimeError:
        pass
    check(closed(con))
    check(rows(path) == [(1,), (4,)])

print(json.dumps({'python': platform.python_version(),
                  'sqlite': sqlite3.sqlite_version,
                  'checks': checks, 'result': 'passed'}))
```

## Validation

The probe passed 12 checks on CPython 3.13.17 and 3.14.9, both linked to SQLite 3.53.1, in this Linux environment. It verifies connection usability after success and rollback, explicit close, rollback when only closing is used, and commit/rollback plus close with the two context managers. These are observed builds, not a claim that every Python/SQLite combination was tested. Repository CI is separate.

## Publisher

One evidence-backed finding with an executable probe. No runtime library changes, package installation, production migration or performance claim.
