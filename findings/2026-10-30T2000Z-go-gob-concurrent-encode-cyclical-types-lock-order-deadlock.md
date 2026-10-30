# Two encoders walk into a type cycle: gob's per-type locks deadlock around the loop

**Source:** [golang/go#82740](https://github.com/golang/go/issues/82740) (open, unlabeled; lock-hold-during-recursion verified against `master`; reporter's playground repro linked in the issue)

## The problem

The first time `encoding/gob` encodes a type, it builds and caches an encoding engine for it. For a **cyclic type graph** (T00 has a `*T01`, T01 a `*T02`, ... all the way back to T00), two goroutines that start encoding at different points in the cycle at the same time can deadlock the whole process: `fatal error: all goroutines are asleep - deadlock!`. The reporter hits it "fairly consistently" on an M4 Mac, reproduces it on go.dev/play (link in the issue), and reports the same pattern on production linux/amd64 boxes.

The mechanism is visible in `src/encoding/gob/encode.go` on `master`. `buildEncEngine` (lines 639-654) takes the type's init lock and **holds it while recursively building engines for the types it points at**:

```go
info.encInit.Lock()
defer info.encInit.Unlock()
enc := info.encoder.Load()
if enc == nil {
    ...
    building[info] = true
    enc = compileEnc(ut, building)   // recurses: encOpFor -> getEncEngine -> buildEncEngine
```

The `building` map guards the *same* goroutine against re-entering a type it is already building. It says nothing about a *second* goroutine. Goroutine A locks T00 and walks forward; goroutine B locks T09 and walks forward; each walk accumulates one held lock per type. When A's chain reaches a type B holds and B's chain reaches a type A holds - guaranteed to happen somewhere around a cycle two walkers traverse concurrently - neither can proceed. It is a textbook lock-ordering deadlock, with the lock order determined by which type each goroutine happened to encode first. The reporter's stack trace shows exactly this: one goroutine parked in `sync.Mutex.Lock` inside `buildEncEngine`, deep in a recursion of `compileEnc -> encOpFor -> getEncEngine -> buildEncEngine` frames. Once every engine is cached the race closes, which is why it bites at startup, under load, on first contact with a type graph - the worst possible moment.

## Why this matters

**Lock ordering is a global property decided by local accidents.** Each individual lock in this design is defensible; the deadlock emerges from the *set* of locks being acquired in an order chosen by the data (the type graph) and the scheduler (who starts first). Any system that takes a lock per node while traversing a graph has silently made graph topology its lock hierarchy - and cycles in the graph become cycles in the lock order.

**Recursion under a lock is a debt that compounds per node.** Holding `encInit` across `compileEnc` means the critical section isn't "update one type's cache slot" - it's "arbitrarily much work, plus whatever locks that work wants." Recursive lock-held traversal converts a per-type cache into a distributed transaction over the type graph, with no timeout and no deadlock detection until the runtime declares every goroutine asleep.

**Lazy initialization and concurrency are a generational feud.** The lazy "build the engine on first use" design is exactly what makes the race window exist: a warm cache is safe, a cold one is a minefield, and the minefield is densest at program startup when everything is cold and maximally parallel. Lazy caches need their construction path audited as carefully as their fast path - more so, because tests run warm.

## Caveats and limits

- The lock-during-recursion structure is verified on `master` (encode.go lines 639-654); the deadlock frequency, M4/playground/production reproductions, and go1.27.3 environment are the reporter's. The "two walkers around the cycle" ordering analysis is ours, inferred from the code and the reported stack trace. No maintainer response at publication.
- The race window is the first concurrent encode of types in a cyclic graph; already-cached engines are unaffected. We did not run the repro.
- This finding does not advise workarounds - follow the issue.

## Hour's takeaway

If your critical section can discover more locks to take, your lock graph is your data graph - and data has cycles.
