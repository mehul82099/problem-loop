# Opik Python SDK: a failed Dataset.insert() leaves unuploaded items in the dedup cache, and a retry silently drops them

**Source:** [comet-ml/opik#9376](https://github.com/comet-ml/opik/issues/9376) - opened 2026-11-03 by BlueX888 (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

With the default `deduplication=True`, `Dataset.insert()` (and `update()`, which delegates to it) adds each item's content hash to the in-memory dedup cache *before* the batch carrying that item is uploaded. If the insert fails part-way - a non-JSON-serializable item, a generator raising mid-iteration, or a 4xx from the backend after earlier batches succeeded - the hashes of items that never reached the backend stay cached. Retrying then treats those items as already-present duplicates and skips them; the duplicate path only logs at DEBUG, so nothing is surfaced.

The reporter includes a self-contained reproduction using a fake upload transport (no Opik server needed). First attempt with items a, b(bad), c raises `ItemNotSerializableError` and sends nothing; after fixing the bad item and retrying with a, b, c, only 2 items are sent instead of 3 - item a was never sent on either attempt yet is treated as a duplicate. A second variant with 1001 items, where the backend accepts the 1000-item batch but rejects the 1-item batch, uploads 0 items on retry instead of 1; the 1000 persisted items are correctly deduplicated, the one that failed is silently lost.

The reporter's stated expectation: on retry, items that never reached the backend should be uploaded, while items already persisted stay deduplicated. They note `Dataset.update()` inherits the behavior, and that passing `deduplication=False` on the retry avoids the skipped items at the cost of disabling duplicate checking for that call.

## Root cause (as reported, verified against source)

The reporter points at `Dataset._deduplicating()` (`sdks/python/src/opik/api_objects/dataset/dataset.py:737`): it inserts `item_hash` into `self._hashes` and `self._id_to_hash` as it yields each item, before any upload. Meanwhile `__internal_api__insert_items_as_dataclasses__()` only resets the cached item count in its `finally` block (~line 1017), leaving `_hashes`, `_id_to_hash` and `_hashes_synced` untouched. Because `_hashes_synced` remains `True`, the next deduplicated insert skips `__internal_api__sync_hashes__()`, the method that rebuilds the caches from what the backend actually persisted.

I checked the source at the commit the reporter names (`main` at `1c7b698`, 2026-11-03 - the commit exists and is dated 2026-11-03T10:25Z). It matches:

- `dataset.py:737` defines `_deduplicating`; at lines 772-775 it does `self._hashes.add(item_hash)` and records `_id_to_hash[...] = item_hash` while yielding, before the writer runs.
- The duplicate branch at lines 766-771 logs `"Duplicate item found with hash: %s - ignored the event"` at `LOGGER.debug` - silent at default logging level, as claimed.
- The `finally` block around line 1017 sets only `self._dataset_items_count = None`; `_hashes`, `_id_to_hash` and `_hashes_synced` are not reset there.

The reporter suggests that marking the cache out of sync when the upload funnel raises would make the retry rebuild from the backend; they explicitly did not include a patch.

## Limits

- The reproduction script was not executed here; output values (2 of 3, 0 of 1) are quoted from the issue. The root-cause lines above were verified against source at the named commit.
- The reporter names version 2.2.139; at check time the latest opik release on PyPI and GitHub is 2.2.138, so the verified anchor is the named `main` commit, not the release tag.
- BlueX888's association is NONE, so the account of the behavior is self-asserted, though the code reading supports the mechanism. As of writing, the only reply on the issue is from `github-actions[bot]` ("Scout", the repo's automation agent) confirming an existing workaround (`deduplication=False` on retry) - that is tooling output, not maintainer triage or approval.
- Affected scope per the report is the Opik Python SDK client-side dedup cache; the backend itself is not implicated.

## Sources

- Issue: <https://github.com/comet-ml/opik/issues/9376>
- Dataset SDK source at the named commit: <https://github.com/comet-ml/opik/blob/1c7b698/sdks/python/src/opik/api_objects/dataset/dataset.py>
- Opik on PyPI: <https://pypi.org/project/opik/>
