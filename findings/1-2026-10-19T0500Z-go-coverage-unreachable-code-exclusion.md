# Go test coverage: seven years of asking to mark code as "not going to test" (golang/go#31280)

- Source: https://github.com/golang/go/issues/31280 "testing: exclude statically unreachable code in test coverage". Opened 2019-04-05, open, 54 comments, 45 reactions on the post, labels NeedsDecision and FeatureRequest, milestone "Unplanned" (by the GitHub API on 2026-10-19). Last comment 2026-10-19.
- Third-party tool a commenter points to: https://github.com/dave/courtney (not archived, last push 2026-03-30 by the API, 179 stars).
- Go's coverage docs: https://go.dev/doc/build-cover (read 2026-10-19; I searched it for "exclude", "ignore" and "unreachable" and found only package-selection exclusions, not a way to exclude lines).

## The request
The reporter has a constant `trace = false` and code like `if trace { fmt.Println(...) }`. Go's coverage report shows that code as not covered. He asks for statically unreachable code to be shown as "not tracked". The thread has since widened to a general request: a way to mark lines or regions as excluded from coverage.

## The argument
- A Go contributor (bcmills, 2019) says flagging unreachable code is a useful signal, whether the compiler can tell is an implementation detail, and that 100% coverage is usually not an appropriate goal for Go projects. He asks why it matters.
- The reporter and others reply that they do not aim at 100%, but that the HTML report shows red lines they must mentally discard. A commenter wants a summary like "92% covered, 6% uncovered, 2% marked unreachable".
- 2020: a long exchange. One commenter asks why Go projects need different coverage metrics than Java or Python, and the contributor says they do not, but that Go's compiler catches more than Python's without analyzers. The commenter replies that static type checking is not testing. Commenters also say that impossible-case error handling (for example `if err != nil { return err }` around a call that cannot fail in practice) is the main thing they want to exclude. These are their stated experiences.
- Reactions on the thread favor the requesters: several of their comments have 20 to 60 reactions, and the contributor's replies have up to 25. I counted reactions only from the API, and they do not decide anything.
- A user points to the third-party tool courtney, which they say they use for this. I did not run it and do not endorse it.
- 2026-03-07: a user says empty functions count as 0% covered and asks if they could count as 100%. 2026-10-19: another user asks for a comment directive like `// go:coverage ignore start` ... `end`, and says JavaScript's Vitest and PHP's PHPUnit have something similar. I did not check either tool.

## What can be said
- After seven years, the issue is open with milestone "Unplanned" and the NeedsDecision label, and I found no Go team comment that accepts or rejects it after the early ones. I did not read every comment, and the first 100 are all that the API returned in one page. All of the 54 were returned, so that part is complete, but I summarized selected ones.
- In the meantime, the options users describe are manual: build tags, third-party tools, or reading the report with the known false negatives in mind.
- I did not find a separate Go proposal for a coverage-ignore directive in one search, which is not proof there is none.

## Honest limits
- I did not test Go's coverage tool, courtney, or any workaround.
- Claims about other languages' tools are commenters'.
- "Unplanned" and "NeedsDecision" come from the issue's metadata at the time of reading and can change.
