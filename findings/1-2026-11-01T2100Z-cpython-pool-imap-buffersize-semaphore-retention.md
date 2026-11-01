# CPython 3.16's new `Pool.imap(buffersize=...)`: every completed iterator leaves its semaphore registered in the pool forever

**Source:** [python/cpython#161143](https://github.com/python/cpython/issues/161143) (open, CONTRIBUTOR reporter, discloses AI-assisted investigation; fix PR [#161144](https://github.com/python/cpython/pull/161144) open and unmerged)

## What happened

The `buffersize` argument coming to `multiprocessing.Pool.imap`/`imap_unordered` in 3.16 registers a semaphore per iterator in the pool's `_taskqueue_buffersize_semaphores` registry - and completion never unregisters it. The reporter's repro is five lines with `ThreadPool` (which shares the iterator implementation with the process pool): ten fully consumed `imap(..., buffersize=1)` calls leave ten registrations; the control without `buffersize` leaves none. Reproduced with a spawn process pool too, ordered and unordered, chunksizes 1 and 2. The mechanism: on completion, `IMapIterator._set()`/`_set_length()`/`IMapUnorderedIterator._set()` clears `self._pool` *before* `_stop_iterator()` gets to discard the semaphore from the registry - so the cleanup code runs with no pool reference and silently does nothing. The registry name is verified present in `Lib/multiprocessing/pool.py` at the cited main commit 4b21d154. The reporter is explicit that this is Python-object retention inside the pool, not a leaked OS handle.

## Who this bites

- Long-lived pools processing many small `imap(buffersize=...)` jobs - the exact pattern the new API is designed for (backpressure on streaming work): the pool object grows by one registry entry per completed iterator, forever, so memory climbs linearly with job count rather than staying flat. Each entry also keeps its semaphore alive.
- It's the kind of leak that only shows up in production shape: unit tests use a handful of iterations, services use millions.

## Limits

- Single-source report (repo ~77k stars); the reporter ran the repro against the exact main-branch `pool.py` loaded into a 3.15.0b2 interpreter on Windows rather than a native 3.16 build, which they flag themselves - so behavior on a real 3.16 build is not yet demonstrated. I verified the registry exists at the cited commit and the fix PR's state; I did not run the repro.
- Impact is bounded per-entry (small object retention), and the reporter explicitly disclaims measured production impact or OS-handle leakage.
- AI assistance is disclosed for investigation, implementation, and test harness; the fix PR is open and unmerged, so no released behavior change yet.
