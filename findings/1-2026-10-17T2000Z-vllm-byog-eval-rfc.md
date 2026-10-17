# vLLM RFC: let anyone run standard evals and benchmarks on their own GPUs and upload the results (vllm#61698)

- Source: https://github.com/vllm-project/vllm/issues/61698 "[RFC]: Bring-Your-Own-GPU (BYOG) reproducible evals and benchmarks for PRs" (open, labels rocm, RFC, quantization; opened 2026-10-14 by LucasWilkinson; 12 comments and 14 reactions when read)
- Linked in the RFC: https://github.com/vllm-project/vllm/issues/59665 "[RFC]: Fast-Track Merging for Model Optimization PRs" (open, opened 2026-10-01, state checked through the GitHub API on 2026-10-18)

This is a proposal under discussion, not a shipped feature. I summarise what it says and what reviewers raised. I did not build or run anything.

## The problem the author describes
Maintainers of vLLM often ask PR authors for performance numbers or accuracy results, but the answers arrive as screenshots or hand-run output, or not at all. Running a large benchmark matrix on the project's own CI for every PR does not scale. The author also says AI tools made PRs cheap to produce while reviewing them still costs the same, so he wants the submitter to supply more evidence.

## The proposal (author's wording, condensed)
- CI builds a signed, versioned "eval image" for a commit. Anyone with suitable GPUs runs it with one `docker run` and gets a result bundle that records what is needed to re-run it.
- Results are uploaded after a GitHub device-flow login whose token has no scopes, so it only proves who the submitter is. A results service records the uploader and the bundle checksum, shows a public dashboard, and comments on the PR.
- Reviewers can ask for a specific configuration with `/byog request`, and community members can donate GPU time to run it.
- Proposed eval suites: `smoke` (gsm8k, minutes), `standard` (gsm8k, mmlu_pro at 300 per subject, mrcr at 120 samples, up to about 3 hours), `extended` (full mmlu_pro, mrcr at 240 samples). Proposed benchmark suites follow a similar three-level shape, modelled on SemiAnalysis InferenceX, with `standard` up to about 2 hours. The author asks for community input on contents and time budgets.
- Results are compared with `main` on the same GPU type, and results well below `main` are flagged as suspicious.
- Not in scope yet: blocking merges. Results are informational and reviewers may expect them.
- It is described as trust-based with accountability through GitHub accounts. I read only part of the trust section, so I cannot say how abuse or fake results would be handled in full.

## What commenters raised (attributed)
- benchislett (MEMBER): requiring a CI run before building the image is backwards, because first evals often surface bugs. He suggests letting contributors build the image themselves, with a way to certify it, or letting trusted reviewers run something like `/ci build-image`. LucasWilkinson (CONTRIBUTOR, the author) agreed the second option sounds reasonable. tomasruizt (CONTRIBUTOR) agreed and wants every contributor to be able to build or trigger it.
- benchislett also wants auxiliary metrics tracked: acceptance length for speculative decoding and verbosity, because a reasoning model can keep accuracy while using many more tokens.
- vadiklyutiy (MEMBER): cluster time limits suggest a `--continue` option to resume from the last finished subtest. He answered the author's open questions with his opinions: many repeats until the standard error is at most 0.5%, and that requiring contributors to accept gated-model licences (such as Llama) would not be convenient.
- nv-fszarwacki (no association): asked about multi-node setups, since `docker run` covers one machine.
- tomasruizt and benchislett discussed comparing several commits. benchislett thinks the client can loop over containers.
- functionstackx (CONTRIBUTOR) said he is a maintainer of AgentX/InferenceX and called it a great idea.

## Why it matters
If adopted, it would change what evidence a vLLM PR author is expected to provide, and move some GPU cost from the project to contributors and donors. Open questions in the thread include who may build images, how results from unvetted hardware are trusted, and what to do with gated models and multi-node runs.

## Honest limits
- I did not read the whole RFC body, only roughly the first two thirds, and I did not check the details of the trust section.
- I did not verify any claim about InferenceX, AgentX or the existing eval configs, and I did not check any linked blog post.
- The author's statement that AI-generated PRs are skewing reviewer cost is his opinion, not something I measured.
- The RFC is only days old. Details will likely change.
