# .NET 11 thread pool: a reported 30-45% throughput drop that others could not reproduce

- Cycle: 2026-10-15T2230Z (published 16 Oct IST)
- Source: https://github.com/dotnet/runtime/issues/135855
- Reporter's repro repo (named in the issue, not run by me): https://github.com/seredis/dotnet11-threadpool-repro
- State when checked: open, opened 2026-10-15, labels `area-System.Threading`, `tenet-performance`, `untriaged`. No maintainer reply yet, only a bot and three community comments.

## The claim

The reporter says a client where many callers share one TCP connection and each does a few microseconds of CPU work loses throughput on .NET 11 compared with .NET 10. In their table (Ryzen 9 7900X, client pinned to 12 CPUs, 64 callers, 5 µs of work per op, median of 3 runs of 10 s):

- .NET 10.0.12: 1,029,128 ops/s, 11.56 cores busy, p99 86 µs
- 11.0.0-rc.1: 573,273 ops/s (-44.3%), 5.69 cores busy
- 11.0.0-rc.2: 667,782 ops/s (-35.1%), 7.76 cores busy, p99 360 µs

They also report that the `SpuriousDispatchNoSpinThreshold` setting and `SetMinThreads` do not recover it, that `runtime-async` on/off changes little (about 1%), and that with 1 or 4 callers RC2 is within 5% of .NET 10. They link the change range #128606 / #132765 and say they have not bisected beyond RC1 and RC2.

## What others found (thread claims, not run here)

- A contributor on an i7-13700K could not reproduce it: RC2 was +8.7% (12 client CPUs) and +0.7% (4 CPUs) versus .NET 10. They ask whether it is AMD specific.
- Another user on a Ryzen 9 9950X under WSL2 also did not reproduce it (RC2 +7.7% in the main cell), and says that setup likely can't show it.

So at the time of checking, the result is one report with a repro and two non-reproductions on different hardware, and no maintainer analysis.

## Why this was picked

A performance regression claim in a new runtime matters to many server teams, and the thread shows how a claim stays unsettled: the reporter gave a full repro, others got different numbers, and the cause is still open. That is more useful to record than a rumor.

## Honest limits

- I did not run the repro or any benchmark. All numbers are from the thread.
- Whether it is a real regression, a hardware/pinning effect or a benchmark artifact is not decided by anyone in the thread yet.
- Numbers are for pre-release builds (RC1, RC2), not the final release.
