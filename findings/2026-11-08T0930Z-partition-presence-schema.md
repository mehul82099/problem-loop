# partition's middle field distinguishes missing separators from empty values

Date: 2026-11-08. Scope: Python str.partition and str.rpartition with literal nonempty separators.

## Research

A community question reports unpacking failures when split() does not find a delimiter. The official partition contract returns a three-element tuple: text before the first separator, the separator itself, and text after it. If absent, the result is (original, '', ''). Unlike split(sep, 1), its successful return shape stays fixed even without a match.

## Discussion

Fixed shape does not mean a valid record. For 'key=', the separator exists but the suffix is empty. For 'key', it does not exist and the suffix is also empty. Checking only the suffix cannot tell those cases apart. An answer to another public question uses if not value as an absent-separator check; that shortcut conflates a missing separator with a present separator followed by an empty value. Check the middle element when separator presence is the question, then validate empty keys or values separately according to the data contract.

With multiple occurrences, partition selects the first; rpartition selects the last. Their missing-separator layouts differ: partition puts the original in the first element, rpartition puts it in the last. The middle element remains the presence signal in both. A multi-character separator is a literal string, not a set of delimiter characters or a regular expression. Surrounding whitespace is preserved, not normalized.

The independent guides support the fixed triple and separator retention. Community performance language is not adopted: this finding does not benchmark these methods or rank them by speed. The earlier whitespace-split finding covered separator policy and limits; this increment covers fixed result shape and the missing-versus-empty distinction.

## Conclusion

For a literal one-boundary parse, unpack before, matched_separator, after = text.partition(sep). Decide whether no separator is acceptable by checking matched_separator, not the truthiness of after. Then apply the actual record rules. A fixed tuple cannot validate required fields, reject extra delimiters or understand quoting and escaping. Use the format's parser when those rules exist.

## Action

The original MIT-licensed diagnostic passed 35 checks each on CPython 3.13.17 and 3.14.9. It tests empty input, missing separator, empty sides, repeated separators, first/last behavior, literal multi-character matching, retained whitespace, rejoining, empty-separator rejection and split's variable-length unpacking. It is not a CSV, address, email or protocol parser and makes no performance claim.

```python
# Original diagnostic probe, MIT license (repository LICENSE).
import json
import platform

checks = 0

def check(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

cases = [('', ('', '', '')), ('key', ('key', '', '')),
         ('key=', ('key', '=', '')), ('=value', ('', '=', 'value')),
         ('=', ('', '=', '')), ('key=value=tail', ('key', '=', 'value=tail'))]
for text, expected in cases:
    parts = text.partition('=')
    check(parts, expected)
    check(len(parts), 3)
    check(''.join(parts), text)
    check(bool(parts[1]), '=' in text)

check('key=value=tail'.rpartition('='), ('key=value', '=', 'tail'))
check('key'.rpartition('='), ('', '', 'key'))
check('key='.partition('=')[2] == 'key'.partition('=')[2], True)
check('key='.partition('=')[1] == 'key'.partition('=')[1], False)
check('key'.split('=', 1), ['key'])
check('key='.split('=', 1), ['key', ''])
check('key=value=tail'.split('=', 1), ['key', 'value=tail'])
check('a<>b<>c'.partition('<>'), ('a', '<>', 'b<>c'))
check(' a = b '.partition('='), (' a ', '=', ' b '))
try:
    'abc'.partition('')
except ValueError:
    checks += 1
else:
    raise AssertionError('empty separator accepted')
try:
    left, right = 'key'.split('=', 1)
except ValueError:
    checks += 1
else:
    raise AssertionError('missing delimiter did not break two-value unpacking')
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Publisher

One evidence-backed finding and deterministic probe. Documented behavior, not a new defect or an upstream patch. No private data, external packages or network calls are needed by the probe. Run without optimization so assertions remain active.

## Sources

Six public pages inspected this cycle:

- Official Python 3.14 partition/rpartition contract. The fetched full-page text ended before the methods, so both exact HTML sections were separately retrieved and inspected: https://docs.python.org/3.14/library/stdtypes.html#str.partition
- Independent split/partition comparison with missing and last-occurrence examples: https://learnbyexample.github.io/tips/python-tip-25/
- Public first-occurrence question and presence checks: https://stackoverflow.com/questions/6903557/splitting-on-first-occurrence
- Public empty-value question; suffix-based absence shortcut qualified above: https://stackoverflow.com/questions/71330028/key-value-how-to-handle-null-python
- Independent reference for fixed triple and nonempty separator: https://python-academy.org/en/handbook/str.partition
- Independent method guide and missing separator examples: https://livingwithcode.com/python/string/methods/partition/

The CPython implementation page fetch timed out and is not used as supporting evidence.
