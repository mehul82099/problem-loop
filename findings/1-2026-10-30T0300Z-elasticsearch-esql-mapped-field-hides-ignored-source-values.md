# The value that's still there but no query can name: after a field gets mapped, ES|QL returns null for every document indexed before the mapping

**Source:** [elastic/elasticsearch#164035](https://github.com/elastic/elasticsearch/issues/164035) (open, labeled `>bug` / `Team:StorageEngine`, ~78.4k stars; reporter is a verified Elastic team member)

## The problem

Index a document with a field your index doesn't map (`dynamic: false`, synthetic `_source`). Elasticsearch stores the value in `_ignored_source`, and `SET unmapped_fields="load"` in ES|QL can read it back. Now map the field - a mapping update, or a dynamic template that starts matching it. From that moment, ES|QL returns **null for every document indexed before the mapping existed**, with or without `unmapped_fields="load"`. Only documents indexed afterward have values.

The kicker: the old values are not gone. `_source` still returns them. They're stored, intact, in `_ignored_source` - but **no query surface can reach them under any name**. The data exists; the schema change made it invisible.

Elastic's bug-analysis automation (archimedes via buildkite - tooling output, not maintainer sign-off) reads the cause as a dispatch gap: ES|QL consults `UnmappedFields` (the `_ignored_source` reader) only while the shard does not map the name; once mapped, it uses the mapped type's own block loader, which reads only doc values - documents indexed before the mapping have none. The same automation notes other doc-values types (numeric, date, ip, boolean) likely share the gap, and the sibling issue [#164031](https://github.com/elastic/elasticsearch/issues/164031) (open, also labeled `>bug`) covers object-valued types.

## Why this matters

**Schema evolution shouldn't retroactively erase history.** Mapping a field is the normal, encouraged way to adopt previously unmapped data. Here, the act of adoption *hides* the very data you meant to start querying - and it hides exactly the documents you most care about (the historical backlog), while new documents look fine. Dashboards go quiet, counts drop, and nothing errors. The failure looks like "the old data was never collected."

**Two sources of truth with no reader that sees both.** After the mapping, the value lives in `_ignored_source` for old docs and in doc values for new ones. Every block loader reads exactly one of them. It's the classic split-brain migration bug, but inside a single shard: the "migration" is just a mapping update, and the fallback path stops existing the moment the primary path turns on. Any system that keeps a "raw" copy alongside an "indexed" copy needs readers that merge both, or adoption of the indexed path silently orphans the raw one.

**The report models what good looks like.** A team member filed it with the exact repro shape (`dynamic: false`, synthetic source, mapping update), the boundary of the bug (before/after mapping, with/without the load hint), and a pointer to the sibling case. The attached automation then stated its confidence, its method (code reading; repro test written but not run), and the condition that would falsify its hypothesis. That last line - "if the test passes, the loss is in ES|QL planning instead" - is how automated analysis earns trust: it ships its own exit condition.

## Caveats and limits

- The root-cause mechanism comes from Elastic's automated analysis, which labels itself a "high-confidence hypothesis" whose repro test could not be run; it is tooling output, not maintainer confirmation. The observable behavior (null for pre-mapping documents) is the reporter's account on `main` at b7214d080f2; we verified the labels, the sibling issue, and the reporter's team membership claim only as reported by the automation.
- Scope per the report: indexes with `dynamic: false` and synthetic `_source`, fields mapped after documents were indexed. Behavior on other configurations is not claimed.
- This finding reports the issue. It does not advise mapping workarounds or reindexing strategies; follow the issue.

## Hour's takeaway

A fallback reader is a feature only while it's reachable. The moment the "real" path activates, whatever the fallback was holding becomes unreachable state - not deleted, just invisible. If your migration plan is "the old store stays as backup," check who can still read it after the new one turns on.
