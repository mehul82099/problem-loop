# Vitest: an invalid `maxWorkers` runs zero tests and exits 0 - a silent green CI

**Source:** https://github.com/vitest-dev/vitest/issues/11844 (opened 2026-11-03 UTC, open, no maintainer reply yet)

## The problem

If the worker count comes out zero or negative - `VITEST_MAX_WORKERS=0`, `VITEST_MAX_WORKERS=-1`, or `--maxWorkers=-1` - Vitest prints its `RUN` banner, runs no tests, writes no report, and exits with code 0. The reporter maps the whole inconsistent matrix on vitest 5.1.0 (verified as the current npm release): `--maxWorkers=1.5` runs one file then dies with `Cannot set concurrency id because there are no valid free ids`; a non-numeric `VITEST_MAX_WORKERS=abc` fails with an unrelated projects-config error; `VITEST_MAX_WORKERS=4 --no-file-parallelism` overrides the fileParallelism clamp because the env var is read after it; and only the literal flag `--maxWorkers=0` does the sensible thing, falling back to the default. The repro is four shell commands.

## Why it matters

Test runners are the last line of defense, and exit code 0 is the only signal CI trusts. A misspelled or zero-valued worker setting - easy to produce from an unset env var in a pipeline (`VITEST_MAX_WORKERS=$EMPTY_VAR` arithmetic is a classic) - turns the entire test stage into a no-op that reports success. The suite could be deleted entirely and the build would stay green. The scattered behavior for other invalid values shows there is no single validation point for this option, which is why the same input class produces four different outcomes.

## Caveats

- Open with no maintainer response; reporter association NONE. The repro is minimal and the behavior matrix is detailed, but these are the reporter's results on one Linux setup; this finding verified the vitest version exists as claimed and did not re-run the matrix.
- This finding does not propose a fix; consistent validation and a non-zero exit for unusable worker counts is the report's ask.
