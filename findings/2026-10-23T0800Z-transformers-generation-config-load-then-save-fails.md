# Hugging Face Transformers: a generation config that loads fine from the Hub cannot be saved again

- Source issue: https://github.com/huggingface/transformers/issues/49879 (open at check time; opened 2026-10-22 17:47 UTC; 4 comments)
- Fix PR by the reporter: https://github.com/huggingface/transformers/pull/49914 (open, not merged, created 2026-10-23)
- Earlier attempt by another contributor: https://github.com/huggingface/transformers/pull/49903 (closed unmerged)
- Prior PRs the thread cites: https://github.com/huggingface/transformers/pull/45619 ("Remove unnecessary generate warnings", closed) and https://github.com/huggingface/transformers/pull/45559 ("Drop noisy generate warnings when do_sample=False (or num_beams=1)", closed)
- Example config checked: https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/generation_config.json
- Project: https://github.com/huggingface/transformers (Apache-2.0)
- Checked: 2026-10-23 08:55 UTC

## Problem
The reporter says that in transformers 5.18.0 and current main, loading a published model's `GenerationConfig` and saving it again fails validation: `ValueError: GenerationConfig is invalid: top_p ... do_sample is not set to True ...`. They say the practical hit is saving a whole model after fine-tuning or editing weights: `model.save_pretrained()` writes `config.json` and then raises on the generation config, leaving an output folder with a config and no weights.

## What we checked
- The cited model's `generation_config.json` on the Hub does set `top_p: 0.95` and `temperature: 1.0` and has no `do_sample` key. In Transformers, `do_sample` defaults to false, so the published file does not pass the library's own save-time validation. That matches the report. We did not run the reproduction.
- A maintainer replied that the published file is "indeed an error on model owner's repo", but agreed saving can be allowed for values the user never changed, and invited the reporter to open a PR.
- PR #49914 (open) is the reporter's attempt; per the reporter's own comment, it warns on issues that are unchanged since load and still blocks new or edited ones. They say the now-closed PR #49903 only allowed a save when the whole config hashed the same as at load, so any edit (like setting `pad_token_id`) would fail again. We did not read either diff, so both descriptions are the reporter's.
- The reporter notes #45619 already stopped `generate()` from warning about values that come from a model's file, while `save_pretrained` kept validating strictly. We verified those PRs exist and are closed, not their content.

## What this does not tell you
- No fix is merged. The behavior may be intended to change per #49914, but that is not decided.
- The thread's view is split in an interesting way: the config file is "wrong" by the library's rules, yet the library accepts it on load and rejects it on save. The finding is that inconsistency, not that one side is correct.
- The reporter's workaround (editing the model's `generation_config.json` by hand) is their suggestion, not ours; editing a published config changes generation behavior.

## Honest limits
- We read the issue, the Hub config file, and the PR listings. We ran no Python.
- Issue state may have changed since 08:55 UTC.
