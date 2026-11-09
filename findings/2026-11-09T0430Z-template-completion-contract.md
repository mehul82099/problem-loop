# safe_substitute is partial rendering, not a completion check

Date: 2026-11-09. Evidence-backed Python finding, not a new Template defect.

## Research

Python's string.Template.safe_substitute deliberately keeps missing placeholders in the output. The versioned references also warn that it silently tolerates malformed placeholders. Returning a string therefore proves neither valid source syntax nor complete source-field substitution. The public identifier-inspection issue describes this exact visibility gap, and Python 3.11 added is_valid and get_identifiers to inspect it directly.

This is the long-standing dollar-placeholder string.Template class. It is not Python 3.14's unrelated t-string / string.templatelib.Template feature.

## Discussion

For '$name / ${missing} / $$', supplying only name produces 'Ada / ${missing} / $' with safe_substitute, while substitute raises KeyError. Inputs such as a dangling dollar or unmatched brace also survive safe_substitute in the tested cases but fail strict substitution. The word "safe" refers to forgiving substitution, not proof that a notification, report or configuration is ready to use.

| Check or method | What it tells you | What it does not tell you |
| --- | --- | --- |
| is_valid() | Placeholder syntax is valid | Values exist for every name |
| get_identifiers() | Unique valid names, in first-appearance order | Invalid syntax is absent; invalid placeholders are ignored |
| substitute(values) | Strict substitution succeeded for this call | Output is escaped for HTML, a shell, SQL or another target |
| safe_substitute(values) | A forgiving substitution returned | Every source placeholder was filled or source syntax was valid |

Checking the result for a dollar sign is not a completion check either. '$$name' legitimately renders as '$name', and a replacement value can itself be '$other'. In the probe those replacement dollars are not recursively substituted. Validate the original template and field coverage rather than treating every dollar-shaped sequence in output as a missing source field. Do not add repeated substitution passes to "finish" it unless a separate format deliberately requires them.

The default placeholder pattern uses ASCII identifier-shaped names, but it is not Python-expression evaluation. The probe accepts a mapping key named 'class'. One independent tutorial describes names as excluding Python keywords; that claim is not adopted here. The versioned default pattern and the actual test support this narrower distinction. Extra mapping keys are ignored by ordinary substitute; rejecting them below is an additional toy reporting rule, not a built-in requirement.

## Conclusion

Use forgiving substitution when partial output is explicitly wanted. For a plain-text output that must fill every source field, first reject malformed syntax, inspect required names, compare them with the supplied mapping, then substitute. Keep output-context escaping and field-value validation separate. A successfully substituted '<tag>' remains '<tag>' in this probe; neither method supplies an HTML-escaping policy.

The helper defines "complete" only as valid default Template syntax plus exact supplied source names. It accepts exact built-in str/dict objects with string keys and values and rejects unexpected as well as missing keys. It does not ban literal dollar signs in values or output. It is not an HTML renderer, shell-command builder, localization framework, authorization check or general sandbox. Template subclasses and custom placeholder grammars are outside its contract.

## Action: string-only diagnostic and exact-field helper

Original code under the repository MIT license. No files, network, task execution or account effects. The controlled BrokenMapping demonstrates that safe_substitute can still propagate exceptions unrelated to a missing key. Run without -O so assertions remain enabled.

