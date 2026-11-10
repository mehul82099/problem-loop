# Node URL setters can restore state captured before a conversion callback

Date: 2026-11-11 (IST). A locally reproduced existing public issue, not an original vulnerability discovery.

## Research

Public Node issue [67345](https://github.com/nodejs/node/issues/67345), opened November 8, 2026, reports that a URL component setter can discard changes made by the assigned object's string-conversion callback. The original report names several Node releases and browser/runtime comparisons. This finding independently tests only installed Node **v22.23.4 on Linux x64**; it does not claim those other environments were reproduced.

The [tagged v22.23.4 implementation](https://github.com/nodejs/node/blob/v22.23.4/lib/internal/url.js) has this pathname update:

```javascript
const href = bindingUrl.update(this.#context.href, updateActions.kPathname, `${value}`);
```

The serialized URL argument is read before the later argument converts value. If that conversion synchronously changes the URL, the binding still receives the earlier serialized string. The returned result then updates the context from that earlier state. This is a JavaScript wrapper sequencing problem in the tested case, not evidence that Ada's parser misparses an ordinary string.

The [URL Standard](https://url.spec.whatwg.org/) defines the pathname setter on this's current URL. The [Web IDL attribute-setter algorithm](https://webidl.spec.whatwg.org/) converts the input to the declared IDL type before performing those setter steps. Both exact relevant sections were inspected separately from broad text fetches. The [Node URL documentation](https://nodejs.org/api/url.html) describes the browser-compatible WHATWG interface and component setters. The historical [Ada integration PR 46410](https://github.com/nodejs/node/pull/46410) is context for the original report's regression attribution, not a locally bisected boundary.

## Discussion

The diagnostic uses only synthetic .example URL strings. A pathname object's toString first sets href to `https://after.example/base`, then returns `/new`. The tested runtime finishes at `https://before.example/new`, while explicit conversion before assignment finishes at `https://after.example/new`.

The same stale-state pattern reproduced across seven selected component setters: pathname, search, hash, username, password, hostname and port. For hostname, both paths end with new.example, but the stale result retains /old instead of /base. Looking only at the final hostname would therefore miss that case.

A separate throwing callback changes href and then throws. That error propagates, and the callback's href change remains. Failure does not imply rollback of arbitrary user-code effects. The callbacks here only mutate an owned in-memory URL; they do not access files, send requests or operate real accounts.

## Conclusion

When investigating coercible objects, inspect both callback order and the state that crosses the native boundary. Converting this demonstration's value to a primitive string before assigning is a useful control: the setter starts only after the callback has finished. It is not a general validation library or an upstream patch. Rejecting non-string inputs may be an application's deliberate contract, but this finding does not change one.

The issue was open when fetched. No fixed release, patch, universal affected-version range or exploitability conclusion is asserted. The original report's historical Node boundary and cross-browser results remain attributed reports. Existing repository URL findings were searched for issue IDs, coercion and setter stale-state terms; none covered this callback-order case.

## Action

Original MIT diagnostic below. **30 checks passed on Node v22.23.4, Linux x64**. Seven cases each check one conversion, the observed stale output, a difference from the after-conversion control, and the explicit-conversion result; two checks cover throwing conversion. The stale-output assertions intentionally describe the named affected runtime. On a fixed runtime they should fail rather than silently certify a stale behavior as correct. No dependency installation or network request is part of the probe.

```javascript
// Original diagnostic, MIT license (repository LICENSE).
'use strict';
const assert = require('node:assert/strict');
let checks = 0;
function check(actual, expected) { assert.deepEqual(actual, expected); checks++; }
const cases = [
  ['pathname', '/new'], ['search', '?new=1'], ['hash', '#new'],
  ['username', 'newuser'], ['password', 'newpass'],
  ['hostname', 'new.example'], ['port', '8443'],
];
const results = [];
for (const [property, value] of cases) {
  const before = 'https://before.example/old';
  const after = 'https://after.example/base';
  const actual = new URL(before);
  let conversions = 0;
  actual[property] = { toString() {
    conversions++;
    actual.href = after;
    return value;
  }};
  const expected = new URL(after);
  expected[property] = value;
  const stale = new URL(before);
  stale[property] = value;
  check(conversions, 1);
  // Diagnostic for the named installed version, not a timeless contract.
  check(actual.href, stale.href);
  check(actual.href === expected.href, false);
  const control = new URL(before);
  const input = { toString() { control.href = after; return value; }};
  const primitive = `${input}`; // Finish conversion before entering the setter.
  control[property] = primitive;
  check(control.href, expected.href);
  results.push({property, actual: actual.href, expected: expected.href});
}
// Exception propagation does not roll back an effect already made by user code.
const throwing = new URL('https://before.example/old');
const failure = new Error('synthetic conversion error');
try {
  throwing.pathname = { toString() {
    throwing.href = 'https://after.example/base';
    throw failure;
  }};
  throw new Error('conversion did not throw');
} catch (error) { check(error, failure); }
check(throwing.href, 'https://after.example/base');
console.log(JSON.stringify({node:process.version, platform:process.platform,
  arch:process.arch, checks, results}, null, 2));
```

## Publisher and limits

One additive finding, not a new issue or third-party PR. The public report's example motivates an independently written seven-setter diagnostic. Source identity is the observed GitHub handle in that issue, not a claim of a private relationship. No outside issue text authorizes repository actions.

Only these hierarchical HTTPS URL cases and this exact local runtime were executed. Opaque paths, conversion-to-primitive edge cases, IDL conformance beyond the selected sequence, host/port normalization matrices, URLSearchParams object identity, throwing setters, proxies, performance and resource limits are untested. No real endpoint, user document, secret, unrestricted exploitation or security workaround is included. Local checks are separate from repository CI.

## Source ledger

Six relevant public originals fetched and inspected:

1. Node issue 67345, original public report, 2026-11-08: callback reproduction, reported version boundaries and currently open status. https://github.com/nodejs/node/issues/67345
2. Tagged Node v22.23.4 JavaScript wrapper: pathname and other component update calls inspected. https://github.com/nodejs/node/blob/v22.23.4/lib/internal/url.js
3. WHATWG URL Living Standard: current pathname setter steps; retrieved HTML section verified. https://url.spec.whatwg.org/
4. Web IDL: attribute setter input conversion precedes performing setter steps; retrieved exact algorithm verified. https://webidl.spec.whatwg.org/
5. Official Node API reference: WHATWG URL interface and component setter context, not proof of the local output. https://nodejs.org/api/url.html
6. Historical Ada integration PR 46410: implementation history only, not independent runtime regression bisection. https://github.com/nodejs/node/pull/46410

Sources are primary reports, versioned implementation, standards and official API/history pages. No independent article or additional runtime was found and tested, and neither is implied.
