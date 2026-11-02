# Go's race detector crashes with SIGSEGV - no report at all - when the race fires inside a channel timer's `sendTime` on the scheduler stack

**Source:** [golang/go#82771](https://github.com/golang/go/issues/82771) (open; no maintainer reply at publish time)

## What happened

A reporter chasing a race whose read side runs in `time.sendTime` (the function the Go scheduler runs to fire a channel timer) found that the race detector never reports it: instead of the expected `WARNING: DATA RACE`, the test binary dies with `signal: segmentation fault (core dumped)`, exit 139, no output, no report file, 5 of 5 runs on go1.27.3, 1.26.10 and 1.26.9 (tags verified). The minimal repro is a `time.Ticker` kept alive by a receiving goroutine plus an unsynchronized `time.Local = time.UTC` write - `sendTime` calls `time.Now`, which reads `time.Local`, a genuine race. The gdb autopsy explains the crash: TSan detects the race while the scheduler runs the timer on the **system stack**, calls back into Go (`racecallbackthunk`) to symbolize the stack, and the signal raised inside that path hits `sigtrampgo` on a thread with no `g`, so the process goes straight through `badsignal` and dies - the stack frames from `ReportRace` down through `time.sendTime`, `runtime.(*timer).unlockAndRun`, `findRunnable` and `mcall` are all identified in the report. So the failure is not the race but the reporting machinery: symbolization is invoked from a context where a fault cannot be recovered into a report.

## Who this bites

- Anyone running `go test -race` over timer-heavy code: when the detector is needed most - a race inside runtime timer machinery, exactly the kind nobody can eyeball - it produces a silent SIGSEGV that looks like a flaky crash or a bad environment, with zero indication that a race was even found. Teams will disable or re-run tests instead of finding the bug.
- CI triage especially: exit 139 with no output is indistinguishable from infrastructure failure, so real races get swallowed as "rerun the job".

## Limits

- Single-source report (reporter association NONE) with a minimal repro, 5/5 determinism across three releases, and a coherent gdb stack analysis; I did not run it, and the "no g on the thread" mechanism is the reporter's reading of the trace.
- Linux/amd64 only in the report; other platforms untested. No maintainer triage, milestone, or fix at publish time.
- The race used in the repro (`time.Local` write vs `time.Now` read) is itself real but contrived; what matters is the reporting path, and whether other scheduler-context callbacks crash the same way is open.
