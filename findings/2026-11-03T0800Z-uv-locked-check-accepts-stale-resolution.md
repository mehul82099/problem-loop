# uv `--locked` / `--check` can pass a lockfile whose pinned versions violate the project's declared specifiers

**Source:** [astral-sh/uv#23073](https://github.com/astral-sh/uv/issues/23073) - opened 2026-11-03 by mueslo (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

The reporter describes a validation gap in uv's lockfile checks: `uv lock --locked`, `uv lock --check`, `uv sync --locked` and `uv sync --check` all compare the *declarations* recorded inside the lockfile against the declarations in `pyproject.toml` - but never check that the *resolved package versions* in the lockfile actually satisfy those declared specifiers.

Their minimal reproduction:

1. Create a project with `dependencies = ["six==1.16.0"]`, run `uv lock`.
2. Edit `pyproject.toml` to require `six==1.17.0`.
3. Hand-edit `uv.lock` so its recorded declaration (`[package.metadata] requires-dist`) also says `six==1.17.0`, but leave the resolved `[[package]]` entry pinned at `1.16.0` (with its valid wheels and hashes).

Per the report, all four guarded commands then exit 0, and `uv sync --locked` installs `six 1.16.0` even though the project declares `==1.17.0`. The control case behaves correctly: if the lockfile is *not* hand-edited, every command fails with "The lockfile at `uv.lock` needs to be updated".

The reporter writes (self-reported, not independently confirmed): "We hit this in production: a hand-edited `uv.lock` declared `kifv-model-serving==2.3.0rc2` but resolved `2.2.7`; every check passed and our deployed images silently ran the old version." They add that this was "observed in practice after git merges."

## Proposed fix

The reporter proposes validating each locked version on a dependency edge from a workspace member against the declared specifier with a pure PEP 440 `VersionSpecifiers::contains(locked_version)` test. Both sides of that comparison are already static (the specifier lives in the lockfile's recorded declarations / in `pyproject.toml`, and the locked version is in the lockfile), so no network access or metadata refresh is needed. A failure could surface as a new `SatisfiesResult` variant, making `--locked` / `--check` exit non-zero as they already do for the control case. They also suggest the lockfile parser could reject a file whose recorded declaration says `==1.17.0` while the corresponding edge resolves to `1.16.0`, similar to the existing `InconsistentVersions` check on wheel filenames.

## Verification (checked during this finding)

- The reporter's environment is `uv 0.12.3` (Windows) with the issue's version field showing `uv 0.13.7 (316c827e0, 2026-11-03)`; release `0.13.7` and commit `316c827e` both exist (release published 2026-11-03, commit dated 2026-11-03).
- The described design constraint is visible in current uv source. On `main`, the lock-satisfaction walk in `crates/uv-lock/src/lock/mod.rs` (line ~4688) contains exactly:

  ```rust
  // If the package is immutable, we don't need to validate it (or its dependencies).
  if package.id.source.is_immutable() {
      continue;
  }
  ```

  Registry sources are immutable, so registry packages - which is where version pins live - are skipped by this part of the walk. The requirement comparison in `satisfies_requires_dist` (line ~3922) compares the project's current declarations against the lockfile's *recorded* `package.metadata.requires_dist`, i.e. declaration against declaration; neither step compares a declared specifier against the resolved version stored in the lockfile. This is consistent with the mechanism the report describes.

  Note: the reporter cites the path `crates/uv-resolver/src/lock/mod.rs` for uv 0.12.3; on current `main` the lock module has moved to `crates/uv-lock/src/lock/mod.rs`, with the same logic present.

- The reproduction's packages are real: `six` on PyPI has versions 1.16.0 and 1.17.0 (1.17.0 is the latest at check time), so the 1.16.0 -> 1.17.0 hand-edit example is plausible as written.

## Limits

- The reproduction was not executed here; all behavior statements come from the issue text. The production incident is the reporter's own account and is not independently confirmed.
- The reporter's association is NONE, so their claims are self-asserted. As of writing, the issue has no maintainer response (0 comments, 0 reactions), so uv's position on whether this is intended behavior or a bug is unknown.
- Hand-editing a lockfile is arguably an unsupported operation; the security/CI-relevance depends on how a stale lock arises in practice (the reporter attributes theirs to git merges). This finding does not reproduce that path.
- Whether the proposed `contains()` check is accepted - and how it should handle markers, extras, and non-registry sources - is a design question for uv maintainers.

## Sources

- Issue: <https://github.com/astral-sh/uv/issues/23073>
- uv release 0.13.7: <https://github.com/astral-sh/uv/releases/tag/0.13.7>
- Lock satisfaction walk (main): <https://github.com/astral-sh/uv/blob/main/crates/uv-lock/src/lock/mod.rs>
- six on PyPI: <https://pypi.org/project/six/>
