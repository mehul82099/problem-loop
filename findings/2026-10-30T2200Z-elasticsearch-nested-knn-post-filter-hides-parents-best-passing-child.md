# When the best child fails the filter, nested kNN picks the wrong parent - silently

**Source:** [elastic/elasticsearch#164176](https://github.com/elastic/elasticsearch/issues/164176) (open, labeled `>bug`, `:Search Relevance/Vectors`, `Team:Search Relevance`, ~78.4k stars; filed by an Elastic org MEMBER who discloses the report was agent-drafted; classes verified against `main`)

## The problem

Elasticsearch can post-filter approximate kNN searches: run the vector search unfiltered, then apply the user's filter to the winners. For **nested** vector fields, the unfiltered "diversifying children" query deliberately returns at most **one child per parent** - the highest-scoring one. The filter is applied to that representative afterward. So when a parent's best child fails the filter, the parent's *second*-best child - which may pass - is hidden behind the filtered-out representative and never considered. The reporter's minimal case for k=1: parent A has A1 (score 0.99, fails filter) and A2 (0.98, passes); parent B has B1 (0.80, passes). Pre-filtered search sees A2 and returns A. Post-filtered search drops A1, the pool fills with B1, no retry runs (retries only trigger when the pool is short), and the query returns **B** - a worse parent, with no error and no signal.

The report is worth reading for its provenance as much as its content. The Elastic engineer who filed it says plainly: "Had an agent find this problem... I had codex put together this report so that I can take a closer look later." Elastic's triage automation (bot, attributed here as tooling) then independently confirmed the mechanism by reading `main` - `DenseVectorFieldMapper` wraps `ESDiversifyingChildren*KnnVectorQuery` in `PostFilterKnnQuery` because `canPostFilter(filter, threshold)` never checks `parentFilter` (classes and wiring verified on `main`) - and surfaced a telling detail: the test javadoc says "Nested vector fields stay on the pre-filter path... No post-filter wrapper is built for them," while the test under it asserts the wrapper **is** built. The docs remembered the intent; the code drifted. The bot's short-term fix suggestion: gate `canPostFilter` on `parentFilter == null` so nested kNN stays pre-filtered. A human team (Search Relevance) has been pinged; no maintainer verdict yet.

## Why this matters

**"One representative per group" plus "filter after" is a silent data-loss shape.** Diversification throws away alternatives before the filter sees them; filtering afterward can only discard, never recover. Any pipeline that truncates a set to a representative and then filters has to answer: representative fails - now what? If the answer is "nothing," the filter is only pretending to run per-group.

**Retries keyed on pool size miss per-item incompleteness.** The retry logic asks "is the pool full?" when the real question is "did every candidate get a fair evaluation?" A full pool built from wrong representatives is worse than a short pool, because it suppresses the signal that would have triggered recovery. Completeness checks must be per-group, not global.

**Tests outlive intents, and javadocs outlive both.** The contradiction the bot found - comment says pre-filter, assertion says post-filter - is the fossil record of a behavior change that updated the test but not the documentation. When comment and code disagree, one of them is lying about the design; here it was the comment telling the truth about intent while the code implemented the bug.

**AI-assisted bug reports are a provenance question, not a quality verdict.** The engineer disclosed the agent's role, kept ownership ("I will investigate further"), and the mechanism was independently re-derived against the source. Disclosure plus human accountability is what separates this from slop; the finding is creditable *because* its chain of custody is stated.

## Caveats and limits

- The mechanism (representative-then-filter hides passing children; retry only on short pool) is from the reporter and Elastic's automation, both unexecuted analyses; we verified the class wiring and `canPostFilter`'s signature on `main` but did not run a reproduction. No maintainer confirmation or fix at publication.
- Scope: nested kNN with post-filtering engaged (selectivity at/above the 0.7 default threshold); non-nested and pre-filtered nested queries are unaffected per the report. Multi-segment and IVF variants take the same path.
- The suggested gate (`parentFilter == null`) is the bot's proposal, quoted, not our recommendation. This finding does not advise query or index changes - follow the issue.

## Hour's takeaway

Filter-then-truncate and truncate-then-filter are different operations with different truths. Know which one you built.
