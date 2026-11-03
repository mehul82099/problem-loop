# TypeSpec's Python client emitter splices query/header wire names into generated code without escaping

**Source:** https://github.com/microsoft/typespec/issues/12473 (opened 2026-11-03 UTC, open, triaged by automation to the python-emitter area, no human maintainer reply yet)

## The problem

In `@typespec/http-client-python` (0.39.0, verified as current on npm; the Azure flavor `@azure-tools/typespec-python` consumes the same generator), the wire name an API author writes in `@query("...")` or `@header("...")` is interpolated into the generated request builder as a raw string literal, unescaped. A quote character in the wire name closes the literal early; everything after it becomes a live Python expression in the generated module, or the module simply fails with a SyntaxError at import. Either way the wire name no longer round-trips as data - and since the emitter runs at build time, the corrupted output is what ships in the SDK.

The report pins the mechanism precisely, and the cited code checks out on `main`: `parameter_serializer.py`'s `serialize_query_header` builds `"_{}['{}'] = {}".format(..., param.wire_name, ...)` with no escaping (the template layer's `escape_str` macro is never applied on this path), and two sibling sites - `serialize_path` and `pop_kwargs_from_signature` - interpolate `wire_name` the same raw way (verified present at lines 123, 168, 234). The same team is already fixing the model-side instances of this defect class: issue #12405 (verified open) and PR #12342 (verified open, 16 files) cover string declarations, discriminator values, docstrings and TypedDict keys - and the reporter verified that `parameter_serializer.py` is not among that PR's files, so the request-builder sites remain exposed even once it merges.

## Why it matters

Generated SDKs are trusted output: consumers pip-install them and never re-read the generated request builders. A spec-controlled string that silently changes what the generated code *does* - rather than just what it says - is a code-generation integrity bug, and in the Azure flavor it propagates into officially published Azure SDK for Python clients. The minimal repro in the issue uses a deliberately benign computed expression; the point is that the boundary between data and code is gone.

## Caveats

- Open with no human maintainer response yet; routing so far is the repo's automated triage, attributed here as tooling. Reporter association NONE, but the report includes a full local repro and file-level code citations, the load-bearing ones verified directly.
- The report demonstrates malformed/generated-expression output with a harmless payload; this finding intentionally does not elaborate exploitation and does not propose a patch.
