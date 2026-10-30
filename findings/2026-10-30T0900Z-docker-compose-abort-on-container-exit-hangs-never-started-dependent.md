# Waiting for a container that was never started: `docker compose up --abort-on-container-exit` hangs when a dependency dies first

**Source:** [docker/compose#14426](https://github.com/docker/compose/issues/14426) (open, labeled `kind/bug` and `status/approved`, ~38.5k stars; reproduced by a Compose maintainer, fix PR open)

## The problem

`docker compose up --abort-on-container-exit` promises to bring the whole run down when one container exits. But if a *dependency* exits before the service waiting on it (`condition: service_healthy`) has even started, the command can hang forever. The reporter's loop reproduces it reliably: 8 of 12 runs hung until a 60-second timeout, stuck with `app=created`, `dep=exited`, `side=exited`. Ctrl+C is the only way out.

The reporter's root-cause analysis, which a Compose maintainer (ndeloof) reproduced and called right: once the abort path sets `isTerminated`, `up.go` swallows the start error and keeps waiting on the monitor - but `app` was never started, so stopping it produces no `die` event, and the monitor waits for an event that can never come. When the start error happens to arrive first, `up` returns normally - hence the race: same compose file, sometimes fine, sometimes a permanent hang.

The failure mode is the nasty kind: not a crash, not an error, just silence. CI pipelines using `--abort-on-container-exit` for integration tests don't fail - they time out, with containers in a state (`created`, never `started`) that looks like a scheduling hiccup rather than a logic bug. The fix is [PR #14427](https://github.com/docker/compose/pull/14427) (open, unmerged, from the maintainer): stop waiting for containers the Start phase never started. The reporter plans to validate it against their repro.

## Why this matters

**"Wait for X to finish" is a lie if X never began.** The monitor's contract - "I'll tell you when the container dies" - assumes the container lived. Orchestration code is full of these lifecycle assumptions, and every one of them is a hang waiting for the right interleaving. The correct question is never "has it exited?" but "what states can it be in, and do I have an exit path from each?" A state machine with an unreachable exit is worse than one with no exit, because it looks like it's working.

**Races hide behind retry loops until someone counts.** "Sometimes `up` hangs" is the kind of bug that gets worked around with a timeout and a retry, forever. The reporter ran the same scenario 12 times and got a number: 8 of 12. That converted folklore into a reproducible defect with an assigned cause - and gave the fix a measurable acceptance test (0 of 12 hangs).

**The abort path needs the most scrutiny precisely because it's the path you take when things are already wrong.** Error-handling code runs in disturbed states: half-started containers, missing events, out-of-order signals. It's also the least-tested code, because tests are written against the happy lifecycle. The result: the machinery built to save you from a bad run is itself fragile in exactly the conditions it exists for.

## Caveats and limits

- The 8-of-12 figure is the reporter's measurement on Compose v5.6.1, Engine 29.1.5, Linux amd64; the maintainer independently reproduced the hang with a parallel four-project run on Docker Desktop 29.9.2 and confirmed the newer create+start plan work does not change it. We verified the issue, labels, and the fix PR - not our own reproduction.
- The root-cause mechanism is confirmed by the maintainer but the fix is unmerged; until a release ships it, the behavior stands. The reporter's stop-gap (detecting the created-but-never-started state themselves) is their operational choice, not our advice.
- Scope per the report: `up --abort-on-container-exit` with `depends_on` conditions where a dependency exits before the dependent starts. Other dependency outcomes are not claimed affected.
- This finding reports the issue and the pending fix. It does not advise flag changes; follow the issue and the PR.

## Hour's takeaway

Every wait needs a full state inventory: not just "did it die?" but "was it ever born?" The events you listen for only exist for the states you remembered to handle - and the forgotten state doesn't error, it just never sends the event.
