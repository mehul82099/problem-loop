# Setting one level, clearing ten thousand caches: CPython's `Logger.setLevel()` is quadratic in the number of loggers

**Source:** [python/cpython#160936](https://github.com/python/cpython/issues/160936) (open, labeled `type-bug` / `performance` / `stdlib`, ~77.7k stars; benchmarked repro, maintainer pushback included)

## The problem

Every `Logger.setLevel()` and `logging.disable()` call runs `Manager._clear_cache()`, which walks the **entire** `loggerDict` and clears each logger's `isEnabledFor` cache - including loggers that never cached anything. Configure N loggers one by one and the total work is O(N^2). The reporter's benchmark on Python 3.14.7: 0.23 s at 2,000 loggers, 0.89 s at 4,000, 4.4 s at 8,000 - each doubling of logger count roughly quadruples the time.

The code confirms it. In `Lib/logging/__init__.py` on `main` (verified): `_clear_cache` (line 1467) iterates `self.loggerDict.values()` and clears every `Logger._cache`, plus the root's. It's called from `Logger.setLevel` (line 1516) and `logging.disable` (line 2268). One logger's level change invalidates everyone's memoized `isEnabledFor` results, even though the level that changed affects only loggers that inherit from it.

The interesting part is the response: a CPython member (aisk, MEMBER, commenting on the issue) pushed back - thousands of loggers configured individually isn't common real-world usage, and `setLevel` isn't called often - asking whether the reporter hit a genuine performance problem or a synthetic one. As of publication the question is open: the issue carries `type-bug` and `performance` labels, but the "is this worth optimizing" debate is unresolved.

## Why this matters

**Global invalidation is the default because it's easy, and it's a tax on scale.** Clearing every cache when one input changes is correct - invalidation is never wrong about staleness - but it makes every mutation pay for the whole population. That's invisible until someone runs an app with a logger per plugin, per connection, per module - which is precisely how large Python codebases end up structured. The operations most likely to be "not called very often" are the ones whose cost nobody profiles until a test suite or an app boot takes four seconds of pure cache clearing.

**Hierarchy-aware invalidation is the road not taken.** Python's loggers form a tree: changing `app.db`'s level can only affect loggers inheriting from it. A targeted clear (the changed logger plus its descendants, or only loggers that actually cached) keeps correctness and drops the quadratic factor. The reporter's framing invites exactly that; the maintainer's question invites the counter-argument that complexity in hot stdlib paths needs real-world justification. Both are right; that's what makes it a good issue.

**"Not a common case" is a load-bearing assumption about users you don't see.** The stdlib's users include every framework and plugin system built on it, each multiplying logger counts in ways the original design didn't anticipate. The measured quadratic is a fact; whether it matters is a bet about how people actually configure logging. Bugs like this are where those bets get audited - cheaply, in public, with a benchmark anyone can rerun.

## Caveats and limits

- The benchmark numbers are the reporter's (a contributor) on Python 3.14.7; we verified the code path on `main` (`_clear_cache` and its two call sites) but did not rerun the timing. A maintainer has questioned whether the pattern occurs in real code - treat the practical impact as unproven, the algorithmic fact as verified.
- No fix PR exists yet; the discussion is one maintainer comment asking for motivation.
- `logging.disable()` is a global switch, so clearing everything there is defensible; the quadratic pain is specifically per-logger `setLevel` in a loop.
- This finding reports the issue and the debate. It does not advise patching your logging setup; follow the issue.

## Hour's takeaway

"Clear all caches" is the null hypothesis of invalidation - always correct, never free. When the cost of a mutation scales with the size of the whole population rather than the size of the change, the system works fine until the day someone uses it as designed, at scale.
