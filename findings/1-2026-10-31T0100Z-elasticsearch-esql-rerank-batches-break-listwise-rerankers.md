# Scores that only mean something together, merged as if they don't: ES|QL RERANK batches listwise rerankers into nonsense

**Source:** [elastic/elasticsearch#164149](https://github.com/elastic/elasticsearch/issues/164149) (open, labeled `>bug`, `Team:Search Relevance`, ~78.4k stars; batch constant verified against `main`; no human maintainer verdict yet)

## The problem

ES|QL's `RERANK` command splits your candidates into small independent inference requests - `DEFAULT_BATCH_SIZE = 10`, verified verbatim in `RerankOperator.java` on `main` - then merges the returned scores with a global `SORT _score DESC`. That merge is only valid if scores from different requests are comparable. For **pointwise** rerankers (cross-encoders scoring each query-document pair alone), they are. For **listwise** rerankers, which score documents *relative to each other* in one shared context, they are not: a document's score depends on which 9 other documents happened to share its batch. And the RERANK documentation recommends a listwise endpoint - the preconfigured `.jina-reranker-v3` (docs mention verified) - which places query and candidates in one context window where documents attend to each other.

The failure is silent and nondeterministic. Batch membership is decided by page boundaries, which depend on schema, value sizes, heap, and - without an upstream sort - shard timing: the same query can rank differently across runs. A document that looked strong against 9 weak neighbors outranks a better document scored against 9 strong ones. No warning is emitted; results look plausible. The report further argues the open enhancement #161191 (verified: "Allow configurable inference batch size for ES|QL RERANK") would not fix this and could make it worse - bigger batches are still not the whole candidate set. By contrast, the older `text_similarity_reranker` retriever sends the entire rank window in one request. Elastic's triage automation (bot, attributed as tooling) read `main` and reports the code matches the analysis; the Search Relevance team has been pinged but no human verdict or fix exists at publication.

## Why this matters

**Aggregation has a type, and "sortable" is not universal.** Merging scores across requests is a mathematical claim - that the score function is context-free - smuggled in as plumbing. Anytime a system shards work for performance and reassembles results, the reassembly is only as valid as the invariants of the thing being sharded. Listwise models exist *because* relevance is contextual; batching them is parallelizing away the property you paid for.

**Defaults and docs form the real API.** The batch size is invisible, the docs recommend a listwise model, and the command emits no warning - so the documented happy path is the broken path. Users did everything right: read the docs, used the recommended endpoint, got a subtly wrong ranking they will never notice. Compatibility constraints between features need to live in the tool (a check, a warning, a refusal), not in the user's head.

**"Looks plausible" is the most expensive failure mode.** A wrong ranking doesn't page anyone. It quietly degrades every search, recommendation, and RAG answer downstream - each individual result defensible, the ordering wrong in aggregate. Systems whose output is a judgment call need invariant tests ("reranking a shuffled input must not change the order") precisely because no human will eyeball the difference.

## Caveats and limits

- The batch constant and the docs' listwise recommendation are verified; the request-splitting mechanics and the cross-run nondeterminism are the reporter's code-level analysis, corroborated by Elastic's automation (tooling) reading the same code. Neither ran an end-to-end listwise comparison; we did not run one either.
- Scope: ES|QL `RERANK` with listwise endpoints; pointwise rerankers are unaffected. The `text_similarity_reranker` retriever takes the whole-window approach per the report.
- This finding does not advise reranker or query changes - follow the issue and the Search Relevance team.

## Hour's takeaway

Before you merge results from parallel work, ask what each piece knew when it was computed. Context-dependent scores can't be parallelized by splitting the context.
