# Azure Pipelines: "Merge coverage reports from multiple runs" is still open after 7 years (azure-pipelines-tasks#10353)

- Source issue: https://github.com/microsoft/azure-pipelines-tasks/issues/10353 . Opened 2019-05-10, open, labels "enhancement", "Area: CodeCoverage", "stale". 83 reactions on the post, 62 comments, last comment 2026-10-19. The stale bot marked it stale several times; commenters kept replying "active". A project member reopened it on 2026-04-13 (comment: "Reopening the issue").
- Docs, read 2026-10-19: the v1 task page, https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-code-coverage-results-v1 , and the v2 task page, https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-code-coverage-results-v2 .

## The problem
A monorepo or a multi-project build produces several coverage files (for example one Cobertura XML per test project). `PublishCodeCoverageResults@1` with a wildcard path logs "Multiple file or directory matches were found. Using the first match" and shows only that file's numbers. The reporter wanted a summary per project, or a merged one.

## What the docs say now
- The v1 page has an FAQ entry that answers the question directly. Its text says the task's code coverage reporting is "limited, and it does not merge coverage data", that with multiple input files "only the first match is considered", and that with several publish tasks the report is shown for the last task.
- The same v1 page also says, in the description of the input, that "Multiple summary files are merged into a single report". Those two statements disagree on that page. A commenter in 2022 pointed out the same contradiction in the older docs and asked for the docs to be corrected.
- The v1 page says v2 "is the newest version of the task and should be used" and that v1 "will be deprecated".
- The v2 page says "Multiple summary files are merged into a single report", and that v2 supports many formats. I did not run v2, so I cannot say what the merged result looks like for overlapping files or different tools.

## What commenters did
- The workaround most people used was to merge the files first with the open-source ReportGenerator tool (run as a tool or via its Azure DevOps extension), then publish the one merged Cobertura file. Its author, who posted in the thread, gave sample YAML. People reported it working, and also reported failures. One project member (2023) found the tool saw only one input file, because his test step wrote every project's coverage to the same path so each run overwrote the last. Another commenter calls the approach a hack, since the last publishing task wins and templated pipelines are hard to coordinate.
- A 2021 comment suggests a v2 task already existed in the repo and was not yet published. The current docs show v2 as published, so that comment is out of date.
- Some commenters said their org could not install marketplace extensions, so an extension was not an option for them.

## What can be said
- Per Microsoft's own v1 docs FAQ, v1 does not merge. Per the v2 docs, v2 does. The issue itself is still open and I found no comment saying whether v2 closes it for the original reporter's case.
- If you are on v1 and see "Using the first match", the log message is accurate: only one file is used.
- This is not advice to change your pipeline. Moving to v2 changes the report format and prerequisites (the v2 page lists a .NET Core step), so try it on a branch.

## Honest limits
- I did not run either task version or ReportGenerator.
- I read the comments in full only up to 2023 and skimmed later ones. The issue thread does not show whether anyone verified v2 on a monorepo.
- I did not check what v2 does with duplicate files or mixed formats.
