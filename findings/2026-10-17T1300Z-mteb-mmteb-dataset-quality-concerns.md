# MTEB: quality concerns in 11 MMTEB datasets, and the proposed v3 benchmark

- Source: https://github.com/embeddings-benchmark/mteb/issues/5416 "Quality Concerns in 11 MMTEB Datasets" (open, label `Decision`, opened 2026-09-08, 22 comments, last activity 2026-10-17)
- Pull request mentioned in the thread, state checked through the GitHub API on 2026-10-17: https://github.com/embeddings-benchmark/mteb/pull/5687 "benchmark: Add mmteb v3" (open, not merged, by KennethEnevoldsen, opened 2026-10-16)
- Results data cited by commenters: https://github.com/embeddings-benchmark/results (repository exists)

## The report
Reporter shuangli-z says he analysed all 131 MMTEB tasks using scores from 172 models with complete results, computing rank agreement across model tiers and checking the BM25 baseline for retrieval tasks, then spot-checked samples. He flags 11 datasets in three groups:
- Reasoning tasks labelled as retrieval: TempReasonL1, SpartQA, WinoGrande. For example, TempReasonL1 queries are date arithmetic and the "document" is the computed date.
- Linguistic acceptability tasks that embeddings may not be able to solve: DalajClassification, ScalaClassification.
- Data integrity concerns: PAC, SemRel24STS, AfriSentiClassification, PoemSentimentCls, KorSarcasmClassification, MultiEURLEXMultilabelCls (label noise by his sampling).

He later withdrew the PAC claim. PAC turned out to be a metadata error: the description says "Polish Paraphrase Corpus" while the paper cited by the reporter describes the Polish Abusive Clauses dataset. A contributor offered to fix the description. Also, for AfriSenti he said he judged labels by translating the texts to English with an AI model and does not speak those languages, and agreed that is weak evidence.

## What maintainers said (attributed)
- tomaarsen and Samoed (marked as members in the GitHub API) agreed TempReasonL1 and SpartQA are weak. Tom noted that models trained on such datasets gain a large edge in the overall mean, while others cannot compete. He added that WinoGrande is a fill-mask style problem and a poor fit for a retrieval subset.
- KennethEnevoldsen (marked as a contributor, and the author of the v3 PR) said some odd datasets entered MMTEB because it was selected for diversity, and that rank correlation alone is not a good indicator. On 2026-10-12 he proposed a short-term rework: remove TempReasonL1, SpartQA and WinoGrande, fix PAC, and look at the other concerns case by case, followed by a longer replacement of weak datasets with better ones. He preferred calling the cleaned version v3 rather than v2.1.
- Samoed raised extra worries about FollowIR instruction tasks and WebLINX.

## A second review
On 2026-10-15 contributor oliarmak-web posted an audit of five tasks with explicit criteria and a recommendation. For TempReasonL1 it reports 4,000 queries, 12,504 candidate strings and one positive each, and result medians around 1.24 across 204 records, and recommends removing it from the general aggregate while keeping it in the RAR-b benchmark. I read only the first part of that comment. Its writing is polished and long, and I could not tell whether it was written with AI help, so treat the numbers as the commenter's.

## Status
Samoed pointed out on 2026-10-17 that PR 5687 is already open. I only confirmed that it exists, is open, and has the title above. I did not read its diff, so I cannot say which tasks it removes.

## Why it matters
Scores on the leaderboard average over these tasks, so a task where only models trained on it do well shifts rankings. This is the maintainers' own point in the thread.

## Honest limits
- I did not recompute any score, rank correlation or label sample. All statistics and spot-check results come from the reporter and the second reviewer.
- The 11 labels of "concern" are the reporter's judgement, partly withdrawn, and the maintainers have not agreed on all of them.
- The planned removal list in KennethEnevoldsen's comment is his lean, not a decision, and the PR is unmerged.
- The reporter's arXiv citation for PAC was not independently checked by me.
