# Perl blead: a regex like /$$foo[0]/ matches differently under `use strict`

- Source issue: https://github.com/Perl/perl5/issues/24977 (open at check time; labels: Bug, type-regex; opened 2026-10-19)
- Related issue: https://github.com/Perl/perl5/issues/24789 (open; "BBC: Blead breaks Text-Beautify-0.08", opened 2026-09-02)
- Checked: 2026-10-21 02:20 UTC

## Problem
The reporter says that in a development build of Perl (the `blead` branch, version 5.45.4 per their `perl -V`), this one-liner prints "yes" without `use strict` and "no" with it:

    @main::bar = ("a","b"); $main::bar = "c"; my $foo = *bar;
    print "a" =~ /$$foo[0]/ ? "yes" : "no"

Without strict the regex is read as the first element of the array behind `$foo`, so it matches "a". Under strict, a commenter's `re "debug"` output shows the pattern compiled as `c[0]` (scalar `$$foo` followed by a literal character class) so it cannot match "a". The whole thing is about how the lexer decides whether `[` after an interpolated variable in a regex is a subscript or part of the pattern.

## What the thread says (all from commenters labelled CONTRIBUTOR by GitHub; none quoted by name here)
- One commenter checked a 5.44.0 build: it prints "yes" under strict, so the change came after 5.44.0.
- A bisect with Perl's `Porting/bisect.pl` between v5.44.0 and blead was reported to point to commit 6aef1e87c1e, "intuit_more: Pass context to it in another instance". We confirmed by API that this commit exists, dated 2026-07-17, touching `toke.c` and `t/re/pat.t`. We did not rerun the bisect.
- A commenter suggested a regression test for `t/re/pat.t`. It is a suggestion, not a merged change.
- In the older issue #24789 (a CPAN module that breaks on blead), a commenter had earlier traced a similar failure to the same area and said they did not yet know how to fix it without reverting the `intuit_more` changes.
- On 2026-10-20, one commenter framed the real question: should `use strict` change parsing at all? They said they had always assumed a working strict program behaves the same without strict, and that if the new behaviour is intended the report is not a bug. Two other commenters agreed with that assumption and saw no benefit to the new behaviour, with one calling it a footgun. These are opinions in a discussion, not a decision. No core developer answer was visible in this thread at check time.

## Why it may matter
Only blead (a development branch) is described as affected. The 5.44.0 test run does not show it. Whether a stable release will carry it depends on the unresolved decision above, and nothing we read says it will.

## Honest limits
- We did not build or run Perl. All behaviour comes from commenters' pasted output.
- The root cause statement is commenters' analysis. The thread did not show a maintainer ruling or a fix.
- We did not check whether #24977 and #24789 will be treated as duplicates. A commenter hinted they might be.
- The repo license shows as NOASSERTION in the API (GitHub could not detect one; Perl uses its own dual license). 2347 stars at check time.
- No advice is given for production code. If your code uses `$$ref[0]` inside regexes, test on the Perl version you use.
