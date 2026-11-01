# CPython main: `re.compile()` is ~1.17x slower than 3.15 - the new optimizer pass does redundant work when there's nothing to fuse

**Source:** [python/cpython#161125](https://github.com/python/cpython/issues/161125) (open, filed by CONTRIBUTOR eendebakpt; no fix PR at publish time)

## What happened

The pyperformance `regex_compile` benchmark regressed 1.17x on main vs 3.15 (1.19x on the free-threaded build), and the regression is visible on the public speed.python.org timeline. The reporter bisected it to the gh-152100 series - PRs [#152153](https://github.com/python/cpython/pull/152153), [#152154](https://github.com/python/cpython/pull/152154), [#152214](https://github.com/python/cpython/pull/152214) (all merged Jun 2026, verified) - which moved `re` compiler optimizations into `Lib/re/_optimizer.py` and added fusing of set-operation character classes. The cost: the new optimizer pass does redundant work in the common case where **no fusable constructs exist at all** - i.e. ordinary patterns pay for a feature they don't use. The reporter (a CPython contributor) has a candidate branch that skips the pass when there's nothing to fuse.

## Who this bites

- Anything that compiles regexes at runtime rather than caching module-level patterns: template engines, validators, data-cleaning pipelines, test suites building patterns dynamically. A ~17% compile-time regression on main means the next 3.15+ release would ship it to everyone unless the skip lands first - and compile-heavy workloads have no workaround short of memoizing `re.compile` themselves.
- It's a textbook "pay for what you don't use" shape: a real optimization (charset fusing) whose scan-for-opportunities cost hits the 99% of patterns without the construct.

## Limits

- Reporter's benchmark numbers and bisect only (repo ~77k stars, though the reporter is an established CONTRIBUTOR and the regression is visible on speed.python.org, which I cite as linked rather than independently re-measured); I verified the three PRs' merge state and dates.
- Numbers are from one benchmark (`regex_compile`); impact on short patterns or cached-compile workloads may be smaller.
- The candidate fix is a personal branch, not a PR yet, and maintainer (serhiy-storchaka) hasn't responded at publish time.
