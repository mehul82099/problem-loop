# A rejected URL setter receiver can still run input conversion first

Date: 2026-11-11 (IST). Reproduction of public Node issue 67344, not a new vulnerability discovery.

## Research

[Node issue 67344](https://github.com/nodejs/node/issues/67344), opened November 8, 2026, reports that the href setter converts an input object before rejecting an incompatible receiver. This finding independently reproduced that order on **Node v22.23.4, Linux x64**. The original report's other versions and browsers are attributed reports, not local test results.

The [tagged v22.23.4 wrapper](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/url.js) converts value with a template literal before reading this.#context for bindingUrl.update. The [Web IDL attribute setter algorithm](https://webidl.spec.whatwg.org/) instead rejects an invalid interface receiver before converting the input and then performing setter steps. Its exact algorithm was inspected, rather than inferring order from the [URL interface's setter description](https://url.spec.whatwg.org/) alone.

An upstream [proposed fix, PR 67350](https://github.com/nodejs/node/pull/67350), moves the private context access before conversion. Its [diff](https://github.com/nodejs/node/pull/67350.diff) includes a regression assertion that an invalid receiver causes zero conversion calls. The public API was checked because the page extract confusingly included a merge-commit field while saying open: it returns state=open, merged=false and merged_at=null. A non-null merge_commit_sha field alone does not establish that a PR landed. No fixed release is claimed. The older [PR 47339](https://github.com/nodejs/node/pull/47339) is historical implementation context, not a locally bisected regression boundary.

## Discussion

The probe retrieves URL.prototype's actual href setter and calls it with five incompatible receivers: a plain object, an array, an object inheriting URL.prototype without its internal state, null and undefined. On this installed runtime, each case calls the supplied object's toString once, then throws TypeError. Merely receiving TypeError therefore does not prove the input was untouched.

The second input throws a specific owned Error from toString. That exact error escapes for all five invalid receivers, demonstrating that conversion failure can win before the receiver error. These are inert counters and sentinel exceptions only. No external side effect, request, credential, filesystem access or real object from another party is used.

The valid-receiver control converts once and updates href normally. An inherited prototype is not the same as a branded instance: Object.create(URL.prototype) is deliberately invalid here. Do not infer general URL-instance validation rules for other realms, proxies or subclasses from these samples.

## Conclusion

Test rejected calls for callback ordering and exception identity, not only final error class. A rejection can occur after user code has already run. This is not an upstream fix or a recommendation to call setters on arbitrary receivers.

The previous repository finding on issue 67345 concerns a valid URL whose component state is captured before conversion. That full adjacent finding was inspected. This increment concerns the distinct invalid-receiver contract and exception precedence of the href setter, with current proposed-fix verification. It does not repeat the seven-setter state-loss grid or claim that the same fix resolves both reports.

## Action

Original diagnostic under the repository MIT license. **17 checks passed** on the named local Node build: each invalid receiver checks TypeError after successful conversion, one conversion call, and exact propagation of a throwing conversion; two valid-receiver checks confirm ordinary operation. Assertions describe observed affected behavior and should fail after a receiver-first correction. They are a diagnostic, not a timeless conformance oracle.

```javascript
// Original inert diagnostic, MIT license.
'use strict';
const assert = require('node:assert/strict');
const setter = Object.getOwnPropertyDescriptor(URL.prototype, 'href').set;
const receivers = [{}, [], Object.create(URL.prototype), null, undefined];
let checks = 0;
for (const receiver of receivers) {
  let calls = 0;
  assert.throws(() => setter.call(receiver, {toString() {
    calls++; return 'https://example.invalid/';
  }}), TypeError); checks++;
  assert.equal(calls, 1); checks++;
  const failure = new Error('owned conversion sentinel');
  assert.throws(() => setter.call(receiver, {toString() {throw failure;}}),
    error => error === failure); checks++;
}
const valid = new URL('https://before.example/');
let calls = 0;
setter.call(valid, {toString() {calls++;return 'https://after.example/';}});
assert.equal(calls, 1); checks++;
assert.equal(valid.href, 'https://after.example/'); checks++;
console.log(JSON.stringify({node:process.version,checks,status:'passed'}));
```

## Publisher and limits

One additive finding with synthetic owned objects only. No new issue, third-party PR, package install or patch deployment. Local runtime and exact committed code are checked separately from repository CI. No security severity, exploitability, performance, universal affected-version range, fixed release or production impact claim. No other setters, realms, proxies, subclasses or browser runtimes were tested here.

## Sources

- Original issue and reported historical boundary: https://github.com/nodejs/node/issues/67344
- Tagged implementation: https://github.com/nodejs/node/blob/v22.23.4/lib/internal/url.js
- Primary Web IDL attribute-setter ordering: https://webidl.spec.whatwg.org/
- Primary WHATWG URL interface context: https://url.spec.whatwg.org/
- Proposed fix and test, open at inspection: https://github.com/nodejs/node/pull/67350 and https://github.com/nodejs/node/pull/67350.diff
- Public API status cross-check: https://api.github.com/repos/nodejs/node/pulls/67350
- Historical implementation change, not a local bisection: https://github.com/nodejs/node/pull/47339

Current issue/fix records were fetched this cycle; the versioned wrapper and exact standard algorithm sections were inspected in the preceding adjacent investigation and reused. Sources are primary reports, implementation, standards and official history. No independent corroborating runtime is implied.
