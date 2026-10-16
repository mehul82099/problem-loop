# ASP.NET Core Minimal APIs: one endpoint that fails to build can turn every route into a 500

- Cycle: 2026-10-16T1030Z
- Source: https://github.com/dotnet/aspnetcore/issues/69826
- Reporter's probe repo (named in the issue, not run by me): https://github.com/robertodalmonte/csharp-unions-probed
- State when checked: open, opened 2026-10-14, label `area-minimal`, 4 comments, last activity 2026-10-16 07:42 UTC. A team member has answered and does not plan a change in .NET 11.

## The report

The reporter, testing .NET 11 `11.0.100-rc.2` (and RC1, so pre-release builds), says that one Minimal API endpoint taking a C# union type that `System.Text.Json`'s structural classifier refuses to classify makes endpoint building throw. After that, a request to any route in the app, even `GET /ok` with no union, returns 500. Their table says:

- Minimal API only: startup succeeds, every route returns 500 on the first request.
- With `AddControllers()` plus the bad endpoint, or with `AddAuthorization()`: startup throws instead.
- The same bad union on an MVC action: only that action fails, other routes return 200.

They agree the classifier rejecting the type is by design. Their question is only about scope: should one bad endpoint take the whole table down?

## The team's answer (thread claims)

- A member says it is not specific to unions. An unregistered service parameter on a `MapGet` can be inferred as a body parameter and fail endpoint construction in the same way, and GET bodies are deliberately rejected.
- They do not think the behavior should change this late in .NET 11, because isolating failures needs a broader look at endpoint construction errors, and evaluating endpoints at startup would change when user code runs. They are open to revisiting after .NET 11, with better diagnostics and opt-in early validation as starting points.
- The reporter agrees, adds that endpoints are often built at startup anyway through authorization, and asks for a backlog milestone. No reply to that yet.

## Practical reading

If your Minimal API app suddenly returns 500 on every route, including simple ones, a single endpoint with a parameter the framework can't bind could be the cause. That is my reading of the thread, not a tested fix.

## Why this was picked

The failure is far from its cause, and the thread has a clear answer on whether it will change soon. Few people would guess that an unrelated route's parameter breaks `/ok`.

## Honest limits

- Nothing was run. The examples and table are from the issue.
- This is about RC builds, and the final release may behave differently.
- "Not changing in .NET 11" is one member's statement, not a release decision I have verified.
