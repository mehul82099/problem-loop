# ElementTree presence is not the truth value of a found element

Date: 2026-11-05. A tested migration pattern for documented behavior, not a new XML parser defect.

## Research

The [ElementTree reference](https://docs.python.org/3/library/xml.etree.elementtree.html) says `find()` returns an element or `None`. It separately warns that elements without subelements test false and that truth testing emits `DeprecationWarning` starting in Python 3.12. [CPython issue 83122](https://github.com/python/cpython/issues/83122) records the confusion and warning discussion. A [developer question](https://stackoverflow.com/questions/20129996/why-does-boolxml-etree-elementtree-element-evaluate-to-false) shows why a found element can surprise code using an existence-style boolean check.

## Discussion

A leaf can contain text or attributes and still have no child elements. Therefore `if not found` conflates a missing match with a present leaf on the tested runtimes. `primary or fallback` has the same problem: a present leaf in the primary path can be replaced by the fallback.

Separate the questions. Use `found is None` to ask whether the search failed. After checking presence, use `len(found)` if the actual question is whether it has child elements. Text and attribute validation are separate again.

## Conclusion

Use an explicit None check before choosing a fallback. This avoids deprecated element truth testing without relying on when or how a future release will change it. This example concerns standard-library `xml.etree.ElementTree`, not lxml, XPath in general, or safe parsing of untrusted XML.

## Action: tested presence-aware fallback

The probe below passed 15 assertions each on CPython **3.13.17** and **3.14.9**, Linux x86_64. It checks missing, empty, text-only, attribute-only and parent elements; demonstrates the incorrect `or` fallback; captures the deprecation warnings; and verifies the replacement with those warnings promoted to errors. These are fresh, tiny in-memory XML strings, not external documents.

```python
import json
import platform
import warnings
import xml.etree.ElementTree as ET

def find_present(root, primary, fallback):
    found = root.find(primary)
    return root.find(fallback) if found is None else found

root = ET.fromstring('<root><empty/><text>yes</text><attr ok="1"/><parent><child/></parent><fallback>backup</fallback></root>')
empty, text, attr, parent = (root.find(name) for name in ('empty', 'text', 'attr', 'parent'))
assert root.find('missing') is None
assert empty is not None and len(empty) == 0
assert text is not None and text.text == 'yes' and len(text) == 0
assert attr is not None and attr.get('ok') == '1' and len(attr) == 0
assert parent is not None and len(parent) == 1
with warnings.catch_warnings(record=True) as seen:
    warnings.simplefilter('always', DeprecationWarning)
    assert bool(empty) is False
    assert bool(text) is False
    assert bool(attr) is False
    assert bool(parent) is True
    wrong = root.find('empty') or root.find('fallback')
assert wrong is root.find('fallback')
assert seen and all(issubclass(w.category, DeprecationWarning) for w in seen)
with warnings.catch_warnings():
    warnings.simplefilter('error', DeprecationWarning)
    assert find_present(root, 'empty', 'fallback') is empty
    assert find_present(root, 'text', 'fallback') is text
    assert find_present(root, 'missing', 'fallback') is root.find('fallback')
    assert find_present(root, 'missing', 'also_missing') is None
print(json.dumps({'python': platform.python_version(), 'result': 'passed', 'cases': 15}))
```

## Publisher checks and limits

- Original helper and finding are under the repository's MIT license. Linked reports retain their authorship.
- The old boolean result is asserted only for the two tested builds. No future release behavior or upstream issue resolution date is claimed.
- `find_present` is a two-path fallback, not a parser wrapper or schema validator. It inherits `find()` path and namespace behavior and returns None when both paths are missing.
- No network, files, hostile XML, resource limits, custom element classes, or alternate implementations were tested.
