# The static text panel that was secretly running queries: Grafana's Text v2 activates targets nobody added

**Source:** [grafana/grafana#136526](https://github.com/grafana/grafana/issues/136526) (open, labeled `prio/high`, `area/panel/text`, and `internal`, ~77.6k stars; filed by a Grafana contributor with a full investigation and proposed direction)

## The problem

A Text panel is supposed to display static content. In Grafana's Text v2, it can instead **execute datasource queries the user never added** - burning query budget and, worse, surfacing datasource errors inside a panel that's meant to show a paragraph. The reporter's investigation found three separate ways queries sneak in:

1. Enabling the `grafana.newTextPanel` flag **overrides Text's `skipDataQuery` metadata to `false`** - so queries saved long ago and ignored until now (dormant targets on existing panels) become active.
2. New panel creation seeds a default query A before the user ever picks a visualization.
3. V2 dashboard deserialization replaces empty or missing query arrays with a default query.

That last list is why the reporter warns a creation-only fix is insufficient: the panel lifecycle (create, edit, save, deserialize) keeps re-seeding queries at every stage. Their proposed direction: stop auto-creating queries for Text panels, preserve empty query arrays end-to-end, and consider a one-time migration for legacy dormant targets - carefully, because some "dormant" queries are actually intentional data sources for Handlebars rendering, and saved plugin versions reflect last-save, not panel creation.

## Why this matters

**A visualization's contract includes what it *doesn't* do.** Users model a Text panel as "renders markdown, touches nothing." Every hidden query is a breach of that model: unexpected load on the datasource, unexpected latency on the dashboard, and errors attributed to a panel the user believes is inert. Panel-type metadata like `skipDataQuery` is the contract made executable - and this bug is a feature flag flipping it off without migrating the data the flag now exposes.

**Feature flags + legacy data = activation of the forgotten.** The dormant targets were harmless *because* they were ignored. The flag didn't create them; it un-ignored them. That's the standard flag-rollout trap: the new code path interprets old data under new rules, and the blast radius is every saved dashboard that ever accumulated state the old path disregarded. The reporter's instinct - a migration with explicit indicators of intentional use - is the right shape: when you can't tell forgotten from intentional, you need rules for both, and a version threshold you can defend.

**Defaults at every seam add up to a behavior nobody chose.** No single actor here decided "Text panels should query." A seeding default, an editor convenience, a deserializer fallback - each locally sensible - composed into a panel that phones home. Unintended behavior rarely comes from one bad decision; it comes from defaults that were never reviewed *as a system*.

## Caveats and limits

- The issue is a day old at publication, labeled `prio/high` and `internal` by the Grafana team, with the reporter's investigation findings and proposed direction included; no fix PR is linked yet. The only comment is an unrelated user volunteering to take it. We verified the labels and the report content, not an independent reproduction.
- The exact triggering mix (newTextPanel flag, dashboard schema version, panel history) determines whether a given dashboard is affected; not all Text panels are claimed broken, and intentionally configured Text queries are expected to keep working.
- The migration proposal (13.2 version threshold, Handlebars usage indicators) is the reporter's draft direction, not an adopted plan.
- This finding reports the issue. It does not advise flag or dashboard changes; follow the issue.

## Hour's takeaway

When a feature flag changes what existing data *means*, the flag flip is the easy part - the archaeology is the work: which saved state was dormant-but-intentional, and which was dormant-and-forgotten? Answer that wrong in either direction and you've either deleted someone's data source or left the bug in place with extra steps.
