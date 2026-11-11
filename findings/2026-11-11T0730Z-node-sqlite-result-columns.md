# Result columns, returned rows, and SQL keyword guesses are different questions

Date: 2026-11-11 (IST). Independent Node SQLite diagnostic motivated by reader feature request 67352.

## Research

[Issue 67352](https://github.com/nodejs/node/issues/67352) asks for a cheap reader flag instead of constructing column metadata. It also warns that SQL text heuristics can misclassify statements. This report tests that correctness question, not the issue's performance numbers or proposed API.

The [v22.23.4 Node reference](https://nodejs.org/download/release/v22.23.4/docs/api/sqlite.html) defines columns() as metadata about returned columns. The [SQLite column-count contract](https://sqlite.org/c3ref/column_count.html) explicitly distinguishes a positive column count from the presence of any returned rows. [SQLite RETURNING](https://sqlite.org/lang_returning.html) can make INSERT/UPDATE/DELETE return rows; the [WITH reference](https://sqlite.org/lang_with.html) permits common table expressions in front of writes, not just SELECTs.

The pinned [MikroORM adapter source](https://github.com/mikro-orm/mikro-orm/blob/14737a2349c834dbb39e1dc82bd5adf32fb2531c/packages/sql/src/dialects/sqlite/NodeSqliteDialect.ts) contains a reader decision based on an initial select/pragma/explain/with keyword or any occurrence of the word returning. The diagnostic evaluates that same two-regex decision rule against synthetic SQL. It does not run MikroORM or establish the effect of a wrong flag on that package's actual execution paths.

## Discussion

On **Node v22.23.4, Linux x64**, six of thirteen cases disagree with that rule: commented SELECT and standalone VALUES have columns but the rule says false; WITH INSERT, a string literal containing returning, a comment containing returning, and a write PRAGMA have no columns but the rule says true. The rule is not a SQL parser.

A SELECT filtered to zero rows and an UPDATE ... RETURNING matching no rows both still have one result column. Looking at rows.length would incorrectly conflate an empty result with a statement that has no result set. Conversely, INSERT ... RETURNING changes data and returns columns, so row-producing does not mean read-only. EXPLAIN INSERT returns an instruction result set without performing the INSERT in this fixture.

## Conclusion

For the tested Node API, columns().length > 0 answers whether a prepared statement has result columns without executing it. Do not substitute a keyword test, an empty-result check or a read-only assumption for that question. This is not a performance recommendation: no benchmark, allocation comparison or cache strategy was measured here, and no proposed reader API is claimed shipped.

## Action

**79 assertions passed over 13 isolated in-memory fixtures**: six per case, plus an exact mismatch-count assertion. Each fixture prepares one SQL statement, checks column count and the decision rule, checks the table before execution, executes with all(), checks actual rows, confirms metadata stays the same, and checks the table after execution. The pre-execution table check does not prove absence of every possible side effect; it checks the one synthetic table only.

| Case | Columns | Actual rows | Keyword rule | Mismatch |
| --- | --- | --- | --- | --- |
| select | 1 | 1 | true | no |
| empty-select | 1 | 0 | true | no |
| commented-select | 1 | 1 | false | yes |
| values | 1 | 1 | false | yes |
| insert | 0 | 0 | false | no |
| with-insert | 0 | 0 | true | yes |
| literal-returning | 0 | 0 | true | yes |
| comment-returning | 0 | 0 | true | yes |
| insert-returning | 1 | 1 | true | no |
| empty-update-returning | 1 | 0 | true | no |
| pragma-read | 1 | 1 | true | no |
| pragma-write | 0 | 0 | true | yes |
| explain-write | 8 | 9 | true | no |

Run the original MIT diagnostic as `node sqlite-result-columns.cjs`. It uses built-ins, a separate :memory: database per case, fixed synthetic SQL and no private data, files, package installs or network. Node emits its experimental SQLite warning.

```javascript
// Original diagnostic, MIT licensed. Synthetic in-memory fixtures only.
'use strict';
const assert = require('node:assert/strict');
const { DatabaseSync } = require('node:sqlite');
const cases = [
  ['select', 'SELECT v FROM fixture', 1, 1, true, 1],
  ['empty-select', 'SELECT v FROM fixture WHERE 0', 1, 0, true, 1],
  ['commented-select', '/* prefix */ SELECT v FROM fixture', 1, 1, false, 1],
  ['values', 'VALUES(7)', 1, 1, false, 1],
  ['insert', 'INSERT INTO fixture VALUES (2)', 0, 0, false, 2],
  ['with-insert', 'WITH c(x) AS (VALUES(2)) INSERT INTO fixture SELECT x FROM c', 0, 0, true, 2],
  ['literal-returning', "INSERT INTO fixture VALUES ('returning')", 0, 0, true, 2],
  ['comment-returning', 'INSERT INTO fixture VALUES (2) /* returning */', 0, 0, true, 2],
  ['insert-returning', 'INSERT INTO fixture VALUES (2) RETURNING v', 1, 1, true, 2],
  ['empty-update-returning', 'UPDATE fixture SET v=2 WHERE 0 RETURNING v', 1, 0, true, 1],
  ['pragma-read', 'PRAGMA user_version', 1, 1, true, 1],
  ['pragma-write', 'PRAGMA user_version=5', 0, 0, true, 1],
  ['explain-write', 'EXPLAIN INSERT INTO fixture VALUES (2)', 8, null, true, 1],
];
const results = [];
let checks = 0;
for (const [name, sql, count, rowCount, expectedHeuristic, tableCount] of cases) {
  const db = new DatabaseSync(':memory:');
  try {
    db.exec('CREATE TABLE fixture(v); INSERT INTO fixture VALUES (1)');
    const statement = db.prepare(sql);
    // Equivalent decision rule to the pinned adapter's two-regex reader test.
    const heuristic = /^\s*(select|pragma|explain|with)/i.test(sql) || /\breturning\b/i.test(sql);
    const before = statement.columns();
    assert.equal(before.length, count);
    assert.equal(heuristic, expectedHeuristic);
    assert.equal(db.prepare('SELECT count(*) AS n FROM fixture').get().n, 1);
    const rows = statement.all();
    if (rowCount === null) assert.ok(rows.length > 0);
    else assert.equal(rows.length, rowCount);
    assert.deepEqual(statement.columns(), before);
    assert.equal(db.prepare('SELECT count(*) AS n FROM fixture').get().n, tableCount);
    checks += 6;
    results.push({ name, columns: before.length, returnedRows: rows.length, heuristic, hasResultColumns: before.length > 0, mismatch: heuristic !== (before.length > 0) });
  } finally {
    db.close();
  }
}
assert.equal(results.filter(x => x.mismatch).length, 6);
checks++;
console.log(JSON.stringify({ node: process.version, platform: process.platform, arch: process.arch, checks, cases: results.length, results }, null, 2));
```

## Publisher and limits

Only this installed Node build and these statements were run. Actual ORM behavior, better-sqlite3, other Node versions, virtual tables, schema changes/reprepare, triggers, custom functions, multiple SQL statements and performance are outside the test. The sampled EXPLAIN row count is observational; the code asserts only that it is positive because exact instruction counts can vary. This is separate from the earlier array-binding diagnostic: arguments are not being adapted here; the question is result-set classification.
