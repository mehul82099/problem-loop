# Package exports arrays are not missing-file fallbacks

Date: 2026-11-11 (IST). Independent diagnostic of a longstanding documented-resolution pitfall, not a newly discovered Node defect.

## Research

[Issue 58600](https://github.com/nodejs/node/issues/58600) records the misconception that exports arrays can choose a built file when a development file is absent. [New documentation PR 67393](https://github.com/nodejs/node/pull/67393) revisits this; it was open and unmerged at inspection. An [earlier documentation PR 65240](https://github.com/nodejs/node/pull/65240) explicitly includes null among skipped array entries. These are proposals and discussion, not proof of shipped behavior.

The [versioned packages reference](https://nodejs.org/download/release/v22.23.4/docs/api/packages.html) documents exports and conditions. The [versioned ESM reference](https://nodejs.org/download/release/v22.23.4/docs/api/esm.html) describes PACKAGE_TARGET_RESOLVE and says import.meta.resolve no longer throws for file URLs that point at absent local files. An [independent demonstration repository](https://github.com/Boshen/test-esm-exports-array) describes the missing-file distinction; its bundler comparisons were not rerun here.

## Discussion

An invalid package target such as ../outside.cjs can be skipped. A valid ./missing.cjs target is selected even when it does not exist. Loading that selection fails rather than trying ./ok.cjs. Returning a URL from import.meta.resolve is not evidence that the module can be loaded.

A second detail needs care: null inside an array is skipped on the tested runtime, but can reset a previously saved invalid-target error. Reversing [invalid, null] to [null, invalid] changes the final error. The [exact tagged implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/modules/esm/resolve.js), lines 495-523 inspected, explicitly sets lastException to null and continues. The ESM reference pseudocode instead says to return a resolved result after checking undefined and does not spell out that null-continuation branch. We therefore ground these null results in the implementation and actual execution, not a claim that the pseudocode literally matches them. The fresh PR's short skip list also omits null; it should not substitute for runtime tests.

## Conclusion

Do not use an exports array as a source/build file-existence switch. Select the intended artifact explicitly, for example with a build-generated package manifest or intentional export conditions, and test that packaging choice in its intended runtime. This diagnostic does not implement or validate either packaging strategy.

## Action

Executed on **Node v22.23.4, Linux x64**: **52 expected-result checks passed**, using 13 arrays and four operations in separate child processes. Each child exit and absence of spawn errors were checked too. All fixtures are generated in a unique temporary directory and deleted in finally. No package install, network, private project, credentials or existing package edits are used. Run the original MIT-licensed diagnostic below as `node exports-array.cjs`.

In the result table, PNE means ERR_PACKAGE_PATH_NOT_EXPORTED; IPT means ERR_INVALID_PACKAGE_TARGET; MNF means MODULE_NOT_FOUND; EMNF means ERR_MODULE_NOT_FOUND. A cjs filename in a resolve column means the path/URL ends in that filename. Loaded fixture-ok means the actual module ran. Full expected paths/URLs are asserted in the diagnostic, not just basenames.

| Case | require | require.resolve | import | import.meta.resolve |
| --- | --- | --- | --- | --- |
| missing-first | MNF | MNF | EMNF | missing.cjs |
| invalid-first | fixture-ok | ok.cjs | fixture-ok | ok.cjs |
| unmatched-condition | fixture-ok | ok.cjs | fixture-ok | ok.cjs |
| null-first | fixture-ok | ok.cjs | fixture-ok | ok.cjs |
| empty-nested-first | fixture-ok | ok.cjs | fixture-ok | ok.cjs |
| empty | PNE | PNE | PNE | PNE |
| null-only | PNE | PNE | PNE | PNE |
| unmatched-only | PNE | PNE | PNE | PNE |
| all-invalid | IPT | IPT | IPT | IPT |
| existing-first | fixture-ok | ok.cjs | fixture-ok | ok.cjs |
| invalid-then-missing | MNF | MNF | EMNF | missing.cjs |
| invalid-then-null | PNE | PNE | PNE | PNE |
| null-then-invalid | IPT | IPT | IPT | IPT |

```javascript
// Original diagnostic, MIT licensed. Uses only disposable local fixtures.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = fs.mkdtempSync(path.join(os.tmpdir(), 'exports-array-'));
const cases = [
  ['missing-first', ['./missing.cjs', './ok.cjs'], 'missing'],
  ['invalid-first', ['../outside.cjs', './ok.cjs'], 'ok'],
  ['unmatched-condition', [{ browser: './missing.cjs' }, './ok.cjs'], 'ok'],
  ['null-first', [null, './ok.cjs'], 'ok'],
  ['empty-nested-first', [[], './ok.cjs'], 'ok'],
  ['empty', [], 'blocked'],
  ['null-only', [null], 'blocked'],
  ['unmatched-only', [{ browser: './ok.cjs' }], 'blocked'],
  ['all-invalid', ['../x.cjs', '../y.cjs'], 'invalid'],
  ['existing-first', ['./ok.cjs', './missing.cjs'], 'ok'],
  ['invalid-then-missing', ['../outside.cjs', './missing.cjs', './ok.cjs'], 'missing'],
  ['invalid-then-null', ['../outside.cjs', null], 'blocked'],
  ['null-then-invalid', [null, '../outside.cjs'], 'invalid'],
];
const operations = {
  require: `const value=require('fixture'); console.log(JSON.stringify({value}));`,
  requireResolve: `const value=require.resolve('fixture'); console.log(JSON.stringify({value}));`,
  import: `const value=(await import('fixture')).default; console.log(JSON.stringify({value}));`,
  importResolve: `const value=import.meta.resolve('fixture'); console.log(JSON.stringify({value}));`,
};
const results = [];
let checks = 0;
try {
  const pkg = path.join(root, 'node_modules', 'fixture');
  fs.mkdirSync(pkg, { recursive: true });
  fs.writeFileSync(path.join(pkg, 'ok.cjs'), `module.exports='fixture-ok';\n`);
  for (const [name, target, kind] of cases) {
    fs.writeFileSync(path.join(pkg, 'package.json'), JSON.stringify({ name: 'fixture', exports: target }));
    for (const [op, code] of Object.entries(operations)) {
      const script = `try { ${code} } catch(e) {console.log(JSON.stringify({error:e.code}));}`;
      const args = op.startsWith('import') ? ['--input-type=module', '-e', script] : ['-e', script];
      const child = spawnSync(process.execPath, args, { cwd: root, encoding: 'utf8', timeout: 3000 });
      assert.equal(child.error, undefined);
      assert.equal(child.status, 0);
      const actual = JSON.parse(child.stdout);
      let expected;
      if (kind === 'blocked') expected = { error: 'ERR_PACKAGE_PATH_NOT_EXPORTED' };
      else if (kind === 'invalid') expected = { error: 'ERR_INVALID_PACKAGE_TARGET' };
      else if (kind === 'missing' && op !== 'importResolve') expected = { error: op === 'import' ? 'ERR_MODULE_NOT_FOUND' : 'MODULE_NOT_FOUND' };
      else if (op === 'require' || op === 'import') expected = { value: 'fixture-ok' };
      else if (op === 'requireResolve') expected = { value: path.join(pkg, 'ok.cjs') };
      else expected = { value: require('node:url').pathToFileURL(path.join(pkg, kind === 'missing' ? 'missing.cjs' : 'ok.cjs')).href };
      assert.deepEqual(actual, expected, `${name}/${op}`);
      checks++;
      results.push({ name, op, result: actual.error || (actual.value === 'fixture-ok' ? actual.value : path.basename(actual.value)) });
    }
  }
  console.log(JSON.stringify({ node: process.version, platform: process.platform, arch: process.arch, checks, results }, null, 2));
} finally {
  fs.rmSync(root, { recursive: true, force: true });
}
```

## Publisher and limits

This is a dependency-free diagnostic, not a Node patch or upstream endorsement. Only this installed Node build and the listed exports cases were executed. Imports maps, custom loaders, custom conditions, other Node versions and bundlers are not covered. Child processes have a 3-second timeout; failures throw rather than being counted as successful checks. No general claim about all fallback arrays follows from this finite matrix.
