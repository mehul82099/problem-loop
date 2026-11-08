# Unicode comparison keys need a named equivalence policy

Date: 2026-11-08. Evidence-backed Python finding, not a new Unicode defect.

## Research

The Python Unicode HOWTO gives a canonical caseless comparison recipe: normalize to NFD, casefold, then normalize to NFD again. Lowercasing alone does not implement case folding, and folding alone does not equate canonically equivalent composed and decomposed text. The Unicode normalization FAQ distinguishes canonical equivalence from compatibility equivalence, which can erase additional distinctions.

## Discussion

`Straße` and `STRASSE` differ after lowercasing but match after case folding. A composed `é` and `e` plus a combining acute accent can still differ after case folding alone. Combining both operations addresses a different contract: canonical caseless equality.

Order matters. The probe includes canonically equivalent Greek combining-mark sequences that differ if case folding is done before the initial decomposition. It uses the full HOWTO recipe rather than assuming one normalization call can always be removed.

There is no universal "normalize everything" policy. An independent article recommends NFKC as a general identifier-oriented default, while the HOWTO gives NFD-based canonical caseless comparison. These serve different equivalence goals. This finding deliberately preserves compatibility distinctions such as circled digit one versus ordinary digit one. It does not strip accents or implement language-specific Turkish casing rules.

## Conclusion

| Intended comparison | Candidate policy | Boundary |
| --- | --- | --- |
| Exact code-point sequence | Ordinary string equality | Different canonical representations remain different |
| Default caseless only | `casefold()` | Does not itself normalize canonical representations |
| Canonical caseless | NFD, casefold, NFD | Merges case/canonical variants; not all compatibility variants |
| Identifier or locale-specific matching | Follow the system's explicit specification | Do not substitute this generic key for its rules |

Keep the original text for display. Treat a comparison-key collision as an application decision, not permission to overwrite a record. The example groups originals under keys so collisions remain visible. This is not a username migration, authentication fix, locale collation algorithm, spoofing defense, or proof that visually similar strings should match.

## Action: diagnostic and collision-preserving example

Standard-library-only code. Original code is covered by the repository MIT license. The source uses visible text plus explicit escapes for combining-mark examples.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform
import unicodedata as ud

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

def canonical_key(text):
    return ud.normalize('NFD', ud.normalize('NFD', text).casefold())

check('Straße'.lower() != 'STRASSE'.lower())
check('Straße'.casefold() == 'STRASSE'.casefold())
check('é' != 'e\u0301')
check('é'.casefold() != 'e\u0301'.casefold())
check(canonical_key('É') == canonical_key('e\u0301'))
check(canonical_key('Σ') == canonical_key('ς'))
check(canonical_key('Σ') == canonical_key('σ'))
# Canonically reordered marks must be handled before case folding.
a = '\u03b1\u0345\u0301'
b = '\u03b1\u0301\u0345'
check(ud.normalize('NFD', a) == ud.normalize('NFD', b))
check(ud.normalize('NFD', a.casefold()) != ud.normalize('NFD', b.casefold()))
check(canonical_key(a) == canonical_key(b))
# Explicit limits: not accent stripping, compatibility folding, or locale rules.
check(canonical_key('e') != canonical_key('é'))
check(canonical_key('①') != canonical_key('1'))
check(ud.normalize('NFKC', '①') == '1')
check(canonical_key('I') == canonical_key('i'))
check(canonical_key('İ') != canonical_key('i'))
check(canonical_key('ı') != canonical_key('I'))
# Preserve originals in collision buckets, rather than silently overwrite.
originals = ['Straße', 'STRASSE', 'É', 'e\u0301']
buckets = {}
for original in originals:
    buckets.setdefault(canonical_key(original), []).append(original)
check(len(buckets) == 2)
check(buckets[canonical_key('strasse')] == ['Straße', 'STRASSE'])
check(buckets[canonical_key('é')] == ['É', 'e\u0301'])
check(originals == ['Straße', 'STRASSE', 'É', 'e\u0301'])
for sample in originals + [a, b, '①', 'İ', 'ς']:
    check(canonical_key(canonical_key(sample)) == canonical_key(sample))
    check(ud.is_normalized('NFD', canonical_key(sample)))
print(json.dumps({'python': platform.python_version(),
                  'unicode_database': ud.unidata_version, 'checks': checks}))
```

## Validation

Executed **38 checks per build** on CPython **3.13.17** (Unicode database **15.1.0**) and **3.14.9** (Unicode database **16.0.0**). Both passed. Checks include lower-versus-fold distinction, canonical composition, sigma forms, a normalization-order counterexample, accent/compatibility/locale limits, visible collision buckets, and idempotent NFD output for the selected samples.

The versions intentionally report their database versions: these selected samples agree across the two builds, but that is not a claim that all mappings are identical across Unicode versions. Persisted comparison keys require a version and migration policy. This finite sample is not Unicode conformance testing. Repository CI is separate.

## Publisher and sources

Published deliverable: this finding and runnable diagnostic. All six pages were read. These are longstanding documented distinctions, not evidence of a new regression or measured production incident rate.

1. [Python 3.14 Unicode HOWTO](https://docs.python.org/3.14/howto/unicode.html), primary documentation: canonical caseless recipe and why normalization appears twice.
2. [Python 3.14 unicodedata](https://docs.python.org/3.14/library/unicodedata.html), primary reference: normalization forms and database version.
3. [Python 3.14 string methods](https://docs.python.org/3.14/library/stdtypes.html#str.casefold), primary reference: case folding is more aggressive than lowercase conversion.
4. [Unicode normalization FAQ](https://unicode.org/faq/normalization.html), standards publisher: canonical versus compatibility equivalence and information loss.
5. [Case-insensitive comparison question](https://stackoverflow.com/questions/319426/how-do-i-do-a-case-insensitive-string-comparison), community evidence: multiple answers choose different matching policies. They are not interchangeable universal fixes.
6. [Compare strings the right way](https://www.b-list.org/weblog/2023/dec/23/compare-python-strings/), independent article, 2023-12-23: equivalence and identifier-oriented NFKC advice. Its broader default is not silently substituted for the narrower canonical policy here.
