# PowerShell: converting a string to System.Text.Rune, and why `[char]` is not enough (PowerShell#28222)

- Source: https://github.com/PowerShell/PowerShell/issues/28222 "In from-string conversions, also honor `IParsable<T>` interface implementations, not just public static `Parse` methods" (open, labels Issue-Enhancement, WG-Engine, Needs-Triage; opened 2026-10-16 by mklement0, who is marked CONTRIBUTOR; 6 comments when read)
- Earlier request it builds on: https://github.com/PowerShell/PowerShell/issues/27596 "Allow convertion from string consisting of single code point to `System.Text.Rune`" (open, opened 2026-06-12, 10 comments)
- .NET documentation read on 2026-10-18: https://learn.microsoft.com/en-us/dotnet/api/system.text.rune
- Latest PowerShell release shown by the GitHub API: v7.6.7. I do not have PowerShell or .NET in my sandbox, so I ran nothing here.

## The feature request
The issue title was changed during the discussion (at GeeLaw's suggestion) to say PowerShell should honour `IParsable<T>`. The author's argument: a .NET type that implements the `IParsable<TSelf>` interface says it can be built from a string through a static `Parse` method. PowerShell's string conversion, as the author describes it, only looks for a public static `Parse` method on the type itself. A type that implements the interface "explicitly" has no such public method, so PowerShell ignores it. The author's example is `System.Text.Rune`, which he says implements `IParsable<Rune>` from .NET 11 on, so `[System.Text.Rune] '👍'` fails today and would work if PowerShell honoured the interface. I checked the .NET documentation page: it lists `IParsable<Rune>` and the `IParsable<Rune>.Parse` method for `Rune`. It does not show me what PowerShell does, so the claim about PowerShell's behaviour is the author's.

## Why Rune exists (explained by commenters)
- A .NET `char` is one 16-bit UTF-16 unit, so it cannot hold characters outside the Basic Multilingual Plane, such as 👍 (U+1F44D). `[char]"😀"` fails with "String must be exactly one character long", as shown in issue 27596.
- A `Rune` holds one Unicode code point, so it can hold such characters. Today the way to get one from a string, shown in 27596, is `"😀".EnumerateRunes()[0]`.
- GeeLaw (no repository association) and the author explained that a string that looks like one symbol can still be several code points, for example `☀️` (U+2600 plus U+FE0F) or an "e" followed by a combining accent. Those would not convert to a single `Rune`, and the proposal only covers a string that is exactly one code point.
- One commenter (237dmitry) asked why `[Text.Rune]::new(0x2600, 0xfe0f)` errors. GeeLaw answered that the two-argument form takes a surrogate pair, and that this string is one grapheme but two code points, so it does not fit in one `Rune`. The author asked everyone to hide the off-topic comments to keep the thread focused.

## Status
No maintainer has replied in the comments I read. The label `Needs-Triage` means nobody had triaged it as of my reading. Nothing is decided.

## Honest limits
- I did not test any PowerShell behaviour. What PowerShell currently does comes from the issue text and the quoted sessions in 27596.
- I did not check which .NET version first added `IParsable<Rune>`; the "from .NET 11" statement is the author's. The documentation page I read lists the interface but I did not check a version selector.
- I did not read the full comment history of 27596.
