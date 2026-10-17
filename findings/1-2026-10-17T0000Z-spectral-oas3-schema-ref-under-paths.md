# Spectral: `oas3-schema` rejects `$ref` under paths since spectral-rulesets 1.19.0

- Source: https://github.com/stoplightio/spectral/issues/2655 (open, opened 2024-07-17, last activity 2026-10-16, labelled `duplicate`, 7 reactions)
- Suspected cause, named by the reporter and confirmed to exist through the GitHub API: https://github.com/stoplightio/spectral/pull/2574 "improve {oas2,oas3}-valid-schema rule" (merged 2024-05-03)
- Fix attempts, state checked through the API on 2026-10-17:
  - https://github.com/stoplightio/spectral/pull/2844 (by fluz, opened 2025-08-20): **closed, not merged**
  - https://github.com/stoplightio/spectral/pull/3090 (by fluz, opened 2026-10-16): **open**, "allow external path item references and update OAS 3.1 schema to 2026-08-03"

## The problem
Reporter jstuckey says that after spectral-rulesets 1.19.0, a `$ref` that points to another file now makes the `oas3-schema` rule fail, while 1.18.1 and earlier passed. Two shapes are reported:

1. `$ref` placed on an operation (`paths./foos.get.$ref`). Error: `Property "$ref" is not expected to be here`. Reporter notes that the OpenAPI 3.0 spec lets a path item object carry `$ref` but not an operation object, so this shape is arguably invalid, though Redoc and GitLab accepted it.
2. `$ref` placed on the path item itself (`paths./greetings.$ref`), which the spec allows. pedrosmr reports this fails on an OpenAPI 3.1 document with `property must not have unevaluated properties`. Several others (xaben, evgeniy-solaris, fab-mindflow, Theshedman) say they hit the same thing.

## What the thread says (claims attributed, nothing re-run here)
- afmhenry points to a line in the #2574 merge commit and believes the issue would have been avoided if a resolved option there had been set differently. I only verified that the commit exists and is the squash of #2574. I did not read the diff.
- Commenters say the rule is otherwise useful and they do not want to disable it. Some bundle their document first.
- fluz posted a fix in 2025, it was closed without merging, and a new pull request with schema validation changes was opened on 2026-10-16. The thread has no maintainer reply in the comments I read.

## Why this is worth noting
The issue is over two years old, still gets new comments, and the two cases are different. Case 1 looks like a spec question (operation-level `$ref` is not valid OpenAPI 3.0). Case 2 looks like a real bug for valid documents. Anyone hitting the error should check which shape their document uses before pinning an older version.

## Honest limits
- I did not run Spectral or reproduce either error. The error text and version claims come from the issue and its commenters.
- I did not confirm which exact release first contained #2574, so "since 1.19.0" is the reporter's claim.
- The label `duplicate` implies another issue exists, but I did not find or check which one.
- Whether #3090 fixes both cases is not established. Its title mentions path item references and an OAS 3.1 schema update, and I did not read the code.
