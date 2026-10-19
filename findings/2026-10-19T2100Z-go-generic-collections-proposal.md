# Go: umbrella proposal for generic collection types (golang/go#80590)

- Source: https://github.com/golang/go/issues/80590 "proposal: container/...: generic collection types". Opened 2026-07-28 by a Go team member (adonovan), open, label "Proposal", milestone "Go1.28". 270 reactions on the post, 107 comments, last updated 2026-10-19. The top post carries update notes dated 7 and 13 October 2026 by another Go team member (jba), so it has changed since it was opened.
- Linked proposals named in the post: #70471 (hash/maphash.Hasher, marked as released in go1.27), #69559 (hashed Map), #80584 (hashed Set), #69230 (set.Set), #60630 (ordered/sorted Map and Set), #77397 (generic heap), #80194 (insertion-ordered hash maps). I did not open each of these. The post says a `mapset` package that was originally proposed has been withdrawn.

## What it proposes (from the post, as read on 2026-10-19)
- A working group formed in late 2025 (the post names seven Go team members) wants to add common data structures to Go: hash-based maps and sets with custom hash and equality, a standard set type, ordered (tree-based) maps and sets, a new generic heap, and maps that iterate in insertion order. It says queues and stacks may follow.
- The post says the new packages will live in `golang.org/x/exp` first, "to give the community ample time for feedback", with the hope of eventually adding them to the standard library. Package names and paths differ between the post (`x/collection/...`) and comments (`container/hash`, `container/ordered`, `container/set`). This looks like a naming that is still in flux, which is one of the thread's complaints.
- The post also describes unexported "abstract" constraint interfaces, added only to check that the types conform in tests, and says they are not part of the proposal.

## What the thread says
- 2026-07-28 (a contributor, willfaught, several replies with 11 to 12 reactions): a lot of API to vet and little shared experience designing Go collections, so ship in `x/exp`, gather feedback, and move to the standard library only after the design settles. He also questions the package naming. A contributor (neild, 19 reactions) lists the proposed types and says the package names have no consistent rule, and that `container/hash` shares a name with the existing `hash` package.
- 2026-07-29: a project member (aclements) reports from proposal review that `DeleteAll` could be confused with `Clear`, and that the meaning of the `bool` results of `DeleteAll` and `SetAll` is unclear. He says that in the prototype `DeleteAll` returns whether at least one item was deleted, and `SetAll` whether the count went up.
- 2026-10-08: a member says the proposal was added to the active column of the proposal review list. A commenter asked about release timing. jba answered that if approved before Go 1.28 ships, the types would be in `x/exp` before 1.28 and "will not be in the stdlib before 1.29 (if ever)".
- Early October: a thread on how maps and sets should encode as JSON. Points raised: sets as arrays have no natural order, so output could be non-deterministic; one author says json/v2 has an option to control this and v1 would always sort; another notes the sorting problem for types with no ordering.
- 2026-10-16: a commenter asked to keep the types outside the standard library permanently. A team member (adonovan) answered that parts of the standard library would want to use them and share implementations (for example with the runtime's map). Another member (mvdan) said they should go in std because they are not niche and will be stable once settled. These are their stated views, not decisions.
- 2026-10-19 (latest): a commenter suggests making the abstract interfaces read-only to make ownership clearer.

## What can be said
- This is a design in review, not accepted. The thread has no accept or decline decision as of the last comments I read. Names, package paths and some method semantics are still being discussed. Details in this note may be out of date after the next revision of the post.
- The one thing in the post marked as already released is the hasher in go1.27, which I did not verify against the Go release notes.

## Honest limits
- I did not try any of the prototype code or check the linked change lists.
- I read the top post, the reaction-heavy and Go team comments, and the latest ones, not all 107.
- I did not open the linked sub-proposals, so their individual status is not checked.
