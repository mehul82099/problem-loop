# Repeated regex captures do not keep a history of every iteration

Date: 2026-11-05. A tested capture-versus-extraction distinction, not a new regular-expression defect.

## Research

The [Python re reference](https://docs.python.org/3/library/re.html?highlight=re+finditer) says only the last match is accessible when a capturing group matches repeatedly. It separately documents finditer as yielding match objects for non-overlapping matches. [Regular-Expressions.info](https://www.regular-expressions.info/captureall.html) explains repeating a capture versus capturing a repeated block, and a [Python-focused guide](https://learnbyexample.github.io/py_regular_expressions/groupings-and-backreferences.html) illustrates the same trap.

## Discussion

In the example below, the full match contains RED,GREEN,BLUE but the repeated second group contains BLUE, not a list containing GREEN and BLUE. Moving parentheses around the repeated portion can capture that entire portion as one string; it does not produce a capture-history list in the standard re API.

For this tiny word-list grammar, validate the whole string first, then extract each word with finditer. Extraction alone is not validation: finditer can skip invalid text and still return plausible words. The final assertion demonstrates that exact failure mode. For this particular grammar, splitting a validated string on commas would also be simpler and sufficient.

## Conclusion

Choose between a whole repeated block and individual items before designing groups. If every item is needed, iterate individual matches or use a parser suited to the input. Keep validation separate when the whole input must obey a grammar. No third-party regex engine or capture-history extension is assumed here.

## Action: tested tiny word-list parser

Ran 14 cases each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover full-match contents, last repeated capture, three-word extraction, one word, duplicates, seven malformed inputs and the extraction-only counterexample. This deliberately accepts ASCII uppercase words separated by a single comma, without spaces, quoting, escaping or empty fields.

```python
import json
import platform
import re

# Deliberately tiny grammar: one or more ASCII uppercase words, comma-separated.
whole = re.compile(r'[A-Z]+(?:,[A-Z]+)*')
word = re.compile(r'[A-Z]+')

def parse_words(text):
    if whole.fullmatch(text) is None:
        raise ValueError('invalid word list')
    return [match.group(0) for match in word.finditer(text)]

m = re.fullmatch(r'([A-Z]+)(?:,([A-Z]+))*', 'RED,GREEN,BLUE')
assert m is not None
assert m.group(0) == 'RED,GREEN,BLUE'
assert m.groups() == ('RED', 'BLUE')
assert parse_words('RED,GREEN,BLUE') == ['RED', 'GREEN', 'BLUE']
assert parse_words('RED') == ['RED']
assert parse_words('A,A') == ['A', 'A']
for invalid in ('', ',A', 'A,', 'A,,B', 'A B', 'A,lower', 'A\n'):
    try:
        parse_words(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid input accepted')
assert [m.group(0) for m in word.finditer('A,broken,B')] == ['A', 'B']
print(json.dumps({'python': platform.python_version(), 'cases': 14, 'result': 'passed'}))
```

## Publisher checks and limits

- Original helper and finding use the repository's MIT license. Linked explanations retain their authorship.
- This is not CSV, a general tokenizer or a production input-validation policy. Different grammars need different validation and extraction rules.
- No file/network input, hostile large input, regex-timeout feature, benchmark, Unicode word policy or third-party engine was tested.
- The probe does not claim all regex extraction requires two passes. The two-stage design makes this particular grammar and failure mode explicit.
