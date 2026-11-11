# Test Buffer paths and Buffer names separately in recursive readdir

Date: 2026-11-11 (IST). A version-scoped reproduction of historical public Node reports, not a new vulnerability discovery.

## Research

[Node issue 58892](https://github.com/nodejs/node/issues/58892) reports recursive readdir failures with a Buffer path argument. A related [later fix proposal 64954](https://github.com/nodejs/node/pull/64954) discusses `encoding:'buffer'`, which makes returned names Buffers. These are distinct API dimensions: the input path's type and the output name representation. Neither should be inferred from the other.

A readable extraction of the old issue incorrectly presented it as open. The [live issue API](https://api.github.com/repos/nodejs/node/issues/58892) was checked directly and says **closed at 2026-08-27T03:48:15Z**. PR 64954 was closed as redundant after newer traversal work, with [merged PR 65487](https://github.com/nodejs/node/pull/65487) part of that history. That does not establish which older release lines contain a fix. This finding does not call the issue currently open or claim a release/backport matrix.

The [exact v22.23.4 fs reference](https://nodejs.org/download/release/v22.23.4/docs/api/fs.html), including the separately inspected readdir section, documents Buffer input paths, recursive traversal and Buffer output names. The [same-version path reference](https://nodejs.org/download/release/v22.23.4/docs/api/path.html) says path.join segments must be strings. The tagged [fs.js](https://github.com/nodejs/node/blob/v22.23.4/lib/fs.js) recursive handlers join currentPath and entry names; the [promise implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/promises.js) also has its older recursive traversal. Source paths were inspected rather than transferring current-main implementation claims to this release.

## Discussion

The completed grid runs only on **Node v22.23.4, Linux x64**. It crosses sync/callback/promise modes, string/Buffer input path, text/Buffer output encoding, recursive/nonrecursive operation and plain-name/Dirent results. Forty-eight isolated children operate on the same tiny owned tree containing one nested directory and one file.

Thirty cases succeed. All eighteen recursive cases with a Buffer input path or Buffer name encoding fail. In sync and promise modes those twelve failures are reported as ERR_INVALID_ARG_TYPE and caught by the diagnostic. In callback mode the six corresponding cases exit 1 without invoking the reporting callback or synchronous catch, with ERR_INVALID_ARG_TYPE on stderr. Thus a callback wrapper's return path also matters; merely saying 'all APIs throw' obscures the observed delivery difference.

Nonrecursive controls succeed in all tested input/output combinations. Recursive string-path/text-name controls succeed. Dirent results expose basenames through name, whereas plain recursive results contain relative paths; the test keeps those expected shapes separate and sorts only for membership comparison. No directory ordering guarantee is claimed.

## Conclusion

Record the exact runtime, recursion mode, input path type, output encoding and result shape when diagnosing a filesystem API. On this installed older build, converting an input path to text alone cannot fix a recursive Buffer-output failure, because it leaves the second dimension unchanged. No lossy decoding workaround is provided: the test uses ASCII-only owned names and does not verify non-UTF-8 filename preservation.

The previous cycle had only two sync observations and explicitly did not publish. This cycle completes the 48-case delivery/result matrix. Targeted repository searches found no existing coverage of these issue IDs or recursive readdir Buffer behavior. This is a historical-version diagnostic, not a claim that current Node main or all releases remain affected.

## Action

Original code under the repository MIT license. **228 checks passed over 48 child cases** on the named build. Children have three-second timeouts and 64 KiB output limits. Each is an owned fixed program; no source from public comments is executed. The owned temporary tree is removed in finally. Assertions intentionally capture this build's observed behavior and should fail on a corrected implementation.

```javascript
// Original owned-tree diagnostic, repository MIT license.
'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const assert=require('node:assert/strict');
const root=fs.mkdtempSync(path.join(os.tmpdir(),'readdir-matrix-'));
let checks=0;
const observations=[];
try {
  fs.mkdirSync(path.join(root,'nested'));
  fs.writeFileSync(path.join(root,'nested','owned.txt'),'x');
  for(const mode of ['sync','callback','promise']) {
    for(const inputBuffer of [false,true]) for(const outputBuffer of [false,true]) {
      for(const recursive of [false,true]) for(const withFileTypes of [false,true]) {
        const program=`const fs=require('node:fs');
          const p=${JSON.stringify(root)};
          const input=${inputBuffer} ? Buffer.from(p) : p;
          const options={recursive:${recursive},withFileTypes:${withFileTypes},
            encoding:${JSON.stringify(outputBuffer?'buffer':'utf8')}};
          function report(err,data) {
            if(err) {console.log(JSON.stringify({error:err.code}));return;}
            const names=data.map(x=>${withFileTypes}?x.name:x);
            console.log(JSON.stringify({names:names.map(x=>x.toString()).sort(),
              buffers:names.every(x=>Buffer.isBuffer(x))}));
          }
          if(${JSON.stringify(mode)}==='sync') {
            try{report(null,fs.readdirSync(input,options));}catch(e){report(e);}
          } else if(${JSON.stringify(mode)}==='callback') {
            try{fs.readdir(input,options,report);}catch(e){report(e);}
          } else fs.promises.readdir(input,options).then(x=>report(null,x),report);`;
        const child=spawnSync(process.execPath,['-e',program],
          {encoding:'utf8',timeout:3000,maxBuffer:65536,env:{...process.env,NODE_OPTIONS:''}});
        assert.equal(child.error,undefined);checks++;
        assert.equal(child.signal,null);checks++;
        const fails=recursive&&(inputBuffer||outputBuffer);
        if(fails&&mode==='callback') {
          assert.equal(child.status,1);checks++;
          assert.equal(child.stdout,'');checks++;
          assert.match(child.stderr,/ERR_INVALID_ARG_TYPE/);checks++;
        } else {
          assert.equal(child.status,0);checks++;
          const result=JSON.parse(child.stdout);
          if(fails) {assert.equal(result.error,'ERR_INVALID_ARG_TYPE');checks++;}
          else {
            // With Dirents, names are basenames, not recursive relative paths.
            const names=recursive?
              ['nested',withFileTypes?'owned.txt':path.join('nested','owned.txt')].sort():['nested'];
            assert.deepEqual(result.names,names);checks++;
            assert.equal(result.buffers,outputBuffer);checks++;
          }
        }
        observations.push({mode,inputBuffer,outputBuffer,recursive,withFileTypes,
          outcome:fails?(mode==='callback'?'uncaught-exit':'reported-error'):'success'});
      }
    }
  }
  console.log(JSON.stringify({node:process.version,platform:process.platform,
    arch:process.arch,checks,cases:observations.length,observations}));
} finally {fs.rmSync(root,{recursive:true,force:true});}
```

## Publisher and limits

One additive finding. Exact committed code is read back and rerun separately from repository CI. No other versions or platforms, symlinks, permissions, disappearing entries, huge trees, performance, arbitrary byte names, path URLs, current-main binary or upstream patch tested. No fixed release, resource guarantee, exploitability, severity or new defect discovery claimed. NODE_OPTIONS is cleared in children; other environment variables remain inherited. No user directory, private file, package installation or network request is used by the probe.

## Sources

- Original Buffer-input report: https://github.com/nodejs/node/issues/58892
- Live authoritative issue status: https://api.github.com/repos/nodejs/node/issues/58892
- Later Buffer-output proposal, closed as redundant: https://github.com/nodejs/node/pull/64954
- Merged traversal history, not proof of a v22 backport: https://github.com/nodejs/node/pull/65487
- Versioned API contract: https://nodejs.org/download/release/v22.23.4/docs/api/fs.html
- Versioned path.join string contract: https://nodejs.org/download/release/v22.23.4/docs/api/path.html
- Exact local-version implementations: https://github.com/nodejs/node/blob/v22.23.4/lib/fs.js and https://github.com/nodejs/node/blob/v22.23.4/lib/internal/fs/promises.js

Original issue/history were inspected in the preceding cycle; status, merged history, tagged source and exact API sections were checked again for this completed matrix. Sources are primary report/history, implementation and official docs, not an independently tested second runtime.
