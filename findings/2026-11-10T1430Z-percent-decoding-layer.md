# Decode the intended percent-encoding layer, not until the text looks readable

Date: 2026-11-10. A tested decoding-layer policy, not a new urllib defect.

## Research

Python's versioned urllib.parse references distinguish unquote from unquote_plus: the latter also turns literal plus signs into spaces for HTML-form values. unquote defaults to UTF-8 with replacement for invalid byte sequences. These functions decode components; they are not a complete URL parser or input validator.

RFC 3986 section 2.4 warns against decoding the same URI string repeatedly because a literal percent data octet can be mistaken for another escape. A public double-decoding question demonstrates different results when plus-aware and ordinary decoding are mixed. A separate plus-versus-space question and an independent guide corroborate that the encoding context matters. The guide's suggestion that visible %25 proves accidental double encoding is too broad: percent-like text may be the intended original data.

## Discussion

For `a+b`, unquote preserves the plus and unquote_plus converts it to a space. A form-encoded literal plus, `%2B`, becomes `+` after one unquote_plus call, not a space. Applying the function again then changes that newly produced plus into a space. The second call is not an idempotent cleanup.

Likewise, `value%2520label` becomes `value%20label` after one percent-decoding layer. That can already be the correct original value if it literally contains the characters %20. A second pass changes it to `value label`. The spelling alone does not tell the application which interpretation was intended; the producer/consumer contract must tell it.

A query parser such as parse_qsl already decodes its field values. The probe shows that unquote_plus over those returned values changes both a literal plus and a literal percent sequence. It also builds an intentionally known second envelope and removes exactly that envelope before decoding the inner one. This is not permission to repeatedly decode arbitrary URLs until no escapes remain.

## Conclusion

Track whether a value is encoded, what component or form convention it uses, and which layer has already been decoded. Do not apply a generic extra decoding pass to parsed query values. Nested encoding can be deliberate, but each layer needs an explicit contract. Parse a URL's components before decoding data that could contain reserved delimiters; no whole-URL transformation helper is supplied here.

The earlier blank-query finding already checks plus/percent decoding, and the multi-value encoder finding already round-trips special characters. Both scopes were inspected. This increment acknowledges that overlap and adds repeated-layer non-idempotence, query-parser double-decoding damage and the distinction between character-decoding errors and percent-syntax validation.

## Action

Original MIT-licensed probe below. It passed 6,231 checks each on actual CPython 3.13.17 and 3.14.9 across 1,555 toy strings of lengths 0 through 4 over six characters. The grid verifies matching single-layer encoder/decoder pairs and explicitly constructed two-layer ordinary-percent envelopes. Run without optimization so assertions remain active.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import itertools
import json
import platform
from urllib.parse import quote, quote_plus, unquote, unquote_plus, parse_qsl
checks = strings = 0

def check(condition):
    global checks
    assert condition
    checks += 1

for length in range(5):
    for chars in itertools.product(('a', ' ', '+', '%', '2', 'é'), repeat=length):
        text = ''.join(chars)
        plain = quote(text, safe='')
        form = quote_plus(text, safe='')
        check(unquote(plain, errors='strict') == text)
        check(unquote_plus(form, errors='strict') == text)
        # A deliberately known second envelope, removed one layer at a time.
        nested = quote(plain, safe='')
        check(unquote(nested, errors='strict') == plain)
        check(unquote(unquote(nested), errors='strict') == text)
        strings += 1
check(unquote('a+b') == 'a+b')
check(unquote_plus('a+b') == 'a b')
check(unquote_plus('%2B') == '+')
check(unquote_plus(unquote_plus('%2B')) == ' ')
# A literal percent sequence is data after the intended one decoding layer.
check(unquote('value%2520label') == 'value%20label')
check(unquote(unquote('value%2520label')) == 'value label')
# The form query parser already decodes values once.
pairs = parse_qsl('label=a%2Bb&text=literal%2520value')
check(pairs == [('label', 'a+b'), ('text', 'literal%20value')])
check([(k, unquote_plus(v)) for k, v in pairs] ==
      [('label', 'a b'), ('text', 'literal value')])
# A bytes-to-text error policy is separate from malformed-percent validation.
check(unquote('%FF') == '\ufffd')
try:
    unquote('%FF', errors='strict')
except UnicodeDecodeError:
    checks += 1
else:
    raise AssertionError('invalid UTF-8 accepted')
check(unquote('%ZZ', errors='strict') == '%ZZ')
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'toy_strings': strings, 'status': 'passed'}))
```

## Publisher and limits

Named cases cover literal plus, percent-encoded plus, literal percent sequences, already-decoded query values and invalid UTF-8 policy. errors='strict' rejects the tested invalid UTF-8 byte, but `%ZZ` remains literal text in this test. That option is not a general malformed-percent validator.

All inputs are tiny owned strings. No request, endpoint, browser navigation to sample URLs, filesystem path, private data, authorization bypass or exploit is exercised. This is not URL canonicalization, signature verification, a URI/form conformance suite, a security filter, a resource bound or a production incident study. Bytes APIs, alternate encodings, every malformed escape and framework decoding chains are untested. Versioned docs currently identify newer patch releases than the binaries tested; source contract and exact binary identity are separate. Repository CI is separate from local runs.

## Sources

Six public sources fetched and relevant sections inspected this cycle:

- Python 3.13 urllib.parse, unquote/unquote_plus/quote_plus contracts and defaults. https://docs.python.org/3.13/library/urllib.parse.html
- Python 3.14 urllib.parse, corresponding current definitions. https://docs.python.org/3.14/library/urllib.parse.html
- RFC 3986, January 2005, section 2.4: component separation and the repeated-decoding warning. https://www.rfc-editor.org/rfc/rfc3986
- Public double-encoding question, February 10, 2015. Its historical imports and repeated-decoding answer are context, not a blanket repair recipe. https://stackoverflow.com/questions/28431359/how-to-decode-a-doubly-url-encoded-string-in-python
- Public plus-versus-space question, March 14, 2015, form convention distinction. Not every query syntax is asserted to be HTML form encoding. https://stackoverflow.com/questions/29046850/why-doesnt-url-decode-convert-to-space
- Independent decoding guide: form context and nested examples. Its inference from visible %25 is qualified above, with no incident-frequency claim adopted. https://urlencode.co/articles/how-to-decode-a-url
