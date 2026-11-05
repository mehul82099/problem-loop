# Query parsing can drop blank values unless the retention policy is explicit

Date: 2026-11-05. A tested urllib.parse usage distinction, not a new decoder defect.

## Research

The [urllib.parse reference](https://docs.python.org/3/library/urllib.parse.html) says parse_qs and parse_qsl ignore blank values by default; keep_blank_values=True retains them as empty strings. It documents dictionary values as lists and parse_qsl as returning name/value pairs. A [developer question about missing empty parameters](https://stackoverflow.com/questions/26473859/how-to-parse-empty-value-of-parameter-in-http-request-in-python) reports the surprise. A [discussion of empty form values](https://stackoverflow.com/questions/5230181/what-is-the-standard-for-application-x-www-form-urlencoded-and-an-empty-value) provides context; this finding claims Python behavior, not a universal standard-conformance verdict.

## Discussion

An absent parameter and a submitted empty value can mean different things to an application. Default parsing can collapse that distinction. Retaining blanks preserves the empty value, while parse_qs also retains repeated values in a list. Converting parse_qsl directly to dict instead keeps only one value per repeated name, which is a separate loss of information.

Blank retention does not preserve the exact original spelling. In permissive parsing, flag and flag= both produce the same empty value; plus signs and percent encoding are decoded. The round trip below preserves the decoded dictionary data, not byte-for-byte query text or the interleaving of different repeated names.

## Conclusion

Choose blank and duplicate-value policies before mapping a query into application settings. Use keep_blank_values=True when submitted empties matter. Do not present strict_parsing=True as a full URL, percent-encoding, schema or security validator: here it rejects a bare field while still accepting a normal explicitly empty assignment.

## Action: reproducible blank and repeated-value probe

Ran 12 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover default omission, retained blanks, absent keys, repeated pair order, dict collapse, strict bare-field rejection, space/plus decoding, empty query, permissive bare/empty equivalence, decoded-data round trip with doseq and a field-count limit.

```python
import json
import platform
from urllib.parse import parse_qs, parse_qsl, urlencode

query = 'mode=&tag=one&tag=&tag=two&flag'
assert parse_qs(query) == {'tag': ['one', 'two']}
kept = parse_qs(query, keep_blank_values=True)
assert kept == {'mode': [''], 'tag': ['one', '', 'two'], 'flag': ['']}
assert 'absent' not in kept
assert parse_qsl(query, keep_blank_values=True) == [
    ('mode', ''), ('tag', 'one'), ('tag', ''), ('tag', 'two'), ('flag', '')]
assert dict(parse_qsl(query, keep_blank_values=True))['tag'] == 'two'
assert parse_qs('a=', keep_blank_values=True, strict_parsing=True) == {'a': ['']}
try:
    parse_qs('flag', keep_blank_values=True, strict_parsing=True)
except ValueError:
    pass
else:
    raise AssertionError('bare field accepted in strict mode')
assert parse_qs('q=a+b&literal=%2B', keep_blank_values=True) == {'q': ['a b'], 'literal': ['+']}
assert parse_qs('', keep_blank_values=True) == {}
assert parse_qs('flag', keep_blank_values=True) == parse_qs('flag=', keep_blank_values=True)
encoded = urlencode(kept, doseq=True)
assert parse_qs(encoded, keep_blank_values=True) == kept
try:
    parse_qs(query, keep_blank_values=True, max_num_fields=4)
except ValueError:
    pass
else:
    raise AssertionError('field limit was ignored')
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked reports retain their authorship.
- Synthetic query strings only. No real request, endpoint, credential, user data or network traffic is used.
- The input is a query string, not an entire URL. This is not signature canonicalization, duplicate-parameter authorization policy, request validation or an application parser.
- No malformed percent sequences, invalid Unicode, alternative separators, bytes input, huge input, framework behavior or benchmark was tested. max_num_fields is demonstrated, not claimed to cover all resource risks.
