# Dart: `dart format` still cannot exclude files, and a maintainer now plans to add it (dart-lang/dart_style#864)

- Source issue: https://github.com/dart-lang/dart_style/issues/864 "Add ability to exclude files". Opened 2019-10-21, open, label "enhancement". 102 reactions on the post, 60 comments, last updated 2026-10-19.
- Maintainer's plan, 2026-09-23: https://github.com/dart-lang/sdk/issues/64364 "Migrate dart_style to use the analyzer package for configuration", opened by a Dart team member (munificent), open.
- An outside contributor's pull request, https://github.com/dart-lang/dart_style/pull/1776 "Add exclude patterns for files and directories", opened 2025-10-11, closed without merging on 2026-04-21.
- Formatter docs, read 2026-10-19: https://dart.dev/tools/dart-format (the `formatter:` settings in `analysis_options.yaml` there cover `page_width` and `trailing_commas`; I saw no exclude setting in the lines I read).

## The problem
The reporter (2019) runs the formatter over a whole project and it also reformats generated files such as `*.g.dart`, which then flip between the generator's output and the formatted version. He asked for an exclude flag. Later users add cases: CI checks with `--set-exit-if-changed`, template files that are not valid Dart, committed generated localization files, and slow runs on big generated protobuf files.

## What the maintainer said, over time
- 2019 (munificent): he did not want to reimplement `find` inside the formatter, and suggested `find . -name '*.dart' -not -name '*.g.dart' -exec ... {} \;`. The reporter measured that running the tool once per file was much slower (his numbers: under 3 seconds for the whole tree, about 6.5 minutes one file at a time on 282 files, on Windows, in 2019). The maintainer's other suggestion was to format the generated files too, since that is harmless, and he said he would rather fix performance bugs than add a workaround feature.
- 2025-04-01: a file can opt out by putting `// dart format off` at its top (the maintainer's comment, in Dart 3.8 and later per another commenter). A commenter replied that this does not work for generated files you cannot edit.
- 2026-04-16 (on the closed PR): "Overall, yes, I would like to add support for file exclusions." He wants them stored in a config file, probably `analysis_options.yaml`, with IDEs plumbing the configuration in, and does not want a new constructor parameter for each IDE to fill in.
- 2026-09-23 (issue 64364): he says he intends to add file exclusions to the formatter, living in `analysis_options.yaml`, by first moving dart_style onto the analyzer package's config reading and then implementing exclusions once in the analyzer. A commenter on #864 (2026-10-13) quotes this as "the ball has finally started rolling".
- The issue 64364 text is a plan for a migration. It does not give a date, and I did not find a released exclude option.

## Other points in the thread
- Many workarounds from commenters: loop over files with `find`; run `dart format` with `--output none` and filter its output; generate, format, then commit; or in one 2026-10-13 comment, a user whose AI coding agents keep reformatting generated files describes the cause as the `source_gen` builder formatting its parts. I did not verify any of these.
- A commenter on 2026-06-11 argues the formatter should follow the analyzer's exclude list. The maintainer's plan to reuse `analysis_options.yaml` goes in that direction.
- The newest comment says the IDE-based objection from earlier years is weaker now. That is the commenter's opinion.

## What can be said
- As of the comments I read, the answer is still "no built-in exclude", but for the first time the formatter's owner has said it will be added and where the setting would go. Treat the design as a plan: it is unreleased, and the setting name is not decided in what I read.
- Until then, the per-file `// dart format off` and the `find` loops are what commenters use, with the slowness caveat the thread measured.

## Honest limits
- I did not run `dart format` or test any workaround.
- I read the issue and the PR comments, and only the start of issue 64364.
- The 2019 timings are the reporter's, from an old tool version.
