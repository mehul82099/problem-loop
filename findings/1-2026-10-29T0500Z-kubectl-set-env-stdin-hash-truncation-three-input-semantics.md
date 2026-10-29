# Same tool, same value, two answers: kubectl's stdin env parser eats everything after '#'

- Source issue: https://github.com/kubernetes/kubernetes/issues/143548 (open, needs-triage; opened 2026-10-29)
- Project: kubernetes/kubernetes (~129k stars)
- Checked: 2026-10-29 05:50 UTC

## Problem
`kubectl set env -e -` (reading KEY=VALUE lines from stdin) silently drops everything after the first `#` on each line. `TOKEN=ab#cd` becomes `ab`; `DB_URL=postgres://u:p@h/db#x` loses the fragment. No error, no warning. The same value passed as a direct argument (`kubectl set env deploy TOKEN=ab#cd`) is stored intact - and a third path, `kubectl create configmap --from-env-file`, treats only line-leading `#` as a comment and keeps `#` inside values. Three input paths, three different semantics for the same data. The cause is pinned exactly: `readEnv` in `staging/src/k8s.io/kubectl/pkg/cmd/set/env/env_parse.go` truncates at `strings.Index(envSpec, "#")`. The documented example for the stdin form makes it worse: the help text suggests `env | grep RAILS_ | kubectl set env -e - deployment/registry`, and `env` output has no comments - a `#` there is always data, often inside a password or URL.

## Why it is interesting
- This is how secrets get mangled in production: not by crypto bugs or leaks, but by a comment-stripping heuristic that can't tell data from annotation. Connection strings, tokens, and generated passwords all legitimately contain `#`. A deployment pipeline that renders env through stdin will happily deploy truncated credentials - and fail somewhere far away, hours later, as an auth error with no obvious cause.
- Inconsistency inside one tool is its own bug class. Direct-arg keeps `#`, stdin strips it, configmap env-file strips only line-leading `#`. Users reasonably model kubectl as one parser; it's three. The direct-arg behavior becoming the "correct" reference makes the stdin path a plain deviation - but someone using only stdin never sees the reference behavior, so nothing tells them they're losing data.
- The comment heuristic belongs to a different context. Whole-line and trailing comments make sense in curated env *files*; they make none in piped `env` output, which the help text itself recommends as input. A feature imported from file-parsing into a pipe context became a corruption path.
- Repro requires no cluster (`--local` + jsonpath) and the report includes a pure-Go one-liner against the parsing function - the gold standard for CLI bug reports.

## Honest limits
- Awaiting triage; no maintainer response or compatibility assessment at check time (changing the behavior could itself break anyone relying on trailing comments in stdin).
- The report demonstrates `--local`; behavior against a live cluster follows the same code path but was not separately exercised here.
- Which of the three semantics is "correct" is a design question the maintainers haven't answered yet.
