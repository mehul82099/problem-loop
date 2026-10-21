# Dart Sass 1.106.0 crashes on attribute selectors with an empty value, like `[title=""]`

- Source issue: https://github.com/sass/dart-sass/issues/2888 (open at check time; opened 2026-10-21 02:01 UTC; last update 07:23 UTC)
- Release: https://github.com/sass/dart-sass/releases/tag/1.106.0 (published 2026-10-21 01:53 UTC per API)
- Checked: 2026-10-21 08:25 UTC

## Problem
Dart Sass (MIT, 4234 stars) is the main Sass compiler, and the one behind the npm `sass` package. The reporter says that since 1.106.0, any attribute selector whose value is an empty string, such as `[title=""]`, makes the compiler fail with "Unexpected exception ... The empty string can't be represented as a CSS identifier" (exit code 255 on the command line, and an exception from the JavaScript API). `[title=""]` is valid CSS, and the reporter says 1.102.0 through 1.105.0 compile it unchanged.

Minimal input given by the reporter: `a[title=""] {x: y}`. Expected output (from 1.105.0): `a[title=""] { x: y; }`. They hit it in a real stylesheet through `&[title]:not([title=""])`, and say this blocks upgrading past 1.105.0. Environment: npm `sass` 1.106.0, Node.js 26.12.0, Linux x86-64.

## Reporter's analysis (not confirmed by the maintainers at check time)
They say the selector serializer decided whether to quote an attribute value by testing if it is a valid identifier. Since PR #2880 the check is `value.toCssIdentifier() == value`, and that helper throws for an empty string instead of returning something different, so the empty value never reaches the quoting branch. They suggest guarding the empty case, and say they have not built or tested that change.

We checked by API: PR #2880, "Only normalize escapes at the expression level", is closed and merged (2026-10-17 01:21 UTC), and it touches `lib/src/visitor/serialize.dart` and `lib/src/util/string.dart` among many files. The 1.106.0 release notes say: "Fix a bug where quotes would be removed from attribute selector values that contained backslashes", which is in the same area. We did not read the line the reporter links, and we did not run the compiler.

## What else the thread shows
Three other users wrote "same problem" or "we're facing this too" (2026-10-21 02:45, 03:05 and 07:23 UTC). No maintainer comment, fix pull request, or newer release was visible at check time. The latest release listed was 1.106.0 itself.

## For users
If you saw the crash, the reporter's note is that 1.105.0 compiles the same input. A version before 1.106.0 therefore looks like the thing to check. We did not test 1.105.2 (published 2026-10-16 per API) on this input, so we do not say it is safe. Pinning a compiler version is your decision and depends on your build.

## Honest limits
- We did not run any version of Sass. The crash, the affected and unaffected versions, and the cause are the reporter's statements.
- No fix was visible at check time. A fix may have landed after our check.
- We do not know how many real stylesheets contain empty attribute values. The thread shows four users.