```python
# Original string-only diagnostic, MIT license (repository LICENSE).
from string import Template
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

def render_complete(source, values):
    # Toy plain-text contract: exact built-in str/dict, string keys/values.
    if type(source) is not str or type(values) is not dict:
        raise TypeError('expected str source and dict values')
    if any(type(k) is not str or type(v) is not str for k, v in values.items()):
        raise TypeError('string keys and values required')
    template = Template(source)
    if not template.is_valid():
        raise ValueError('malformed template')
    required = set(template.get_identifiers())
    supplied = set(values)
    if required != supplied:
        raise ValueError({'missing': sorted(required - supplied),
                          'unexpected': sorted(supplied - required)})
    return template.substitute(values)

t = Template('$name / ${missing} / $$')
check(t.is_valid())
check(t.get_identifiers() == ['name', 'missing'])
check(t.safe_substitute(name='Ada') == 'Ada / ${missing} / $')
raises(KeyError, lambda: t.substitute(name='Ada'))
check(t.substitute(name='Ada', missing='ready') == 'Ada / ready / $')

for source in ('end $', '${unfinished', '$9bad', '${bad-name}'):
    t = Template(source)
    check(not t.is_valid())
    check(t.safe_substitute({}) == source)
    raises(ValueError, lambda: t.substitute({}))
    raises(ValueError, lambda: render_complete(source, {}))

# Identifier collection is not a validity check and deduplicates names.
t = Template('$b $a ${b} $9bad')
check(t.get_identifiers() == ['b', 'a'])
check(not t.is_valid())
check(Template('$class').substitute({'class': 'keyword key'}) == 'keyword key')
check(Template('$name').substitute({'name': 'mapping'}, name='keyword') == 'keyword')

# Substitution is single-pass: values and escaped dollars can look like slots.
check(render_complete('$name', {'name': '$other'}) == '$other')
check(render_complete('$$name', {}) == '$name')
check(Template('$$name').get_identifiers() == [])
check(Template('$name').substitute(name='<tag>') == '<tag>')
check(render_complete('${noun}ification', {'noun': 'test'}) == 'testification')
check(render_complete('$x / $x', {'x': 'ok'}) == 'ok / ok')
check(render_complete('', {}) == '')
check(Template('$x').substitute({'x': 'ok', 'unused': 'ignored'}) == 'ok')
raises(ValueError, lambda: render_complete('$x', {'x': 'ok', 'unused': 'extra'}))
raises(ValueError, lambda: render_complete('$x $y', {'x': 'ok'}))
for source, values in ((None, {}), ('ok', []), ('$x', {'x': None}),
                       ('$x', {1: 'one'})):
    raises(TypeError, lambda: render_complete(source, values))

# 'safe' does not catch arbitrary exceptions from user-defined mappings.
class BrokenMapping(dict):
    def __getitem__(self, key):
        raise RuntimeError('controlled lookup failure')
raises(RuntimeError, lambda: Template('$x').safe_substitute(BrokenMapping()))
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'status': 'passed'}, sort_keys=True))
```

## Verification

40 checks passed separately on CPython 3.13.17 and 3.14.9. Tests cover missing fields, four malformed forms, validity versus identifier discovery, duplicate-name ordering, keyword-shaped mapping keys, mapping/keyword precedence, escaped dollars, replacement dollars, literal angle brackets, braced suffixes, empty input, ignored built-in extra keys versus rejected helper extras, wrong helper input types and a controlled mapping exception. No rendered messages were sent or used as executable input.

## Sources

1. [Python 3.13 string reference](https://docs.python.org/3.13/library/string.html): Template substitution, malformed-input caveat, default pattern and inspection methods.
2. [Python 3.14 string reference](https://docs.python.org/3.14/library/string.html): same contracts and distinction from t-strings.
3. [PEP 292](https://peps.python.org/pep-0292/): original rationale, missing-field behavior and dollar/braced syntax; modern API details follow versioned docs.
4. [Identifier-inspection issue 46307](https://bugs.python.org/issue46307), opened 2022-01-08: primary use cases for discovering all required names instead of only the first missing key. Early proposals in the discussion are not current API guarantees.
5. [Real Python string interpolation tutorial](https://realpython.com/python-string-interpolation/), 2024-06-03: independent partial-substitution example. Its Python-keyword restriction description is not used as the default Template contract.
6. [Independent inspection-method demo](https://gist.github.com/benkehoe/3fd5c2ca04093618f486c42d87e9cb1c), 2023-06-23: corroborates checking validity separately from collecting names. The code here was written independently and is not copied from that demo.

The contribution is a reproducible boundary probe and narrow completion contract, not a newly discovered defect or a claim that forgiving templates should always be rejected.
