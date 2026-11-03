# Vite: `vite build` rips a `<link rel="stylesheet">` out of a declarative shadow DOM template and hoists it into the global document CSS

**Source:** https://github.com/vitejs/vite/issues/23981 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

A `<link rel="stylesheet">` inside a declarative shadow DOM `<template shadowrootmode="open">` is scoped styling: it should apply only inside that shadow root. `vite dev` leaves it alone. `vite build` removes it from the template and bundles its CSS into a stylesheet linked from the document `<head>`. The reporter's minimal repro is a host div with a shadow template whose only stylesheet is `:host{color:red;display:block}` - after build, the template is empty and `:host` sits in a global stylesheet, where it matches nothing useful and the shadow root gets no styles at all. Verified against vite 8.3.5.

The mechanism is visible in the source, and the reporter cites it correctly (checked at the referenced commit): the HTML plugin's `traverseNodes` explicitly unwraps `template` nodes into their `content` and keeps descending (`packages/vite/src/node/plugins/html.ts`), so a link inside a shadow template is visited like any document-level node, and the build's CSS path converts it to a JS import and bundles it. Nothing in that path distinguishes a `<template shadowrootmode>` subtree from ordinary HTML. Adding `vite-ignore` to each link keeps it in place, which is the reporter's current workaround. A related long-standing issue (#11855, verified open) asks for the opposite direction - getting styles into shadow roots - so the build tooling has an unresolved gap around shadow DOM scoping in both directions.

## Why it matters

Declarative shadow DOM is the standards-based way to ship server-rendered web components, and scoped styles are the point of the exercise: a build step that silently re-scopes shadow styles to the document both breaks the component (no styles inside the shadow root) and risks leaking rules onto the page. Because `vite dev` behaves differently from `vite build`, the breakage only appears in production output - the worst place to discover a scoping bug.

## Caveats

- Open with no maintainer response; reporter association NONE. The repro repository (created alongside the issue) and the two cited code locations were verified directly; the built-output description is the reporter's.
- This finding does not propose a fix. The `vite-ignore` workaround is the reporter's, noted for completeness, not vetted.
