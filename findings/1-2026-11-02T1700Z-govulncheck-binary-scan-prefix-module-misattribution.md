# govulncheck binary scans assign advisories to a sibling module whose path merely shares a string prefix

**Source:** https://github.com/golang/go/issues/82780 (opened 2026-11-02, open, no maintainer reply yet)

## The problem

`govulncheck -mode=binary` can blame the wrong module for a vulnerability when the real affected module's path is a plain string prefix of an unrelated module's package path. The reporter built a tiny Linux binary that imports two separate public modules, `github.com/docker/docker` and `github.com/docker/docker-credential-helpers`, and scanned it. govulncheck exited 3 and attributed GO-2026-4887 and GO-2026-4883 to `github.com/docker/docker-credential-helpers@v0.9.8`, naming `client.NewShellProgramFunc` as the vulnerable symbol.

The official records tell a different story. The GO-2026-4887 and GO-2026-4883 entries on vuln.go.dev list `github.com/docker/docker`, `github.com/moby/moby` and `github.com/moby/moby/v2` as affected. `github.com/docker/docker-credential-helpers` appears in neither. The credential-helpers module gets flagged only because the string `github.com/docker/docker` is a prefix of `github.com/docker/docker-credential-helpers/client`.

## Why it happens

In `golang.org/x/vuln/internal/vulncheck/vulncheck.go` (v1.9.0), the branch that handles packages whose module is not known from build info picks a module with `strings.HasPrefix(importPath, md.Module.Path)`, taking the longest matching module path. A comment on the very next line already concedes the weakness: `TODO: do matching based on path components.` Prefix matching on raw strings cannot tell `example.com/foo/pkg` (belongs to module `example.com/foo`) apart from `example.com/foo-helpers/client` (a different module that only shares a prefix). The reporter reproduced the misattribution on govulncheck v1.9.0 and observed the same behavior on v1.7.0.

## Why it matters

Binary-mode scanning is what teams point at shipped artifacts in CI, where no module graph is available. A false attribution has two symmetric costs: it cries wolf against a clean module (here a credential helper, an especially awkward place for a bogus CVE), and it can mask whether the actually affected module is present at a vulnerable version, since the finding is filed under the wrong module name. The suggested fix direction, matching on path components instead of raw string prefixes, is already anticipated by the TODO in the code.

## Caveats

- The issue is open with no maintainer response; the behavior is documented by the reporter with a self-contained repro, not confirmed by the Go security team.
- This reports the upstream report and verifies its public anchors (the two vuln.go.dev records' affected-module lists, the v1.9.0 tag, and the prefix-matching code at the cited location). It does not re-run the scan and does not propose a specific patch.
- The reporter notes the repro binary only needs to be built, not executed; the misattribution happens entirely at scan time.
