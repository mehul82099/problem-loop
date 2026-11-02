# Rails: mutating a JSON attribute in place to an *equivalent* value marks the record changed - phantom UPDATEs, bumped `lock_version`, fired callbacks

**Source:** [rails/rails#59517](https://github.com/rails/rails/issues/59517) (open; proposed fix PR [#52939](https://github.com/rails/rails/pull/52939) open and unmerged, verified)

## What happened

Assigning `record.payload = { "one" => :two }` to a JSON column whose stored value is `{ "one" => "two" }` correctly registers as *no change* - assignment casts the symbol to its serialized form first. But mutating in place - `record.payload["one"] = :two` - marks the record changed, because `ActiveRecord::Type::Json#changed_in_place?` compares `deserialize(raw_old_value) != new_value` **without casting the new value**. The two paths disagree about the same logical edit. Saving the "changed" record issues an UPDATE writing byte-identical JSON - and with it everything an UPDATE drags along: `updated_at` advances, `lock_version` increments, update callbacks run. Reproduced on Rails 8.1.4 (released 2026-09-24, verified) and main, in a self-contained bundler/inline script; the comparison lives in `ActiveRecord::Type::Json`, so it's database-independent.

## Who this bites

- Any app that edits JSON columns in place (a very natural pattern: `record.settings["theme"] = :dark`) with symbol values: phantom dirty state means spurious UPDATEs on save, `updated_at` churn that breaks "recently touched" queries and cache keys, and - the sharpest edge - **optimistic-locking contention**: `lock_version` increments for writes that changed nothing, turning harmless in-place edits into `StaleObjectError` under concurrency.
- Update callbacks (`after_update`, websocket broadcasts, audit trails, search reindexers) fire for no-op writes, so downstream systems see phantom changes and can't tell them from real ones.

## Limits

- Single-source report (repo ~59k stars, reporter association NONE) with a clean minitest repro I did not run; mechanism is stated in the report against `changed_in_place?` and is plausible, but I verified only the releases and the fix PR's state, not the code line itself.
- The fix PR has been open a while without merge, so no released version corrects the comparison yet.
- Workaround direction (assign the whole hash instead of mutating in place) follows from the mechanism but is not maintainer-endorsed in the issue.
