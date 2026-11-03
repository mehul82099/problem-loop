# uv: `link-mode = "symlink"` breaks Apple's mlx on macOS because @rpath resolves against the cache, not the venv

**Source:** https://github.com/astral-sh/uv/issues/23072 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

With `link-mode = "symlink"` set, `uv run python -c "import mlx.core"` fails with `ImportError: Library not loaded: @rpath/libmlx.dylib`. The repro is four lines: init a project, set the link mode, `uv add mlx`, import. With `clone` or `copy` the same import works. The reporter is on uv 0.13.6 (verified release, 2026-10-27) on Apple Silicon, and mlx is Apple's own machine-learning framework (verified on PyPI).

The mechanism is a known macOS loader behavior meeting a cache optimization. Under symlink link-mode, the native extension `core.cpython-313-darwin.so` in the venv is a symlink into uv's global archive cache. dyld resolves `@loader_path`-relative rpath entries against the real file location - the cache directory - not the symlink's location in the venv. The quoted loader trace shows it trying `<cache>/archive-v0/<hash>/mlx/lib/libmlx.dylib` and the managed-Python lib dir, none of which hold the dylib in the cache's layout, while the venv-relative location where it does exist is never consulted. So the same wheel that imports fine when copied cannot find its own bundled library when referenced through a symlink.

## Why it matters

`link-mode = "symlink"` gets recommended for saving disk and install time in multi-project setups, and mlx is the standard way to run models on Apple Silicon - the intersection is anyone doing local LLM work on a Mac with several venvs. The failure mode is confusing: installation succeeds, the file is visibly "there" in site-packages, and only the dynamic loader knows the layout is wrong. The report's implicit ask - resolve rpaths appropriately or document the limitation - applies to any package shipping dylibs next to its extensions, so mlx is likely the most visible instance rather than the only one.

## Caveats

- Open with no maintainer response; reporter association NONE. The repro is self-contained and the loader error is quoted verbatim; this finding verified the uv release, the mlx package, and the existence of the documented setting, but did not re-run the repro.
- Whether other dylib-bundling packages are affected is untested here.
- This finding does not propose a fix; whether symlink mode can or should handle this is a maintainer decision.
