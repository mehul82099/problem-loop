# JSON duplicate names need a pairs hook, not a check after decoding to a dictionary

Date: 2026-11-04. A tested duplicate-name policy example, not a new decoder defect.

## Research

The [Python json reference](https://docs.python.org/3/library/json.html) documents that repeated object names are accepted by default and only the last name/value pair survives. It exposes `object_pairs_hook` to change this behavior before dictionary construction. [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) says object names SHOULD be unique and notes that implementations differ when they are not. Duplicate handling therefore needs an explicit application policy, not an assumption of universal rejection.

[Python issue 45054](https://bugs.python.org/issue45054) reports another route to the same ambiguity: a Python mapping with both the integer key 1 and string key "1" can encode to repeated JSON names because JSON object names are strings. The [developer question](https://stackoverflow.com/questions/16172011/json-in-python-receive-check-duplicate-key-error) asks how to reject duplicates rather than silently retain one. This finding tests that narrow policy, not the status of a proposed upstream warning.

## Discussion

An ordinary `object_hook` sees an already-built dictionary, so the earlier repeated values are no longer available there. An `object_pairs_hook` receives the decoded pairs before that collapse. It runs for nested objects too. Duplicate scope is per object: two sibling objects may each contain an x key without conflicting.

The comparison is over decoded name strings. The spellings `"a"` and `"\u0061"` decode to the same name and must be treated as a duplicate under this policy. The helper deliberately reports only a generic error, not the supplied key or document contents. It does not return a source location or full JSON path.

## Conclusion

If unique names are required, reject repeats while pairs are still available. Do not attempt to recover them from `dict.keys()` after ordinary decoding. Checking encoder inputs is a separate task: accepting non-string mapping keys can create collisions during encoding, so a decoder-only hook does not prevent an ambiguous file from being produced in the first place.

This helper enforces unique names only. It does not require an object at the top level, reject every non-standard numeric constant, enforce a schema, normalize Unicode, or impose size/depth limits. Calling it a complete strict JSON validator would overstate what was built.

## Action: tested helper

Ran 12 cases on each of CPython **3.13.17** and **3.14.9**, Linux x86_64, for 24 passing case executions. Tests cover default last-value behavior, distinct names, repeated names in separate objects, nested duplicate rejection, escaped-equivalent names, a first value of null, top-level arrays, and an encoder key collision. Only fresh in-memory strings and objects are used.

```python
import json
import platform

def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON object name')
        result[key] = value
    return result

def loads_unique(text):
    return json.loads(text, object_pairs_hook=unique_object)

assert json.loads('{"x":1,"x":2}') == {'x': 2}
assert loads_unique('{"x":1,"y":2}') == {'x': 1, 'y': 2}
assert loads_unique('[{"x":1},{"x":2}]') == [{'x': 1}, {'x': 2}]
assert loads_unique('{"left":{"x":1},"right":{"x":2}}') == {'left': {'x': 1}, 'right': {'x': 2}}
assert loads_unique('{"x":null}') == {'x': None}
assert loads_unique('{}') == {}
assert loads_unique('[1,2]') == [1, 2]
for text in ('{"x":1,"x":2}', '{"outer":{"x":1,"x":2}}',
             r'{"a":1,"\u0061":2}', '{"x":null,"x":2}'):
    try:
        loads_unique(text)
    except ValueError as error:
        assert str(error) == 'duplicate JSON object name'
    else:
        raise AssertionError('duplicate accepted')
encoded = json.dumps({'1': 'text', 1: 'number'})
assert json.loads(encoded) == {'1': 'number'}
print(json.dumps({'python': platform.python_version(), 'cases': 12, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and helper are under the repository's MIT license; linked discussions retain their authorship.
- No files, network, external service, custom decoder, streaming input, schema or resource-limit behavior was tested.
- This is longstanding documented behavior, not a newly discovered vulnerability or a claim of production data loss. A generic ValueError identifies this policy rejection but does not replace application-specific error handling.
