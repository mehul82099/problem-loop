# A late opendir option error can escape both callback and promise callers

Date: 2026-11-11 (IST). Independent reproduction of public Node issue 67182, not an original vulnerability discovery.

## Research

[Node issue 67182](https://github.com/nodejs/node/issues/67182), opened November 1, 2026, reports that an invalid opendir bufferSize is validated after the asynchronous directory open. The error then escapes from an internal completion callback instead of reaching the caller's callback or awaited rejection. The original report names other builds; this finding independently tests only **Node v22.23.4, Linux x64**.

The [tagged implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/dir.js) calls `callback(null, new Dir(handle, path, options))` after a successful native open. The Dir constructor validates bufferSize; on failure it closes its handle and throws. That construction occurs before the user's callback is invoked. The synchronous path constructs Dir on the caller's stack, where try/catch can catch it. The source close path was inspected, but no general resource-leak measurement is claimed.

The [fs reference](https://nodejs.org/api/fs.html) describes bufferSize as an internal entry-buffer count, default 32. Its exact opendir section was separately inspected because the broad fetch omitted that part. The [error reference](https://nodejs.org/api/errors.html) distinguishes callback/rejection reporting from exceptions thrown later outside a caller's try/catch. The [process reference](https://nodejs.org/api/process.html) documents default exit on uncaught exceptions and warns against resuming normal operation through an uncaughtException handler. No such handler is installed or recommended here.

The [proposed fix PR 67183](https://github.com/nodejs/node/pull/67183) and [diff](https://github.com/nodejs/node/pull/67183.diff) move validation ahead of the asynchronous open and copy the options. The [public API](https://api.github.com/repos/nodejs/node/pulls/67183) confirmed state=open, merged=false, merged_at=null at inspection. A merge_commit_sha field on an open PR is not a landed-fix signal. No release containing a fix is claimed.

## Discussion

The probe owns one empty temporary directory and starts isolated child processes for each mode and option. Zero, negative one, a fractional number, a numeric string and explicit undefined each produce an unhandled error and exit 1 in both callback and promise modes on this build. The child prints neither the caller's catch marker nor a user callback marker. The synchronous controls catch the corresponding error and exit 0. A valid promise-mode bufferSize of 1 opens and explicitly closes the directory.

An explicit undefined property is tested, not omission of the option. Do not generalize its rejection to the documented default. The test also uses a real accessible owned directory; an earlier filesystem error for a nonexistent or inaccessible path can choose a different branch before Dir construction.

This is a JavaScript error-reporting boundary, not a native assertion abort. Checking only that an operation failed misses whether the caller can handle the failure. Likewise, putting await inside try/catch does not catch an exception thrown later outside the promise's rejection path.

## Conclusion

For this affected build, invalid options on a successful asynchronous open can terminate an otherwise guarded call. The independent child-process checks preserve exit status, signal, stdout markers and the error code family. They do not turn a process-wide exception handler into a repair. Validate any application-owned option policy deliberately and verify the actual runtime/fix status before changing deployed handling; no production wrapper is supplied here.

Targeted repository searches for issue IDs, opendir bufferSize and late Dir construction found no prior finding. This differs from unrelated read/short-read and URL/VM boundaries. The upstream diagnostic and proposed fix are attributed sources; the probe below is independently written.

## Action

Original MIT-licensed bounded diagnostic. **73 checks passed on Node v22.23.4, Linux x64**, across 15 invalid-value/mode children plus one valid child. Each child has a three-second timeout and 64 KiB output cap. The empty owned directory is removed in finally. Assertions intentionally describe affected behavior and should fail once asynchronous errors are delivered correctly. No dependency, existing user directory, untrusted program or network request is used by the diagnostic.

```javascript
// Original bounded diagnostic, repository MIT license.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const dir = fs.mkdtempSync(path.join(os.tmpdir(),'opendir-check-'));
let checks = 0;
function check(a,b) {assert.deepEqual(a,b);checks++;}
const results = [];
try {
  for (const [label,expression] of [['zero','0'],['negative','-1'],
    ['fraction','1.5'],['string',JSON.stringify('1')],['undefined','undefined']]) {
    for (const mode of ['callback','promise','sync']) {
      const program = `const fs=require('node:fs'); const p=${JSON.stringify(dir)};
        const options={bufferSize:${expression}};
        if (${JSON.stringify(mode)}==='sync') {
          try {fs.opendirSync(p,options); console.log('UNEXPECTED_SUCCESS');}
          catch(e) {console.log('CAUGHT:'+e.code);}
        } else if (${JSON.stringify(mode)}==='callback') {
          try {fs.opendir(p,options,(err,d)=>{if(d)d.closeSync();
            console.log('CALLBACK:'+(err?.code??'success'));});}
          catch(e) {console.log('CAUGHT:'+e.code);}
        } else {
          (async()=>{try {const d=await fs.promises.opendir(p,options);
            await d.close();console.log('UNEXPECTED_SUCCESS');}
            catch(e) {console.log('CAUGHT:'+e.code);}})();
        }`;
      const child=spawnSync(process.execPath,['-e',program],
        {encoding:'utf8',timeout:3000,maxBuffer:65536,env:{...process.env,NODE_OPTIONS:''}});
      check(child.error,undefined);
      check(child.signal,null);
      if(mode==='sync') {
        check(child.status,0);
        check(/^CAUGHT:ERR_(OUT_OF_RANGE|INVALID_ARG_TYPE)\n$/.test(child.stdout),true);
      } else {
        check(child.status,1);
        check(child.stdout,'');
        check(/ERR_(OUT_OF_RANGE|INVALID_ARG_TYPE)/.test(child.stderr),true);
      }
      results.push({label,mode,status:child.status});
    }
  }
  const control=spawnSync(process.execPath,['-e',`
    (async()=>{const fs=require('node:fs');
      const d=await fs.promises.opendir(${JSON.stringify(dir)},{bufferSize:1});
      await d.close();console.log('CLOSED');})();`],
    {encoding:'utf8',timeout:3000,maxBuffer:65536,env:{...process.env,NODE_OPTIONS:''}});
  check(control.error,undefined);check(control.status,0);check(control.stdout,'CLOSED\n');
  console.log(JSON.stringify({node:process.version,platform:process.platform,
    arch:process.arch,checks,results}));
} finally {fs.rmSync(dir,{recursive:true,force:true});}
```

## Publisher and limits

One additive finding. Exact committed diagnostic is read back and rerun; repository CI is separate. No other versions, platforms, mutable/getter options, recursive traversal, entry-reading throughput, all invalid values, stress testing or descriptor-leak instrumentation. No fixed release, exploitability, security severity, general resource guarantee or new defect discovery. Clearing NODE_OPTIONS in each child avoids inheriting custom exception behavior; other environment variables remain inherited. All child code is authored here and only opens the owned empty directory.

## Sources

- Original public report: https://github.com/nodejs/node/issues/67182
- Proposed fix and tests: https://github.com/nodejs/node/pull/67183 and https://github.com/nodejs/node/pull/67183.diff
- PR status cross-check: https://api.github.com/repos/nodejs/node/pulls/67183
- Exact local-version JavaScript implementation: https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/dir.js
- Official API contract, exact opendir section inspected: https://nodejs.org/api/fs.html
- Official error propagation guidance: https://nodejs.org/api/errors.html
- Official uncaught-exception exit and recovery limits: https://nodejs.org/api/process.html

Primary report, implementation, proposed test/fix and official documentation were inspected this cycle. No independent second runtime is implied; reported other-version results remain attributed.
