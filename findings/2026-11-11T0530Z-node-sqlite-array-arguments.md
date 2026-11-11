# An array is not a positional-parameter list in node:sqlite

Date: 2026-11-11 (IST). Independent compatibility diagnostic, not a newly discovered SQLite engine defect.

## Research

[Node issue 67353](https://github.com/nodejs/node/issues/67353), open at inspection, proposes accepting better-sqlite3-style array arguments. The [exact versioned Node documentation](https://nodejs.org/download/release/v22.23.4/docs/api/sqlite.html) instead lists an optional named-parameter object followed by anonymous parameter values. It also documents that setAllowUnknownNamedParameters allows unknown names to be ignored, not converted into positional values.

The pinned [Kysely driver](https://github.com/kysely-org/kysely/blob/67263069a242600e914e8a9e03b118e8cbf4267c/src/dialect/sqlite/sqlite-driver.ts) passes its parameters array directly to all/run. A pinned [MikroORM adapter](https://github.com/mikro-orm/mikro-orm/blob/14737a2349c834dbb39e1dc82bd5adf32fb2531c/packages/sql/src/dialects/sqlite/NodeSqliteDialect.ts) spreads arrays for Node. The [better-sqlite3 binder source](https://github.com/WiseLibs/better-sqlite3/blob/dbc2ea1165fef1f599b9be12faea33fa5e9d7ffb/src/util/binder.cpp) is the issue's comparison point. These are source-level context, not locally executed ORM or better-sqlite3 integration tests.

## Discussion

On the installed **Node v22.23.4, Linux x64**, passing [11,22] as one argument throws ERR_INVALID_STATE by default. Enabling unknown-name tolerance instead silently binds both SQL placeholders as NULL. With ([11],22), tolerance binds 22 to the first anonymous placeholder, leaving the second NULL; it does not flatten the array.

The [exact tagged Node binder](https://github.com/nodejs/node/blob/v22.23.4/src/node_sqlite.cc), lines 1854-1945 inspected, clears previous bindings, treats an initial object other than an ArrayBufferView as named parameters, and advances past that argument before binding anonymous values. The numeric array keys are therefore unknown names, not positional slots. A later array or named object is not a second named-parameter container.

## Conclusion

Unknown-name tolerance is not an array compatibility switch. For a call site whose input contract is one flat list of positional values, spreading that list is the shape exercised successfully here. Do not generalize this to a full better-sqlite3 shim: mixed/nested arrays, object placement, argument-count limits and value-type handling need separate design and tests. This report does not change Node or assert that proposed upstream behavior has landed.

An empty array is an important control: on this runtime it succeeds even without tolerance and leaves both values NULL, just like an empty object. Therefore an adapter should not assume that every unsupported array call will be caught by an exception. This is a binding observation, not a claim of production data loss in any named project.

## Action

**130 counted assertions passed**: 64 operations, each with an exact row/error assertion and a table-row-count assertion, plus two prepared-statement-reuse controls. Successful run() operations additionally assert changes=1. The matrix crosses eight call shapes, tolerance off/on, and all/get/iterate/run. Run uses actual INSERTs into a disposable in-memory table so the stored values are checked, not inferred from a SELECT-only example. All successful results agree across the four methods.

| Arguments | Default | Ignore unknown names |
| --- | --- | --- |
| ([11,22]) | ERR_INVALID_STATE | [NULL,NULL] |
| (...[11,22]) | [11,22] | [11,22] |
| ([]) | [NULL,NULL] | [NULL,NULL] |
| ({}) | [NULL,NULL] | [NULL,NULL] |
| ([11],22) | ERR_INVALID_STATE | [22,NULL] |
| (11,[22]) | ERR_INVALID_ARG_TYPE | ERR_INVALID_ARG_TYPE |
| ({x:11},22), SQL :x then ? | [11,22] | [11,22] |
| (22,{x:11}), SQL :x then ? | ERR_INVALID_ARG_TYPE | ERR_INVALID_ARG_TYPE |

The reuse control binds scalars first, then the ignored array, on the same statement; the second result is [NULL,NULL], not stale [11,22]. Default unknown-key failures report an unknown numeric name; the matrix asserts error codes rather than relying on message wording.

Run the original MIT diagnostic as `node sqlite-array-binding.cjs`. Only node: built-ins and a synthetic :memory: database are used; no files, network, dependencies, credentials or real application data. The runtime emits its SQLite experimental-feature warning.

```javascript
// Original diagnostic, MIT licensed. Only an in-memory synthetic database.
'use strict';
const assert = require('node:assert/strict');
const { DatabaseSync } = require('node:sqlite');
const db = new DatabaseSync(':memory:');
const cases = [
  { name: 'array', args: [[11, 22]], strict: 'ERR_INVALID_STATE', relaxed: [null, null] },
  { name: 'spread-array', args: [...[11, 22]], strict: [11, 22], relaxed: [11, 22] },
  { name: 'empty-array', args: [[]], strict: [null, null], relaxed: [null, null] },
  { name: 'empty-object', args: [{}], strict: [null, null], relaxed: [null, null] },
  { name: 'array-then-scalar', args: [[11], 22], strict: 'ERR_INVALID_STATE', relaxed: [22, null] },
  { name: 'scalar-then-array', args: [11, [22]], strict: 'ERR_INVALID_ARG_TYPE', relaxed: 'ERR_INVALID_ARG_TYPE' },
  { name: 'named-first', named: true, args: [{ x: 11 }, 22], strict: [11, 22], relaxed: [11, 22] },
  { name: 'named-last', named: true, args: [22, { x: 11 }], strict: 'ERR_INVALID_ARG_TYPE', relaxed: 'ERR_INVALID_ARG_TYPE' },
];
let checks = 0;
const results = [];
try {
  db.exec('CREATE TABLE fixture(a, b)');
  for (const c of cases) {
    for (const relaxed of [false, true]) {
      for (const method of ['all', 'get', 'iterate', 'run']) {
        const placeholders = c.named ? ':x, ?' : '?, ?';
        const sql = method === 'run' ? `INSERT INTO fixture VALUES (${placeholders})` : `SELECT ${c.named ? ':x' : '?'} AS a, ? AS b`;
        const statement = db.prepare(sql);
        statement.setAllowUnknownNamedParameters(relaxed);
        db.exec('DELETE FROM fixture');
        const expected = relaxed ? c.relaxed : c.strict;
        let actual;
        try {
          const value = statement[method](...c.args);
          let row;
          if (method === 'run') {
            row = db.prepare('SELECT a, b FROM fixture').get();
            assert.equal(value.changes, 1);
          } else if (method === 'all') row = value[0];
          else if (method === 'iterate') row = [...value][0];
          else row = value;
          actual = [row.a, row.b];
        } catch (e) {
          // Assertion errors are test failures, never expected binding errors.
          if (e.code === 'ERR_ASSERTION') throw e;
          actual = e.code;
        }
        assert.deepEqual(actual, expected, `${c.name}/${relaxed}/${method}`);
        const count = db.prepare('SELECT count(*) AS n FROM fixture').get().n;
        assert.equal(count, method === 'run' && Array.isArray(expected) ? 1 : 0);
        checks += 2;
        results.push({ name: c.name, relaxed, method, actual });
      }
    }
  }
  // Reusing a prepared statement must not preserve the previous bindings.
  const reused = db.prepare('SELECT ? AS a, ? AS b');
  assert.deepEqual([...Object.values(reused.get(11, 22))], [11, 22]);
  reused.setAllowUnknownNamedParameters(true);
  assert.deepEqual([...Object.values(reused.get([11, 22]))], [null, null]);
  checks += 2;
  console.log(JSON.stringify({ node: process.version, platform: process.platform, arch: process.arch, checks, operations: results.length, results }, null, 2));
} finally {
  db.close();
}
```

## Publisher and limits

Only this installed Node build and these call shapes were executed. No Node 24/26, better-sqlite3, Kysely or MikroORM runtime compatibility is claimed. No large-array/stack-limit test, typed-array/BLOB test or general migration shim is included. This is separate from the repository's earlier empty-Uint8Array binding report: the input here is an ordinary JavaScript array and the failure is argument interpretation, not BLOB backing storage.
