# Deno's `URL.parse` throws when you detach it - the static method secretly depends on its receiver, against the URL spec

**Source:** [denoland/deno#37104](https://github.com/denoland/deno/issues/37104) (open; implementation verified at the cited commit; reporter disclosed an LLM-assisted writeup with human-verified reproductions)

## What happened

`URL.parse` is a static method: the [WHATWG URL algorithm](https://url.spec.whatwg.org/#dom-url-parse) constructs a new URL object and has no business touching the function's receiver. In Deno 2.9.8, extracting it breaks it:

```js
const parse = URL.parse;
parse("https://example.com/");   // TypeError: this is not a constructor
URL.parse("https://example.com/"); // works
```

The cause is one line in the runtime, verified at the cited commit: the static `parse` ends with `const self = new this(skipInit)` ([00_url.js#L766](https://github.com/denoland/deno/blob/e7b39ebd55c85aaf6a29290c1f5a99e2e21e09dd/ext/web/00_url.js#L766)). Unbound, `this` is `undefined` and `new undefined()` throws. Bound to a subclass it's arguably worse: `class MyURL extends URL {}`; `MyURL.parse(...)` returns a **MyURL** instance, so the result silently depends on which class you called it through - the spec says it should always be a plain URL. Both directions of the same defect break ordinary JavaScript habits: passing `URL.parse` as a callback (`.map(URL.parse)`, memoization helpers, promise chains) or assigning it to a local.

The repro is six lines and the reporter ran it against 2.9.8 (release tag verified); they disclosed the issue was drafted with Claude/Codex assistance with the reproductions verified by hand. A first-time contributor (author_association NONE, unverified) has already volunteered a fix with a test; no maintainer has responded yet.

## Who this bites

- Anyone writing functional-style JavaScript on Deno: `URL.parse` is precisely the kind of utility that gets passed by reference - as a mapper, a parser callback, a default parameter - and every one of those forms throws on valid input.
- Subclassers of `URL` get the mirror-image bug: spec-noncompliant instances leaking from a static factory.
- Compatibility surface: Node and browsers don't share this failure mode, so code portable elsewhere breaks only on Deno.

## Limits

- The behavior claim is the reporter's six-line repro; I verified the implicated line at the exact cited commit and the v2.9.8 tag, but did not execute the repro (repo ~108k stars).
- Whether `URL.canParse` (the sibling static) has the same receiver dependency is not established in the issue and unexamined here.
- The volunteer's fix is aspirational; no PR exists yet and the team's preferred direction (spec-exact `new URL` vs keeping subclass propagation) is unknown.
