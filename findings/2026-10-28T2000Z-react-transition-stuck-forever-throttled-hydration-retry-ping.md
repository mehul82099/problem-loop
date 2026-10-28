# The transition that never commits: a throttled hydration retry dropped at exactly the wrong moment

- Source issue: https://github.com/react/react/issues/38029 (open; opened 2026-10-28)
- Project: react/react (~252k stars)
- Checked: 2026-10-28 20:35 UTC

## Problem
In React 19.3.0-canary (as shipped in Next.js 16.4.2, and reproducible on `main` at dc9aed3), a transition that updates a server-rendered `<Suspense>` (or `<Activity>`) boundary that hasn't hydrated yet can get stuck forever: all data loads, but the transition never commits. Real-world shape: a modal opened by a router transition never appears. The reporter didn't just report it - they wrote the failing test that belongs in React's own `ReactDOMServerPartialHydration` suite, and walked the exact scheduler deadlock: (1) the transition waits for the boundary to hydrate; (2) when the first lazy component loads, React starts a hydration retry, but retry commits are throttled, so it's held back; (3) during that throttle window the second lazy component loads and pings the transition, so React drops the held-back retry and renders the transition instead; (4) the boundary still isn't hydrated, so the render re-suspends - and the dropped retry was the only thing that would ever hydrate it. Nothing is scheduled anymore. Fails in stable, experimental, and www-modern builds, dev and production. One extra twist: the test only fails *outside* `act()`, because `act` turns off the retry throttle - the standard test harness hides the bug by design.

## Why it is interesting
- A liveness bug, not a correctness bug: nothing crashes, nothing errors, the UI just silently never updates. The worst class of scheduler bug, because there is no stack trace to report and the app "works" until one specific interleaving of promise resolutions.
- The deadlock is a pure scheduling race with a four-step interlock: throttle window + dropped retry + re-suspension + nothing left in the queue. Each step is locally reasonable (throttle commits, drop stale work, re-suspend on unhydrated boundaries); the composition is a lost wakeup. This is the concurrent-rendering equivalent of the classic multithreading bug, now expressed in lane/priority language.
- The `act()` detail is a quiet indictment of test infrastructure: React's own test helper disables the very mechanism (retry throttling) needed to reproduce the bug, so the suite is structurally blind to this class. The reporter had to deliberately step outside the sanctioned harness to prove the failure.
- It's a user-visible production bug in a shipped canary line (via Next.js) with a crisp reproducer - filed by an external contributor, association NONE, not a React team member. High-signal community reports into core scheduler internals are rare.

## Honest limits
- Filed ~2 hours before check; no React team response or confirmation at check time.
- Affects canary/experimental lines as shipped through Next.js 16.4.2; whether stable React 19.x releases are affected is unverified (the failing test runs against `main`).
- The four-step mechanism is the reporter's analysis, not yet maintainer-confirmed.
- No workaround is documented in the thread.
