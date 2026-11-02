# uv's generated `activate.fish` splices the venv prompt into a single-quoted fish string unescaped - a quote in the prompt runs arbitrary fish code at source time

**Source:** [astral-sh/uv#23060](https://github.com/astral-sh/uv/issues/23060) (open; reported to astral security first, filed as a regular bug per their threat model)

## What happened

A Fedora maintainer triaging pypa/virtualenv's disclosed CVEs against uv found that CVE-2026-113732 (verified GitHub advisory, severity high: "virtualenv activate.fish runs commands from a path or prompt") reproduces verbatim in uv 0.13.6 (tag verified). uv generates its fish activation script from a template whose line 98 is `set -gx VIRTUAL_ENV_PROMPT '{{ VIRTUAL_PROMPT }}'` (verified in the 0.13.6 source tree) - the prompt value lands raw inside a single-quoted fish literal, so a single quote in the value terminates the literal and everything after it executes as fish code when someone sources the script. The repro is three lines: `uv venv --prompt "x'; touch /tmp/PWNED; set x '" venv`, then sourcing `activate.fish`, creates `/tmp/PWNED`. The same CVE class was fixed in virtualenv itself by [3bddeaf8](https://github.com/pypa/virtualenv/commit/3bddeaf8d02c3ee7f576503efb082f8f494cfcab) (verified commit, 2026-10-01: fish reads `\'` inside single quotes as an escaped quote, so POSIX `shlex.quote` rules were insufficient there). The reporter disclosed using an LLM (Claude Sonnet 5) to find the reproduction, reported it to security@astral.sh first, and quotes their response: it does not constitute a vulnerability under uv's attacker/threat models - hence a public bug. Sibling reports the same hour cover the same unescaped-splice pattern in the zsh path ([#23059](https://github.com/astral-sh/uv/issues/23059), CVE-2026-113726) and bash POSIX-mode prompt handling ([#23058](https://github.com/astral-sh/uv/issues/23058)) - all open, all verified to exist.

## Who this bites

- The scenario that matters is a venv created by one party and sourced by another: a project template, tutorial, tarball, or CI artifact shipping a pre-made venv whose `--prompt` (or path) carries the payload. The victim runs a completely ordinary `source .venv/bin/activate.fish`. Astral's threat model evidently treats venv creation as trusted - users who consume third-party venvs should know that assumption is load-bearing.
- uv is a default Python toolchain now (~70k stars), and activation scripts are sourced interactively, so even a narrow scenario has a large surface.

## Limits

- Single-source report (reporter association NONE, but a known Fedora Python maintainer) with a minimal repro and the template line independently verified here; I did not execute the repro.
- Severity framing follows the reporter and the upstream CVE, but astral explicitly declined vulnerability status - treat this as a hardening gap with a social-engineering precondition, not a remote exploit.
- No fix or maintainer comment at publish time; whether uv adopts virtualenv's fish-specific escaping is open.
