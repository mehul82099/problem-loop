# Choose None's query meaning before URL encoding

Date: 2026-11-11. A small explicit policy adapter, not a new urllib defect.

## Research

[Python issue 18857](https://bugs.python.org/issue18857) asks why urlencode turns None into the text "None". It is closed, resolution "wont fix". The discussion considers empty assignments and omission, with backward compatibility central to leaving the historical behavior unchanged. This report does not adopt its broad claims about every URI or endpoint.

The [Python 3.10 reference](https://docs.python.org/3.10/library/urllib.parse.html) documents encoded key=value pairs and pair ordering. The [3.14 reference](https://docs.python.org/3.14/library/urllib.parse.html) includes a deprecation notice for accepting false-valued objects such as 0 and [], with listed exceptions. Our adapter passes only normalized text pairs to urlencode, not raw numeric or boolean values.

Different libraries can deliberately choose different policies. The [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/) says None-valued params keys are omitted from the URL. The historical [Requests issue 378](https://github.com/psf/requests/issues/378) distinguishes params from data and warns that truthiness conversion loses zero. It is not evidence that all current Requests arguments behave identically. [Django tests at a fixed revision](https://github.com/django/django/blob/f2f52289/tests/utils_tests/test_http.py) expect None query values to raise TypeError and ask the caller to choose an empty string or omission. Framework behavior is source context only, not locally executed here.

## Discussion

An application may mean three different things by None: leave the setting unspecified, submit an explicit empty value, or fail because required information is missing. No encoder can choose that application meaning by looking at None alone. Likewise "false", "0", and a blank are legitimate values for some endpoints, not proof that a field is absent.

The example's endpoint contract is deliberately narrow: exact built-in text keys, text values unchanged, booleans as lowercase true/false, integers as decimal text. None requires a keyword selecting omit, empty, or error. This boolean spelling is an example contract, not a universal API convention. Repeated pairs retain their order. Unsupported values fail instead of invoking arbitrary objects' string conversion.

## Conclusion

Use an explicit None policy and a schema agreed with the receiving endpoint. Do not filter with `if value` or replace every false value with an empty string. If the endpoint expects 1/0 booleans or another representation, change the contract and tests first. Omit and empty intentionally discard different information; neither is a reversible typed serialization. A literal string "None" stays text and still encodes as x=None.

## Action

Original MIT code below. Run `python3 query_none_policy.py`. The 27-case matrix crosses nine scalar values with three None policies. Additional controls cover historical stdlib None stringification, false-value preservation, required policy selection, unsupported types, malformed pairs, repeated keys, escaping, tuple inputs and unchanged input pairs. These are in-memory fixtures only: no server, HTTP, dependency install, credentials or user data.

```python
# Original example policy adapter and diagnostic, MIT licensed.
from urllib.parse import urlencode, parse_qsl
import json
import platform


def encode_pairs(pairs, *, none_policy):
    """Example endpoint contract: lowercase booleans, decimal ints, text.

    None must explicitly mean omit, empty, or error. Repeated pairs keep order.
    Exact built-in types only; no implicit conversion of arbitrary objects.
    """
    if none_policy not in ('omit', 'empty', 'error'):
        raise ValueError('unknown None policy')
    if type(pairs) not in (list, tuple):
        raise TypeError('pairs must be a list or tuple')
    normalized = []
    for pair in pairs:
        if type(pair) not in (list, tuple) or len(pair) != 2:
            raise TypeError('expected two-element pairs')
        key, value = pair
        if type(key) is not str:
            raise TypeError('keys must be text')
        if value is None:
            if none_policy == 'omit':
                continue
            if none_policy == 'error':
                raise ValueError('None needs an application value')
            text = ''
        elif type(value) is str:
            text = value
        elif type(value) is bool:
            text = 'true' if value else 'false'
        elif type(value) is int:
            text = str(value)
        else:
            raise TypeError('unsupported value type')
        normalized.append((key, text))
    return urlencode(normalized)


checks = 0

def check(condition):
    global checks
    if not condition:
        raise AssertionError('check failed')
    checks += 1


def rejects(exception, function):
    global checks
    try:
        function()
    except exception:
        checks += 1
    else:
        raise AssertionError('expected rejection')


# Historical stdlib behavior is measured only on the named installed build.
check(urlencode({'x': None}) == 'x=None')
check(parse_qsl(urlencode({'x': None})) == [('x', 'None')])
values = [(None, None), ('', ''), (False, 'false'), (True, 'true'),
          (0, '0'), (-2, '-2'), ('None', 'None'), ('a&+ b', 'a&+ b'),
          ('caf\u00e9', 'caf\u00e9')]
for policy in ('omit', 'empty', 'error'):
    for value, expected in values:
        pairs = [('start', 'one'), ('x', value), ('start', 'two')]
        snapshot = list(pairs)
        if value is None and policy == 'error':
            rejects(ValueError, lambda: encode_pairs(pairs, none_policy=policy))
        else:
            wire = encode_pairs(pairs, none_policy=policy)
            wanted = [('start', 'one')]
            if value is not None or policy == 'empty':
                wanted.append(('x', '' if value is None else expected))
            wanted.append(('start', 'two'))
            check(parse_qsl(wire, keep_blank_values=True) == wanted)
            check(type(wire) is str and wire.isascii())
            check(encode_pairs(tuple(pairs), none_policy=policy) == wire)
        check(pairs == snapshot)

# Truthiness is not a None check: this drops 0, False and explicit blank text.
raw = [('missing', None), ('zero', 0), ('disabled', False), ('blank', '')]
check([k for k, v in raw if v] == [])
check(parse_qsl(encode_pairs(raw, none_policy='omit'), keep_blank_values=True)
      == [('zero', '0'), ('disabled', 'false'), ('blank', '')])
check(encode_pairs([], none_policy='omit') == '')
check(encode_pairs([('x', 'None')], none_policy='omit') == 'x=None')
check(encode_pairs([('x', None)], none_policy='empty') == 'x=')
for value in ([], {}, b'x', 1.5, float('nan'), object()):
    rejects(TypeError, lambda: encode_pairs([('x', value)], none_policy='omit'))
for pairs in ([('x',)], [('x', 'y', 'z')], [None], [(None, 'x')], {'x': 'y'}, 'xy'):
    rejects(TypeError, lambda: encode_pairs(pairs, none_policy='omit'))
rejects(ValueError, lambda: encode_pairs([], none_policy='guess'))
rejects(TypeError, lambda: encode_pairs([]))
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'matrix_cases': 27, 'result': 'passed'}))
```

## Publisher checks and limits

Executed on installed CPython **3.10.12**, Linux. **127 counted checks passed**, including the 27-case matrix; no other interpreter version was run. Current deprecation wording is documentary context, not a claim that 3.14 emitted a warning in this run. No Django/Requests runtime, receiving endpoint, arbitrary iterators, mapping normalization, nested structures, floats, bytes, custom subclasses, signature canonicalization, URL validation, resource-limit or concurrency support is claimed. The API accepts only a list/tuple of two-element list/tuple pairs.

Earlier repository findings cover repeated-value shape and parser blank retention. This increment adds the application-level None adapter, explicit omission/empty/error choices, normalized boolean/zero preservation and rejection tests. It does not repackage those earlier probes as a new parser defect.
