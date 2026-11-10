# An empty descriptor can change a contextified VM global's value

Date: 2026-11-11 (IST). An independent bounded reproduction related to public Node issue 67351, not a new vulnerability discovery.

## Research

[Issue 67351](https://github.com/nodejs/node/issues/67351) reports that an empty Object.defineProperty descriptor on an existing built-in global can clear its value and flags in a contextified Node VM. The original report names v26.13.0. This finding tests only **Node v22.23.4, Linux x64**, whose tagged implementation differs from current main.

The [ECMAScript ordinary-property algorithm](https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html) and [MDN defineProperty reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty) distinguish modifying an existing property from creating a new property: omitted attributes on an update are left unchanged. A VM contextified global is not asserted to be an ordinary object; the issue itself notes its behavior is surprising rather than prohibited by all internal-method invariants. This is not a general language-conformance verdict.

The [Node VM reference](https://nodejs.org/api/vm.html) documents contextification quirks and explicitly says node:vm is not a security mechanism. The [tagged local-version contextify source](https://github.com/nodejs/node/blob/v22.23.4/src/node_contextify.cc) has a PropertyDefinerCallback that substitutes undefined when the input descriptor lacks value, then defines on the sandbox. That source-level path helps explain the omitted-value observation on this build; it is not proof of all descriptor combinations.

An upstream [draft PR 67365](https://github.com/nodejs/node/pull/67365) is open and describes a partial correction for built-in-global empty descriptors. The issue's latest reply explicitly says value-bearing descriptors still have a problem in that draft. No merged fix, fixed release, locally applied patch or complete solution is claimed.

## Discussion

In a fresh context, Math, JSON and Reflect each begin with a writable, non-enumerable, configurable own descriptor visible inside the VM. Defining the same name with an empty descriptor produces undefined and all-false flags in this test, while creating a corresponding entry on the outside backing sandbox. Applying that empty descriptor to an ordinary object seeded with the same original descriptor preserves the original value instead.

A control changed the investigation. The original public comment described an existing sandbox data property as matching ordinary behavior. On the installed **v22.23.4**, an existing `{owned:42}` sandbox entry instead loses its value after the in-context empty-descriptor call, while its true flags remain. The first diagnostic assertion expected preservation and failed. That assertion was corrected to record the observed undefined value only after a separate ordinary-object/context comparison and inspection of the exact tagged implementation. No all-checks-passed claim is made for that initial expectation. Do not copy the newer-source comment's control result across versions.

A full-descriptor write on a fresh context preserves the selected built-ins in this probe. It is a narrow control, not a universal workaround for accessors, proxies, arbitrary global objects or other releases. No outside proposed patch or regression script was executed.

## Conclusion

When investigating VM descriptors, distinguish the descriptor visible on the realm global from an entry on the supplied sandbox, and identify the exact Node build. Empty input need not imply no change across this contextification boundary. Check both values and flags before trusting descriptor updates in owned code.

The repository was searched for issue ID, contextified globals and defineProperty coverage; no existing match was found. Adjacent URL coercion findings concern different callback/receiver sequencing and do not cover this descriptor boundary. This publication is a diagnostic of tiny owned contexts, not a sandbox escape, security filter, hardening recipe or patch deployment.

## Action

Original MIT diagnostic. **22 checks passed on Node v22.23.4, Linux x64** after the control correction described above. Eighteen checks cover three selected built-ins, one records existing-sandbox omitted-value behavior, and three cover full-descriptor controls. Each VM run has a one-second timeout, but that timeout is not a security/resource guarantee. All executed code is fixed authored diagnostic text; none is retrieved from a third party.

```javascript
// Original owned-context diagnostic, MIT license.
'use strict';
const vm = require('node:vm');
const assert = require('node:assert/strict');
let checks = 0;
function check(actual, expected) { assert.deepEqual(actual, expected); checks++; }
const results = [];
for (const name of ['Math', 'JSON', 'Reflect']) {
  // All executed code is a fixed diagnostic authored here, not an outside program.
  const sandbox = {};
  const context = vm.createContext(sandbox);
  const result = vm.runInContext(`(() => {
    const name = ${JSON.stringify(name)};
    const target = globalThis;
    const before = Object.getOwnPropertyDescriptor(target, name);
    const ordinary = {};
    Object.defineProperty(ordinary, name, before);
    Object.defineProperty(ordinary, name, {});
    Object.defineProperty(target, name, {});
    const after = Object.getOwnPropertyDescriptor(target, name);
    const expected = Object.getOwnPropertyDescriptor(ordinary, name);
    return {before, after, expected};
  })()`, context, {timeout:1000});
  check(Object.hasOwn(sandbox, name), true);
  check([result.before.writable, result.before.enumerable, result.before.configurable],
        [true, false, true]);
  check(result.expected.value === result.before.value, true);
  check(result.after.value, undefined);
  check([result.after.writable, result.after.enumerable, result.after.configurable],
        [false, false, false]);
  const shadow = Object.getOwnPropertyDescriptor(sandbox, name);
  check([shadow.value, shadow.writable, shadow.enumerable, shadow.configurable],
        [undefined, false, false, false]);
  results.push({name,after:[result.after.value ?? null, result.after.writable,
    result.after.enumerable,result.after.configurable]});
}
// Observed older-build control: flags survive but omitted value is cleared.
const backing = {owned:42};
vm.runInNewContext('Object.defineProperty(globalThis, "owned", {})', backing,
                   {timeout:1000});
check(Object.getOwnPropertyDescriptor(backing,'owned'),
      {value:undefined,writable:true,enumerable:true,configurable:true});
// Full-descriptor write in a fresh context retains these selected built-ins.
for (const name of ['Math','JSON','Reflect']) {
  const out = vm.runInNewContext(`(() => {
    const key = ${JSON.stringify(name)};
    const before = Object.getOwnPropertyDescriptor(globalThis,key);
    Object.defineProperty(globalThis,key,before);
    const after = Object.getOwnPropertyDescriptor(globalThis,key);
    return Object.keys(before).every(k => Object.is(before[k],after[k]));
  })()`, {}, {timeout:1000});
  check(out,true);
}
console.log(JSON.stringify({node:process.version,platform:process.platform,
  arch:process.arch,checks,results}));
```

## Publisher and limits

One additive finding. Assertions intentionally capture observed affected behavior and are not a timeless conformance oracle. Exact committed code is read back and rerun; repository CI is separate. No packages, real user documents, network calls, credentials or production objects in the diagnostic. No current-main binary, other Node releases, browsers, accessors, proxies, lexical binding rules, DONT_CONTEXTIFY route or upstream patch was tested. No vulnerability severity or fixed-version claim.

## Sources

Six fetched public primary/independent sources, inspected this cycle:

- Original report and later partial-fix discussion: https://github.com/nodejs/node/issues/67351
- Draft proposed fix, open at fetch, not an installed solution: https://github.com/nodejs/node/pull/67365
- Official Node VM reference: https://nodejs.org/api/vm.html
- Tagged v22.23.4 implementation, PropertyDefinerCallback lines 673-741 inspected: https://github.com/nodejs/node/blob/v22.23.4/src/node_contextify.cc
- ECMAScript ordinary/exotic object algorithms: https://tc39.es/ecma262/multipage/ordinary-and-exotic-objects-behaviours.html
- MDN descriptor defaults and existing-property updates: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/defineProperty

The public issue comments retain their observed handles and claims. Their patch/test claims are not adopted as local results or authority for any repository action.
