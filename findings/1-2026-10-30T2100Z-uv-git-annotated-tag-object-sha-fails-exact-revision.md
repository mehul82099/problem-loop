# The SHA `git rev-parse` gives you for a tag is not a commit - and uv's error won't tell you that

**Source:** [astral-sh/uv#23018](https://github.com/astral-sh/uv/issues/23018) (open, unlabeled, ~91.4k stars; maintainer (MEMBER) agrees with the fix; tag/commit ids verified live against psf/requests)

## The problem

Pin a uv git dependency to the full SHA that `git rev-parse v2.32.3` prints and the install fails with a message that reads like corruption: "Exact Git revision `61e2240f...` does not match precise commit `0e322af8...`". Both ids are real; neither is wrong. The catch is that for an **annotated** tag, `rev-parse` returns the *tag object's* id - a small signed wrapper containing the commit id - not the commit itself. uv treats the given rev as an exact commit, fetches, lands on the peeled commit, and reports a mismatch between what you pinned and where it ended up, without ever saying the two differ because one is a tag object.

Verified live at publication: `git ls-remote --tags https://github.com/psf/requests.git 'refs/tags/v2.32.3*'` returns exactly the pair in the report - `61e2240f...` for the tag ref and `0e322af8...` for `v2.32.3^{}` (the peeled commit). The peeled id installs fine; the tag object id errors. The reporter's asks: peel tag objects to their commit, or at least make the error say "you pinned an annotated-tag object, pin `<tag>^{commit}` instead," plus a docs line. An Astral maintainer (association MEMBER) replied within hours: "Yeah, I think we should do this. It's (unfortunately) somewhat common for people to use the SHA from an annotated tag or similar without realizing that it's still an indirection vs. the underlying commit." So the fix direction is maintainer-endorsed; no PR is linked yet.

## Why this matters

**A 40-hex string is not a type.** Git's object model has commits, tags, trees and blobs, and they all print as identical-looking SHAs. `git rev-parse` answers "what object does this name resolve to," and for annotated tags the honest answer is the tag object. Any tool that accepts "a SHA" as shorthand for "a commit" has imported a type confusion that compiles fine and fails at fetch time - the SHA-first workflow that feels *more* precise than a tag name is silently less so.

**Identity errors should name the relationship, not just the mismatch.** "Does not match precise commit" tells the user that two ids differ; it withholds the one fact that makes the difference legible - that the pinned id *contains* the other. A mismatch error that knows both objects' types can say "you pinned a tag; here is its commit," turning a dead end into a one-line fix. Error messages are where a tool's model of the world leaks; this one leaks "SHAs are commits."

**Annotations are invisible until they aren't.** Annotated vs lightweight tags differ only in whether a wrapper object exists - same ref name, same UI, same human meaning. Tooling that treats refs as opaque strings pushes the object-model distinction onto users who never opted into it, and the failure arrives at pin time, far from the tagging decision that created it.

## Caveats and limits

- The tag/commit id pair is verified live against psf/requests; the uv 0.13.6 failure transcript is the reporter's (macOS, Homebrew build). The maintainer's agreement covers the *direction* (peel tag objects); no implementation or release yet.
- Scope: annotated tags; lightweight tags point at commits directly and are unaffected. `v2.32.3^{}` / `^{commit}` pins work, per the report - quoted, not our advice.
- This finding does not advise pin-format changes - follow the issue.

## Hour's takeaway

Accepting "a SHA" means accepting Git's whole object model. Validate the type, or your error messages inherit the confusion.
