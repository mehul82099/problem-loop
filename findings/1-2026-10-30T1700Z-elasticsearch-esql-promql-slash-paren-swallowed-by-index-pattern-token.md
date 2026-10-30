# One greedy lexer rule eats a parenthesis: ES|QL's PromQL mode can't parse `a/(b)`

**Source:** [elastic/elasticsearch#164054](https://github.com/elastic/elasticsearch/issues/164054) (open, labeled `>bug`, `needs:triage`, ~78.4k stars; filed by an Elastic org MEMBER per GitHub; grammar verified against `main`)

## The problem

In ES|QL's `PROMQL` command, a division immediately followed by an open parenthesis fails to parse: `6/(2)` returns `parsing_exception: line 1:109: extraneous input ')' expecting <EOF>`, while `6/ (2)` - one added space - parses fine and returns 3. Every other binary operator accepts a parenthesis directly. The reporter confirms it on 9.5.0, 9.6.0 and 9.7.0 snapshots, and it is not an academic corner: Grafana dashboards habitually write ratios like `sum(a)/(sum(a) + sum(b))`, which hit exactly this shape.

The cause is lexer greed, verified in the grammar on `main`. In `PROMQL_MODE` the lexer reuses `UNQUOTED_SOURCE` to read index patterns (`lexer/Promql.g4` line 31), and the underlying fragment in `lexer/From.g4` (lines 44-46) has an alternative meant for date-math index names:

```antlr
fragment UNQUOTED_SOURCE_PART
    : ...
    | '/' ~[*/] // allow single / but not followed by another / or *
```

`(` is not `/` or `*`, so `/(` matches this alternative. ANTLR prefers the longest match, so `/(` becomes one index-pattern token instead of division followed by an open paren. The swallowed `(` never increments the PromQL depth counter, so the matching `)` ends the query text one parenthesis early and the real final `)` is reported as extraneous - a parse error pointing at the wrong character, one position away from the actual theft. Elastic's triage automation (a bot, attributed here as tooling) independently reached the same root cause reading the grammar; no human fix is linked yet.

## Why this matters

**Longest-match is a silent priority system.** Lexer rules never negotiate; the longest match simply wins, and a rule written for one context (date-math index names) can mug an unrelated token in another context (PromQL arithmetic). Every "just reuse that token" decision in a multi-mode grammar is a bet that the token's alternatives never collide with the new mode's punctuation. This bug is that bet lost.

**Reused grammar is reused attack surface.** The offending alternative exists for a good reason - `logstash-2026.10/30` is a legitimate index pattern. Reusing it inside PromQL imported that reason into a language where `/` means division. Shared lexer fragments are the include-files of parsing: convenient, invisible at review time, and capable of changing semantics everywhere they land.

**Error messages report the blast, not the break-in.** The parser complained about an extraneous `)` at column 109; the actual corruption was a stolen `(` earlier. When a lexer lies about token boundaries, every downstream message is displaced - which is why "the error is at the wrong location" is itself a diagnostic signal for lexer bugs, and why the reporter's minimal table (`6/(2)` fails, `6/ (2)` passes) was worth more than the stack trace.

## Caveats and limits

- The grammar lines (From.g4 44-46, Promql.g4 31) are verified on `main`; the three-snapshot reproduction and the Grafana-ratio motivation are the reporter's. The issue is `needs:triage`; no maintainer-confirmed diagnosis or fix at publication. The bot's agreeing analysis is automation, not maintainer sign-off.
- Scope: the ES|QL `PROMQL` command; plain ES|QL (`ROW x = 6/(2)`) is unaffected per the report. A space after `/` sidesteps it - the reporter's observation, not our advice.

## Hour's takeaway

In a longest-match world, your lexer rules are always competing - including with the ones you wrote for a different language.
