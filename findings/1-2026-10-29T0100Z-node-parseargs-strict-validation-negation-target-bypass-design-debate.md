# Strict mode with a hole: Node's parseArgs validates the token you declared, not the option you actually set

- Source issue: https://github.com/nodejs/node/issues/67085 (open; opened 2026-10-28, active maintainer discussion)
- Project: nodejs/node (~123k stars)
- Checked: 2026-10-29 01:45 UTC

## Problem
Node's `util.parseArgs` with `strict: true` and `allowNegative: true` has a validation gap around explicitly declared negative options. Two demonstrated shapes: (1) declare `logfile` as `type: 'string'` AND `'no-logfile'` as `type: 'boolean'`, pass `--logfile out.log --no-logfile`, and the result is `{ logfile: false }` - the string option silently became a boolean, because the negation path skips the destination option's type validation; (2) more starkly, declare only `'no-warnings': { type: 'boolean' }` (never declaring `warnings` at all), pass `--no-warnings`, and strict mode happily returns `{ warnings: false }` for an option that was never defined - while *without* the explicit `no-*` declaration, the same flag correctly throws ERR_PARSE_ARGS_UNKNOWN_OPTION. Declaring the negative form turns strict mode off for that flag. Reproduced on v22.16.0, v24.22.1, and current `main`.

## Why it is interesting
- The bug is a validation-scope mistake, not a parsing mistake: strict mode validates the declared token (`no-logfile`, a legal boolean) rather than the effective outcome (setting undeclared `warnings`, or clobbering string `logfile` with a boolean). Validation that checks the wrong object is the parser equivalent of authenticating the messenger instead of the message.
- The thread is a live, civil design debate worth watching: a Node member's first read is "you're not supposed to declare no-* options at all; declare positive ones and let allowNegative negate them." The reporter counters with the original design discussion where negative declarations were shown for short aliases and considered appropriate - then narrows the claim: regardless of the recommended pattern, *strict validation shouldn't pass what it never validated*. The member's pragmatic guidance: keep strict by declaring positive options only, and handle exotic negation yourself after parsing. Unresolved at check time.
- "Strict" is a security-adjacent promise for CLI tools: it exists so that misspelled or unexpected flags fail loudly instead of silently shaping behavior. A documented escape hatch that accepts undeclared options undermines the guarantee without saying so.
- Nice example of a report that survives pushback by shrinking to its defensible core: the design-pattern argument is debatable; the "strict mode accepted an option that was never declared" fact is not.

## Honest limits
- Open design question, not a confirmed bug per maintainers at check time; a member's position is that the triggering pattern is out-of-scope API usage.
- The reporter mentions a patch changing behavior; no PR linked in the thread yet.
- Impact requires explicitly declaring negative options, which the maintainers consider non-idiomatic; plain allowNegative usage is unaffected.
- Thread state may move quickly.
