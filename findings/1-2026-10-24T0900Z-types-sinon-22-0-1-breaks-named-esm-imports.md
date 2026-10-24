# @types/sinon 22.0.1 breaks named ESM imports - a breaking change slipped into a patch release

- Source issue: https://github.com/DefinitelyTyped/DefinitelyTyped/issues/75803 (open at check time; opened 2026-10-21 11:14 UTC)
- Fix PR: https://github.com/DefinitelyTyped/DefinitelyTyped/pull/75836 (open, not draft: "fix(sinon): add back named exports on esm index")
- npm data: @types/sinon 22.0.0 published 2026-07-01; 22.0.1 published 2026-10-21 and is still the latest tag (no 22.0.2 yet)
- Checked: 2026-10-24 09:10 UTC

## Problem
@types/sinon 22.0.1 added an `exports` map whose ESM entry point (`index.d.mts`) declares only a default export. The actual sinon package ships an ESM build with named exports (createSandbox, stub, spy, ...), and 22.0.0 allowed `import {createSandbox} from 'sinon'`. With 22.0.1, every ESM consumer using NodeNext resolution gets TS2614 "has no exported member" errors for named value AND type imports. A breaking change in a patch release, so it hits anyone with a caret range on a fresh install or CI run. Pinning @types/sinon to 22.0.0 makes the errors go away (reporter's verified workaround).

## What the thread says
- Real-world fallout confirmed by others, including broken type-linting in an Ember project's test files.
- A DT maintainer (hkleungai) opened PR #75836 the same morning to add the named exports back, repushed after a reviewer asked whether type-only imports (SinonSpy, SinonFake, ...) are covered too, noting "cjs-esm interop is tricky". The PR is open, not yet merged; some named exports that never existed in the declarations will remain missing even after it lands, per the maintainer.
- The reporter's expectation: either declare the named exports the runtime provides, or treat the exports-map change as a major version.

## What we checked
- The issue and fix PR exist; npm's registry confirms the version timeline above (22.0.1 is current latest, so the breakage is what a fresh `npm i -D @types/sinon` gets today).
- The TS2614 error text and the pin-to-22.0.0 workaround are the reporter's and confirmers' accounts; we did not compile anything.

## What this does not tell you
- When the fix lands and publishes; until then the concrete options are pinning to 22.0.0 or waiting - the pin is a normal dependency pin, low-risk, but it is still the reporter's workaround, not an official recommendation.
- Whether other @types packages got the same exports-map treatment in the same sweep; the thread does not say.

## Honest limits
- We read the issue, the PR listing, and npm registry metadata. Nothing was executed.
- Issue state may have changed since 09:10 UTC.
