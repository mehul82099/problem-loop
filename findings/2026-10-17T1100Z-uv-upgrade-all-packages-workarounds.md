# uv: there is no `upgrade --all` for a plain virtualenv, and the maintainers' list of workarounds

- Source: https://github.com/astral-sh/uv/issues/1419 "Add option to upgrade all packages in the environment, e.g., `upgrade --all`" (open, labels `enhancement`, `needs-design`, `area:uv-pip`; opened 2024-02-16; 631 reactions; 65 comments; last activity 2026-10-17)
- Maintainer overview comment (konstin, 2025-05-04): https://github.com/astral-sh/uv/issues/1419#issuecomment-2849420114
- Related, state checked through the GitHub API on 2026-10-17: https://github.com/astral-sh/uv/issues/6794 "Upgrade dependencies in `pyproject.toml` (`uv upgrade`)" (open, 699 reactions). Latest uv release listed: 0.13.1 (2026-10-14).

## What is being asked
The reporter wanted something like conda's `update --all` for a virtual environment. He later clarified in the issue text that in project mode uv already covers this, and the open gap is plain virtual environments.

## The maintainers' breakdown (konstin's 2025-05-04 comment, quoted in substance)
1. Project mode, upgrade everything to compatible newer versions without editing `pyproject.toml`: `uv sync --upgrade`.
2. Project mode, upgrade to the latest versions and edit `pyproject.toml`: that is the separate request #6794, tentatively `uv upgrade`.
3. Plain venv, upgrade all installed packages:
   - with jq: `uv pip list --format=json | jq -r '.[].name' | uv pip install --upgrade -r -`
   - with Unix tools: `uv pip list | tail -n +3 | cut -d ' ' -f1 | uv pip install --upgrade -r -`
   He notes this can downgrade packages when dependencies conflict, and does not remove packages that are no longer needed.
4. Plain venv, upgrade only the packages you originally asked for: hard, because the environment does not record what was requested (the pip discussion is linked in his comment). Options he lists: `uv pip compile --upgrade` or `uv pip sync` with a package list, or recreating the env with `uv venv && uv pip install -r requirements.txt`.

A commenter (danielfleischer, 2026-09-18) offers a shorter variant for plain venvs: `uv pip install -U $(uv pip freeze | cut -d= -f1)`. That is one user's suggestion. It will behave differently for packages installed from URLs or editable installs, which I did not check.

## Status
- zanieb (an Astral maintainer in the thread, role not verified here) said in March 2024 that for this to move, a contributor must prototype it or the team must free time, and some design questions must be answered, including why it is not done in pip and what the intended behaviour is. On 2025-06-11 he opened two follow-up issues, 13968 and 13970 (both open, small).
- On 2026-10-17 a commenter, msminhas93, posted a design proposal titled `uv pip upgrade` for the plain-venv case (bucket 3) and said he plans a draft PR after a quick thumbs-up. I only read the first lines of it. No maintainer response to it is in the thread yet.

## Honest limits
- I did not run uv or any of the commands above. The commands are quoted from the thread, and their behaviour and caveats are the commenters'.
- I did not read the full text of the 2026-10-17 proposal or judge its design.
- Whether Astral will accept a `uv pip upgrade` command is not stated. The issue still carries `needs-design`.
- The 631-reaction count is from the API today and will change.
