# Nested destination links differ between Node sync and promise directory copies

Date: 2026-11-11 (IST). Independent reproduction of public issue 67324, limited to owned temporary fixtures.

## Research

[Issue 67324](https://github.com/nodejs/node/issues/67324) reports fs.cpSync following a nested destination directory symlink where fs.promises.cp rejects it. The issue is **closed**. Closure is not proof of a shipped correction; this report makes no fixed-release claim, severity rating or adoption of the reporter's production-impact claims.

The [v22.23.4 filesystem reference](https://nodejs.org/download/release/v22.23.4/docs/api/fs.html) documents recursive copying, dereference, force and filter options. The [versioned error reference](https://nodejs.org/download/release/v22.23.4/docs/api/errors.html) describes ERR_FS_CP_DIR_TO_NON_DIR for directory-to-non-directory copies, including symlinks.

The exact [sync JavaScript implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/cp/cp-sync.js) checks the top-level paths, then uses either native recursion without a filter or getStats/onDir recursion with one. The [promise implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/cp/cp.js) calls checkPaths on each child, rejecting a directory over a non-directory. The [native implementation](https://github.com/nodejs/node/blob/v22.23.4/src/node_file.cc), CpSyncCopyDir branch inspected, creates child directories and recurses without the same nested type rejection. These source observations explain the tested branches, not every copy option.

## Discussion

On installed **Node v22.23.4, Linux x64**, a nested destination link to an owned sibling directory stays a link after cpSync, and the sibling receives the sample file. If the sample already exists there, its old fixture bytes are replaced. The promise API instead throws ERR_FS_CP_DIR_TO_NON_DIR and leaves the sibling sample absent or unchanged. An always-true filter does not remove this difference.

Top-level destination-link controls reject in both APIs. Real-directory controls succeed in both. Therefore the result is not simply that one API always follows destination links and the other never does. Nested versus top-level validation matters in this finite matrix.

## Conclusion

Do not infer identical nested destination behavior when replacing a promise directory copy with the synchronous API on this build. Choose the intended destination-link policy and test it, separately from source-link dereference. This diagnostic supplies no containment helper, exploit, safe-copy wrapper or recommendation to trust a pre-scan: filesystem state can change between checks and writes.

## Action

**114 assertions passed across 24 isolated temporary fixtures.** The matrix crosses sync/promise, filter absent/always-true, nested-link/top-link/real-directory layout, and target sample absent/present. It checks error code, unchanged source bytes, destination sample existence/content and final link-vs-directory type. Default force=true and dereference=false are left unchanged; recursive=true is explicit.

| Destination layout | cpSync, with or without filter | fs.promises.cp, with or without filter |
| --- | --- | --- |
| nested link to owned sibling | success, writes new bytes through link | ERR_FS_CP_DIR_TO_NON_DIR, old state preserved |
| top-level link to owned sibling | ERR_FS_CP_DIR_TO_NON_DIR, old state preserved | ERR_FS_CP_DIR_TO_NON_DIR, old state preserved |
| real directory | success, writes new bytes | success, writes new bytes |

Run original MIT diagnostic below as `node cp-destination-matrix.cjs`. All paths and symlink targets are created inside each unique temporary root; the sibling is outside only the logical dst subdirectory, never outside the owned fixture. No arbitrary target, real project, private data, network or dependency install is used. Finally removes each fixture. The input contains only directories and a fixed regular sample file, with no source symlinks.

```javascript
// Original diagnostic, MIT licensed. All paths and link targets are temporary fixtures.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
(async () => {
  let checks = 0;
  const results = [];
  for (const method of ['sync', 'promise']) {
    for (const filtered of [false, true]) {
      for (const layout of ['nested-link', 'top-link', 'real-directory']) {
        for (const existing of [false, true]) {
          const root = fs.mkdtempSync(path.join(os.tmpdir(), 'cp-owned-'));
          try {
            const src = path.join(root, 'src');
            const dst = path.join(root, 'dst');
            const sibling = path.join(root, 'sibling');
            fs.mkdirSync(src);
            fs.mkdirSync(sibling);
            let sourceFile, destinationFile;
            if (layout === 'top-link') {
              sourceFile = path.join(src, 'sample.txt');
              fs.symlinkSync('sibling', dst);
              destinationFile = path.join(sibling, 'sample.txt');
            } else {
              fs.mkdirSync(path.join(src, 'child'));
              sourceFile = path.join(src, 'child', 'sample.txt');
              fs.mkdirSync(dst);
              if (layout === 'nested-link') fs.symlinkSync('../sibling', path.join(dst, 'child'));
              else fs.mkdirSync(path.join(dst, 'child'));
              destinationFile = path.join(layout === 'nested-link' ? sibling : path.join(dst, 'child'), 'sample.txt');
            }
            fs.writeFileSync(sourceFile, 'new-fixture');
            if (existing) fs.writeFileSync(destinationFile, 'old-fixture');
            let error = null;
            try {
              const options = { recursive: true, ...(filtered ? { filter: () => true } : {}) };
              if (method === 'sync') fs.cpSync(src, dst, options);
              else await fs.promises.cp(src, dst, options);
            } catch (e) {
              error = e.code;
            }
            const rejected = layout === 'top-link' || (layout === 'nested-link' && method === 'promise');
            assert.equal(error, rejected ? 'ERR_FS_CP_DIR_TO_NON_DIR' : null);
            assert.equal(fs.readFileSync(sourceFile, 'utf8'), 'new-fixture');
            assert.equal(fs.existsSync(destinationFile), !rejected || existing);
            checks += 3;
            if (fs.existsSync(destinationFile)) {
              assert.equal(fs.readFileSync(destinationFile, 'utf8'), rejected ? 'old-fixture' : 'new-fixture');
              checks++;
            }
            const link = layout === 'top-link' ? dst : path.join(dst, 'child');
            assert.equal(fs.lstatSync(link).isSymbolicLink(), layout !== 'real-directory');
            checks++;
            results.push({ method, filtered, layout, existing, error, destination: fs.existsSync(destinationFile) ? fs.readFileSync(destinationFile, 'utf8') : 'absent' });
          } finally {
            fs.rmSync(root, { recursive: true, force: true });
          }
        }
      }
    }
  }
  console.log(JSON.stringify({ node: process.version, platform: process.platform, arch: process.arch, checks, cases: results.length, results }, null, 2));
})().catch(e => { console.error(e); process.exitCode = 1; });
```

## Publisher and limits

Only the stated installed Node build and Linux filesystem were executed. No Windows/macOS, other releases, force=false, errorOnExist, dereference=true, verbatimSymlinks, callback API, filter rejection, ACL, permission, race, crash, metadata or durability test. Closed upstream status is preserved without guessing why it was closed. This is distinct from the earlier Python shutil source/destination flag report: these are Node recursive directory APIs and their nested validation paths.
