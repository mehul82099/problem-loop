# LSP: a proposal to let language servers ask the user questions (LSP #1164)

- Source: https://github.com/microsoft/language-server-protocol/issues/1164 "Support refactors that require user input/options". Opened 2020-12-09, still open, 32 comments, 132 reactions on the opening post, last comment 2026-10-18.
- Design document linked from the thread: https://go.googlesource.com/proposal/+/refs/heads/master/design/76331-lsp-interactive-refactoring.md (read on 2026-10-18; it says "Last updated: 16 July 2026").
- Related closed issue: https://github.com/microsoft/language-server-protocol/issues/764 (how an "extract method" action could trigger a rename).

## The problem
The Language Server Protocol lets a server offer code actions, but a code action cannot ask the user anything. The opening post (from a Dart maintainer) names "move to file", extract method (needs a name), and inline method (keep or remove). Later commenters add Pylance (rename file, move symbol, which need a file name) and an "implement interface" action that needs an interface name. Each editor ends up with its own custom client code, which is the duplication the commenters complain about.

## How the thread got here
- 2020: people argue about how far the protocol should go. One commenter fears a "slippery slope" toward server-defined UI. Another says he dislikes form-based refactors and prefers in-place edits. Ideas include extra metadata on code actions, command variables, and a server-to-client request like `window/showMessageRequest`.
- 2022: Dart describes a workaround it already uses: parameter data in the code action plus client middleware that prompts the user and replaces arguments before the command runs.
- 2026-09-10: a commenter (h9jiang) posts a proposal on behalf of the Go and Dart teams. It is described there as backward compatible and "entirely stateless", like an HTML form.

## What the proposal says (from the comment and design doc, as written by its authors)
- A new request `command/resolve`. The client sends a command; the server answers either "nothing to ask" (the command comes back unchanged) or with `formFields` (questions, types, defaults, validation errors).
- The client collects answers and calls again with `formAnswers`, repeating until the server returns no fields. Only then does the client call `workspace/executeCommand` with the answers.
- New capabilities: `workspace.interactiveResolve` on the client and `interactiveResolveProvider` on the server.
- Stated reasons for stateless over a server-to-client request: the server holds no open request while a person fills in the form, there is no RPC timeout, and the client can continue with a restarted server.
- Stated downside list exists in the comment; I did not summarize it all here.

## Responses so far
- 2026-09-29: dbaeumer (marked MEMBER of the repo) says he likes the design and the design choices, and asks what makes the client send the first `command/resolve`. The author replies that it is a speculative first call, like `codeAction/resolve`. A Dart contributor adds that Dart-Code runs it as middleware on `executeCommand`, so it only fires when the user triggers the command.
- 2026-10-17 and 2026-10-18: maintainers of the Gleam and wgsl-analyzer language servers each comment that they like it and would use it.
- No comment I saw says the proposal is accepted, and nothing in the thread says it is in the spec.

## Honest limits
- This is a proposal discussion. I did not find a merged spec change, a pull request, or a timeline. A member saying "I do like the design" is not approval.
- I did not test the prototypes mentioned in the comment, did not read the full design doc beyond its opening, and did not check which editors would implement it.
- The "stateless is better" argument is the authors' own. Other designs were discussed in the thread and I did not weigh them.
