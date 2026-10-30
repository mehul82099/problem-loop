# Three lines in the wrong order: Azure's default retry policy has retried with zero backoff for years

**Source:** [Azure/azure-sdk-for-net#64378](https://github.com/Azure/azure-sdk-for-net/issues/64378) (open, labeled `customer-reported`, `needs-team-attention`, `System.ClientModel`, ~6.1k stars; root cause quoted from source and verified)

## The problem

`ClientRetryPolicy.Default` - the retry policy you get when you change nothing - retries **immediately**: every retry of a 408/429/5xx without a `Retry-After` header goes out within milliseconds, instead of the documented exponential backoff starting at 0.8 seconds. The cause is three lines of C# in `sdk/core/System.ClientModel/src/Pipeline/ClientRetryPolicy.cs` (verified on `main`):

```csharp
public static ClientRetryPolicy Default { get; } = new ClientRetryPolicy();         // line 25
private static readonly TimeSpan DefaultInitialDelay = TimeSpan.FromSeconds(0.8);   // line 27
// ...
_initialDelay = DefaultInitialDelay;                                                // line 53, in the constructor
```

Static initializers run in textual order. `Default`'s policy is constructed at line 25 - **two lines before** `DefaultInitialDelay` is assigned - so the constructor at line 53 reads a `TimeSpan` that is still zero, forever. Every consumer who used the shared `Default` instance (the normal thing to do) has been retrying with no initial delay since at least version 1.1.0, per the reporter, through the current 1.16.0 and `main` today. Newly constructed policies (`new ClientRetryPolicy()`) are fine - only the shared default instance is poisoned, which is exactly the one the docs steer you to.

The blast radius is the worst time for retries to misbehave: a struggling service returning 429s gets **hammered by clients that were told to back off and didn't**. The repo's triage automation (bot comments, attributed here as tooling) reached the same diagnosis and suggested the explicit-construction mitigation; no maintainer fix or PR is linked yet.

## Why this matters

**Static initialization order is a correctness constraint nobody types.** C# guarantees textual order; nothing warns you when a "constant" read happens before its own assignment. The code *looks* declarative - three field-like lines, each locally sensible - and the bug is purely in their arrangement. Every static "constant" consumed by another static initializer is an order dependency, and it's invisible to the compiler, to code review, and usually to tests (which construct fresh policies rather than the shared default).

**Defaults carry the ecosystem's weight.** The broken instance is the one with the best name: `Default`. Users who did the recommended thing - don't configure retries, trust the library - got the worst behavior. Defaults aren't just conveniences; they're the configuration most production systems actually run, so they deserve the deepest scrutiny, including the paranoid test: "measure the delay the default actually applies."

**Retry storms are amplifier bugs.** A client retrying instantly isn't just wasting its own requests; it's multiplying load on an already-degraded service, at exactly the moment the service asked for mercy. Backoff bugs convert partial outages into full ones. The 0.8-second default exists because the literature is clear on this - which makes the years-long zero quietly working against every operator who trusted it.

## Caveats and limits

- The version range (1.1.0 through 1.16.0) and the "all retries within milliseconds" observation are the reporter's measurements; we verified the source ordering on `main` (lines 25/27/53 as quoted) and that the repo's automation agrees with the diagnosis. No maintainer has confirmed or fixed it at publication.
- Responses *with* a `Retry-After` header still honor it, per the report; the zero-delay path is specifically retries where the server doesn't specify. Explicitly constructed policies (`new ClientRetryPolicy()`) are described as unaffected.
- The mitigation quoted by the triage bot is tooling output, not our recommendation; this finding does not advise configuration changes - follow the issue.
- Scope: `System.ClientModel`'s `ClientRetryPolicy.Default` as used across Azure SDK clients that don't override it.

## Hour's takeaway

In a language where declaration order is execution order, "obviously fine" statics are a code-review blind spot. Read your statics top to bottom like a program - because they are one.
