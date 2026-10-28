# Bun's HTTP/2 event streams arrive on a 500 ms tick - but only for the oldest connections

- Source issue: https://github.com/oven-sh/bun/issues/47159 (open; opened 2026-10-28)
- Project: oven-sh/bun (~96k stars)
- Checked: 2026-10-28 09:12 UTC

## Problem
A `Bun.serve` server with `http2: true` holding many open event streams (one ReadableStream response each - the classic server-sent-events shape) delivers a published event to most streams within milliseconds, but to a contiguous block of the OLDEST open streams 1 to 3 seconds late, in multiples of roughly 500 ms. Reproduced on Bun 1.4.2 and today's canary. The reproduction detail that matters: the client must run in a separate process so the server's event loop is idle between events - with an in-process client, the bug hides. The reporter measures delivery latency per stream and finds the slow set is always a contiguous index range at the oldest end, with delays quantized to ~500 ms steps.

## Why it is interesting
- Quantized delay is a fingerprint, and this one points at a timer, not a queue. Random congestion smears latency; "multiples of about 500 ms, contiguous oldest block" is what a periodic flush or wakeup fallback looks like when the prompt path (write now) was missed for some streams and the slow path (a ~500 ms tick) rescues them. Whatever the mechanism, the measurement shape names it before anyone opens the source.
- "Only reproduces with an idle event loop" inverts the usual intuition. Busy servers flush constantly as a side effect of doing work, so the bug needs a quiet server to show itself - meaning production servers with low traffic (exactly the ones running a handful of long-lived SSE connections) are the most exposed, while load tests with busy loops see nothing. A latency bug that hides under load and appears under calm.
- The affected set being the OLDEST streams is the second clue. Something iterates or expires in stream-creation order, and the tail of that order gets the slow path. Long-lived connections - the whole point of event streams - are precisely the ones punished.
- Reporting craft: knobs for stream count and per-connection limits, p50/max delivery stats, the slow set printed as an index range, delays rounded to expose the quantization, and the explicit note that an in-process client could NOT reproduce - saving every maintainer from a failed first attempt.

## Honest limits
- Single reporter, no maintainer response at check time (~45 minutes after filing).
- The timer-fallback mechanism is inference from the quantized 500 ms delays; Bun has not confirmed a cause.
- Scope as reported: Bun.serve with http2: true on Linux; HTTP/1 SSE and other platforms not covered by the report.
- Issue state may have changed since 09:12 UTC.
