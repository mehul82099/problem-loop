# problem-loop

A small, readable five-stage agent pipeline that picks a real problem from public internet sources every cycle, argues about it, decides, writes it up with sources, and publishes the result to this repo.

```
Research -> Discussion -> Conclusion -> Action -> Publisher
```

| Stage | What it does |
|---|---|
| Research | Pulls candidate problems from Hacker News (Algolia API), GitHub issue search and Stack Exchange. No API keys. A failing source is skipped, not fatal. |
| Discussion | Three fixed roles score every candidate: `user-advocate` (demand), `skeptic` (is it a concrete, new problem), `builder` (is it small enough). A score of 0 is a veto. |
| Conclusion | Picks the highest unvetoed total. Declines to pick if nothing reaches the minimum. |
| Action | Writes a finding document: the chosen problem, source link, the votes, the runner-ups. |
| Publisher | Writes the file under `findings/`, updates `findings/index.json` (so nothing is published twice), and can commit and push. Refuses any finding with no source. |

## Run it

```
python3 pipeline.py --root .          # one cycle, writes a finding
python3 pipeline.py --root . --push   # also git add, commit, push
python3 -m unittest -v                # 16 offline tests
```

Python 3.9+, standard library only.

## What it does not do

- **No LLM is called.** Discussion is explicit scoring rules, and they are crude (they count reactions and look for problem words). Each stage is one class, so a model-backed stage can replace it.
- A finding is a *candidate problem with sources*. It never claims a solution.
- Automatic picks favour popular, old issues. The hourly runs of this repo add a human-style check on top; each finding file says what was picked and why.
- Source ranking depends on third-party APIs, which can rate-limit (GitHub's unauthenticated search is limited to 10 requests per minute).

## Cadence

The repo is maintained hourly. Each cycle adds at most one finding, or nothing if no candidate clears the bar. Commit history is the audit trail. Stars are not bought or arranged.

## Sources for the APIs used

- Hacker News Search API: https://hn.algolia.com/api
- GitHub REST, search issues: https://docs.github.com/en/rest/search/search#search-issues-and-pull-requests
- Stack Exchange API, questions: https://api.stackexchange.com/docs/questions

## License

MIT
