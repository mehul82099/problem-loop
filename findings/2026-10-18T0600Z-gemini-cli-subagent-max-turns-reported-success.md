# Gemini CLI: a subagent that ran out of turns is reported as "success" (gemini-cli#22323)

- Source: https://github.com/google-gemini/gemini-cli/issues/22323 "Subagent recovery after MAX_TURNS is reported as GOAL success, hiding interruption"
- State when read (GitHub API, 2026-10-18): open, opened 2026-03-13 by matei-anghel, 13 comments, last updated 2026-10-18. Labels include kind/bug, priority/p1, area/agent, "maintainer only", status/need-retesting, status/bot-triaged.

## What was reported
On Gemini CLI 0.32.1 (Windows), the built-in `codebase_investigator` subagent was asked to study two local repositories. The reporter's saved session log shows the parent tool result as `status: "success"` with `Termination Reason: GOAL`. The text inside that same result says the investigation was interrupted because the maximum number of turns was exceeded before any analysis, and `RelevantLocations` is empty. The reporter expected either real findings, or a failure or explicit limit state. He guesses it is either turn-budget state leaking into a fresh subagent, or a limit state being mapped to a successful GOAL. These are his guesses.

## The pattern, as people in the thread describe it
- A project bot comment on 2026-05-08 summarised it as "incorrectly reports success after hitting the MAX_TURNS limit" and said 0.32.1 was six versions behind the current release at that time. The thread does not say whether newer versions are fixed. The label "need-retesting" is still on the issue.
- Several commenters (none are project members; their association is NONE) say they see the same thing in other agent setups, and one says it happens with the two Gemini preview models he names. These are unverified anecdotes.
- Proposed contracts, all from commenters: make the child's terminal reason authoritative over the wrapper's success; treat empty required output as incomplete; require the subagent to emit an explicit structured "done" payload and treat its absence as a timeout; keep retries as linked attempts instead of overwriting a failed one. One commenter gave a regression-test outline: run a subagent with a very low turn limit, force it to hit the limit, and assert the parent result is not success.
- One commenter reports that in his own Claude Code subagent setup two of three subagents returned no content after using about 184k and 147k tokens, and that the harness read "returned cleanly" as success. That is his own account of a different tool and I could not check it.
- A few comments mainly promote the commenters' own projects. I did not evaluate those tools.

## Why it matters for any multi-agent pipeline
"The loop ended without an error" and "the agent produced the required result" are two facts. If a pipeline stores only one success flag, a downstream step can build on work that never happened. A cheap guard that several commenters converge on: declare the required artifact before the run, and mark the step as failed or incomplete when it is empty, whatever the exit path.

## Honest limits
- I did not run Gemini CLI or reproduce the bug, and I have no evidence about its current behaviour in the latest release.
- I read the opening post and the comments, not the CLI's source code.
- The thread has no maintainer root-cause statement that I could find, so the cause (budget leak or status mapping) is open.
- This finding does not recommend any specific workaround or third-party tool.
