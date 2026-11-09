# Character translation does not reprocess its replacement text

Date: 2026-11-09. Evidence-backed Python finding, not a new string-processing defect.

## Research

Public Python questions describe character swaps failing when implemented as a chain of str.replace calls. Each replace receives the previous call's output. By contrast, str.translate maps each source character through a table. A mapping from a to b and b to c turns source 'ab' into 'bc'; the sequential replace chain can turn it into 'cc'. These are different contracts, not interchangeable spelling styles.

## Discussion

| Operation on 'ab' | Tested result | Meaning |
| --- | --- | --- |
| translate with a->b, b->c | bc | Map source characters without translating produced text again |
| replace a->b, then b->c | cc | Second operation sees the first operation's output |
| replace b->c, then a->b | bc | This example agrees, but relies on operation order |
| translate with a->b, b->a | ba | Swap original character identities without a temporary sentinel |

Translation can expand one source code point into several, remove it with None or an empty string, or leave an unmapped code point unchanged. An expansion such as a->bb does not then trigger b->c inside the same translation call. A caller that wants cascading rewrite stages should keep those stages explicit rather than replacing them with a non-cascading table.

The table interface is another boundary. str.translate indexes its table by integer Unicode ordinals, so {'a': 'b'} supplied directly does not replace 'a' in the tested case. str.maketrans converts one-character string keys to ordinal keys. Its string keys must have length one, although replacement strings can have arbitrary length. It is not a simultaneous multi-word replacement engine.

A source character here means a Unicode code point, not a user-perceived grapheme. The probe changes the e in an e-plus-combining-accent sequence while retaining the combining mark. No Unicode normalization, case-insensitive matching, token boundary or grapheme-preservation policy follows from using translate. Those need separate requirements.

## Conclusion

For deliberate per-code-point remapping, build a table once and translate the original text. For deliberate sequential rewriting, preserve the chosen order and test cascading cases. For multi-character patterns, first specify overlap, match priority, token boundaries and whether generated text can match again; do not pass multi-character keys to maketrans and expect a parser.

The toy helper accepts exact str/dict inputs, single-code-point string keys, and string-or-None values. It deliberately rejects integer keys and integer replacement ordinals even though the built-ins support them. Unknown source characters are preserved, not rejected. This is a narrow transformation helper, not validation or escaping. No speed advantage is claimed or benchmarked.

## Action: bounded pure-text diagnostic

Original standard-library-only code under the repository MIT license. No file, network or account effects. Run without -O so assertions remain enabled. The exhaustive portion compares all 341 strings of length 0 through 4 over a four-character alphabet with three independent per-character oracle mappings.

```python
# Original pure-text probe, MIT license (repository LICENSE).
import itertools
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

def raises(kind, operation):
    try:
        operation()
    except kind:
        check(True)
    else:
        raise AssertionError(f'expected {kind.__name__}')

def translate_once(text, replacements):
    # Deliberately narrower than maketrans: exact str keys/str-or-None values.
    if type(text) is not str or type(replacements) is not dict:
        raise TypeError('expected str and dict')
    if any(type(k) is not str or len(k) != 1 for k in replacements):
        raise ValueError('keys must be single-code-point strings')
    if any(v is not None and type(v) is not str for v in replacements.values()):
        raise TypeError('values must be str or None')
    return text.translate(str.maketrans(replacements))

mapping = {'a': 'b', 'b': 'c'}
check(translate_once('ab', mapping) == 'bc')
check('ab'.replace('a', 'b').replace('b', 'c') == 'cc')
check('ab'.replace('b', 'c').replace('a', 'b') == 'bc')
check(translate_once('ab', {'a': 'b', 'b': 'a'}) == 'ba')
check(translate_once('a', {'a': 'bb', 'b': 'c'}) == 'bb')
check(translate_once('a-b?', {'a': '', '-': None}) == 'b?')
check('a'.translate({'a': 'b'}) == 'a')  # Raw table needs ordinal keys.
check('a'.translate({ord('a'): ord('b')}) == 'b')
check(str.maketrans({'a': 'b'}) == {ord('a'): 'b'})
check(translate_once('x🙂', {'🙂': 'OK'}) == 'xOK')
check(translate_once('e\u0301', {'e': 'E'}) == 'E\u0301')
raises(ValueError, lambda: str.maketrans({'ab': 'x'}))
raises(ValueError, lambda: translate_once('ab', {'ab': 'x'}))
raises(ValueError, lambda: translate_once('', {'': 'x'}))
raises(ValueError, lambda: translate_once('a', {97: 'x'}))
raises(TypeError, lambda: translate_once('a', {'a': 98}))
raises(TypeError, lambda: translate_once(None, {}))
raises(TypeError, lambda: translate_once('a', []))
check(translate_once('', {}) == '')
check(translate_once('ab', {}) == 'ab')

# Exhaustive small source alphabet vs an independent per-character oracle.
# The replacement strings are never fed back into this oracle.
for size in range(5):
    for chars in itertools.product('abx-', repeat=size):
        text = ''.join(chars)
        for table in ({'a': 'b', 'b': 'a'}, {'a': 'bx', 'x': None, '-': ''},
                      {'a': 'aa', 'b': 'a', 'x': '-'}):
            expected = ''.join((table[ch] or '') if ch in table else ch
                               for ch in text)
            check(translate_once(text, table) == expected)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

1,043 checks passed separately on CPython 3.13.17 and 3.14.9: 1,023 bounded exhaustive comparisons and 20 focused cases. Cases cover cascade/order differences, swapping, expansion, deletion, unknown-character preservation, raw ordinal tables, a non-BMP code point, a combining sequence, empty input and rejected helper contracts. These are semantic checks, not performance, normalization or arbitrary-text correctness guarantees.

## Sources

1. [Python 3.13 built-in types](https://docs.python.org/3.13/library/stdtypes.html#str.translate): translate/maketrans/replace contracts. Exact sections inspected from the full page after the general fetch stopped early.
2. [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html#str.translate): corroborating versioned contracts.
3. [Character replacement chain question](https://stackoverflow.com/questions/60607645/replacing-characters-by-chaining-str-replace-methods-produces-wrong-result), 2020-03-09: independent user example of generated text being replaced again.
4. [Multi-character translation table question](https://stackoverflow.com/questions/52420009/custom-table-for-str-translate-in-python-3), 2018-09-20: independent evidence of confusion between one-character source keys and arbitrary replacement length.
5. [Python interface discussion](https://discuss.python.org/t/nicer-interface-for-str-translate/30434), 2023-07-28: primary discussion of ordinal tables, maketrans and proposed alternatives. Proposals and performance anecdotes are not adopted as guarantees.
6. [Programiz translate tutorial](https://www.programiz.com/python-programming/methods/string/translate): independent mapping/deletion examples; official references govern the more general string-expansion contract.

The contribution is an original boundary probe and explicit contract, not a claim that non-cascading translation is newly discovered. The earlier exact-affix finding concerns stripping versus removing fixed affixes, not character translation.
