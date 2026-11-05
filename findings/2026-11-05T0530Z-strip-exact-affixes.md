# strip arguments are character sets, not exact prefixes or suffixes

Date: 2026-11-05. A tested text-transformation distinction, not a new string-method defect.

## Research

[PEP 616](https://peps.python.org/pep-0616/) records repeated confusion about lstrip/rstrip interpreting an argument as a set of characters, motivating removeprefix/removesuffix. A [public prefix-removal question](https://stackoverflow.com/questions/4148974/removing-a-prefix-from-a-string) illustrates the mistake, and an [independent method comparison](https://renanmf.com/python-lstrip-vs-removeprefix-and-rstrip-vs-removesuffix/) demonstrates the difference on both ends.

## Discussion

`'ABBAreport'.lstrip('AB')` removes leading A and B characters until a different character occurs, giving report. It does not look for one literal AB prefix. The order of the argument characters does not matter. A string beginning BA can therefore be changed even though it does not start with AB.

For an exact affix, removeprefix/removesuffix remove at most one matching substring at the corresponding end. They leave a nonmatching input unchanged. Repeated AB prefixes are not all removed in one call, and an empty suffix leaves the input unchanged rather than slicing it to an empty string. strip removes matching character-set members from both ends, so using it for one exact prefix can also alter the suffix.

## Conclusion

Choose the transformation contract explicitly: a run of characters from a set, or a single exact affix. Neither operation validates the entire input or makes it safe as a path or identifier. This finding recommends the existing exact-affix methods for that specific requirement, not a new wrapper around them.

## Action: reproducible method-choice probe

Ran 14 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe covers character-set stripping, exact and nonmatching affixes, one-copy removal, both-end stripping, empty affixes, character-order independence and case-sensitive prefix matching. Only synthetic ASCII strings are used.

```python
import json
import platform

assert 'ABBAreport'.lstrip('AB') == 'report'
assert 'ABBAreport'.removeprefix('AB') == 'BAreport'
assert 'BAreport'.lstrip('AB') == 'report'
assert 'BAreport'.removeprefix('AB') == 'BAreport'
assert 'ABABreport'.removeprefix('AB') == 'ABreport'
assert 'reportBAAB'.rstrip('AB') == 'report'
assert 'reportBAAB'.removesuffix('AB') == 'reportBA'
assert 'reportBA'.removesuffix('AB') == 'reportBA'
assert 'ABreportAB'.strip('AB') == 'report'
assert 'ABreportAB'.removeprefix('AB') == 'reportAB'
assert 'report'.removeprefix('') == 'report'
assert 'report'.removesuffix('') == 'report'
assert 'ABBAreport'.lstrip('BA') == 'ABBAreport'.lstrip('AB')
assert 'Report'.removeprefix('re') == 'Report'
print(json.dumps({'python': platform.python_version(), 'cases': 14, 'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked explanations retain their authorship.
- No files are renamed and no URL or path is parsed. This is not directory traversal protection, extension validation or canonicalization.
- No Unicode normalization/case-folding policy, bytes variants, subclass behavior, repeated-removal loop or performance benchmark was tested.
- These are documented methods with different jobs. The result is an evidence-backed usage correction, not an upstream bug report or a newly discovered vulnerability.
