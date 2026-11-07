# urlencode needs an explicit multi-value query representation

## Research
Python's urlencode defaults to doseq=False. Passing a list as a mapping value then encodes its string representation as one value, rather than producing repeated query fields. With doseq=True, sequence elements become separate key=value pairs. Public array-encoding questions show the difference between a syntactically valid encoded query and the data model the caller intended.

## Discussion
The probe contrasts a list encoded as one value with a list expanded into repeated tag fields. Strings and bytes remain scalar values rather than splitting into characters. An ordered sequence of key/value pairs can express repeated names directly without doseq. It can also preserve cross-key interleaving; grouping the same data into a dictionary of lists and re-encoding groups each key's values together instead.

Square brackets in a key are literal key text to urllib.parse, not an automatic array schema. The test encodes tag[] and parses it back as the key 'tag[]'. An endpoint may assign brackets special meaning, but that is its own contract, not an encoder guarantee. Percent-encoding handles characters inside values; hand-joining unquoted values is unnecessary. One explicit blank value is also distinct from a missing collection of values.

## Conclusion
Choose the endpoint's repeated-value format, then encode that representation. Use doseq=True for nonempty list/tuple values when repeated fields are intended, or explicit ordered pairs when pair order/interleaving matters. Do not assume a server interprets every repeated key or bracketed name as a list. Current Python 3.14 docs deprecate acceptance of false-valued objects such as 0 and []; this probe intentionally uses strings, bytes and nonempty collections rather than recommending deprecated input shapes. This is documented encoding behavior, not a new defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory strings and query parsing only; no HTTP requests. Run without Python optimization so assertions remain enabled.

```python
from urllib.parse import urlencode, parse_qs, parse_qsl
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

values = ['red', 'blue']
scalar = urlencode({'tag': values})
check(parse_qs(scalar) == {'tag': [str(values)]})
expanded = urlencode({'tag': values}, doseq=True)
check(expanded == 'tag=red&tag=blue')
check(parse_qs(expanded) == {'tag': ['red', 'blue']})
check(urlencode({'tag': ('red', 'blue')}, doseq=True) == expanded)
check(urlencode({'tag': 'red'}, doseq=True) == 'tag=red')
check(urlencode({'tag': b'red'}, doseq=True) == 'tag=red')

pairs = [('tag', 'red'), ('sort', 'name'), ('tag', 'blue')]
encoded = urlencode(pairs)
check(encoded == 'tag=red&sort=name&tag=blue')
check(parse_qsl(encoded) == pairs)
check(parse_qs(encoded) == {'tag': ['red', 'blue'], 'sort': ['name']})
# Grouping into a dict of lists does not retain cross-key interleaving.
check(urlencode(parse_qs(encoded), doseq=True) == 'tag=red&tag=blue&sort=name')
check(urlencode(parse_qs(encoded), doseq=True) != encoded)

special = [('tag', 'a&b'), ('tag', 'x+y'), ('tag', 'two words'), ('tag', 'café')]
wire = urlencode(special)
check(parse_qsl(wire) == special)
check('a%26b' in wire and 'x%2By' in wire and 'two+words' in wire)
check(urlencode({'tag[]': values}, doseq=True) == 'tag%5B%5D=red&tag%5B%5D=blue')
check(parse_qs(urlencode({'tag[]': values}, doseq=True)) == {'tag[]': values})

blank = urlencode({'tag': ['']}, doseq=True)
check(blank == 'tag=')
check(parse_qsl(blank, keep_blank_values=True) == [('tag', '')])
check(parse_qsl(blank) == [])
check(values == ['red', 'blue'])
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 19 checks passed on CPython 3.13.17 and 3.14.9.
- Covers default list stringification, list/tuple expansion, scalar strings/bytes, ordered repeated pairs, dictionary grouping, special-character round trips, literal bracketed keys, an explicit blank value and unchanged input collection.
- Does not test endpoint/framework interpretation, arbitrary generators or nested structures, deprecated false-valued object inputs, signatures, canonical URL spelling, server parameter limits or actual network delivery. Blank retention is included only as a boundary check; the earlier query-blank finding treats that parser policy in detail.

## Sources
- [Python 3.14 urllib.parse](https://docs.python.org/3.14/library/urllib.parse.html): doseq expansion, tuple order, quoting and 3.14 deprecation notice.
- [CPython urllib.parse, 3.14 branch](https://github.com/python/cpython/blob/3.14/Lib/urllib/parse.py): scalar string/bytes and sequence handling context; not exact tested-build identity.
- [urlencode an array of values](https://stackoverflow.com/questions/2571145/urlencode-an-array-of-values): public question about repeated fields and explicit pairs. Historical Python 2 imports are not used here.
- [CPython issue 77871](https://github.com/python/cpython/issues/77871): May 30, 2018 discussion distinguishing empty collections from a blank value. Historical acceptance is not advice to rely on shapes now marked deprecated.
- [WebDevData urlencode reference](https://www.webdevdata.net/reference/python/stdlib/urllib-parse/urlencode): independent explanation of default stringification and repeated-pair representation. Its broad input claims are not extended beyond the tested shapes.
- [Same key with multiple values](https://stackoverflow.com/questions/70562569/django-python-urlencode-same-key-with-multiple-values): community application question; only the standard-library representation is tested here, not Django behavior.
