# A new dictionary from union is not a deep merged copy

## Research
The dict union operator creates a new dictionary and gives the right operand's value priority for each shared key. It does not recursively merge nested dictionaries. Public merge examples often use configuration data, where replacing an entire nested block can differ from an intended field-level override.

## Discussion
In the probe, overriding one nested port value replaces the whole service dictionary in the result, so the base host field is not present there. The base dictionary is not changed by forming the union. However, the result reuses selected nested objects: mutating the result's service block changes the override's block, and appending to a surviving list changes the base's list. A new top-level dictionary is not deep isolation.

Overwriting a key does not move it to the right operand's insertion position; new keys are appended. Precedence is right-wins and is not commutative. The augmented form updates the existing dictionary, so aliases see the changes. Its accepted operands are broader: ordinary dict augmented union accepts iterable key-value pairs, while ordinary dict binary union does not accept a list of pairs directly.

## Conclusion
Use union for top-level right-wins selection when shallow references are intended. For nested configuration, specify whether each block is replaced or combined, how lists behave, what deletion means and how type conflicts are handled. Deep copying and recursive merging answer different questions; neither policy is inferred by the operator. No generic deep-merge helper is published here because those choices belong to the application's contract. This is documented behavior, not a new defect.

## Action: executable probe
Original code under this repository's MIT license. In-memory ordinary dictionaries and lists only. Run without Python optimization so assertions remain enabled.

```python
import json
import platform

checks = 0

def check(condition):
    global checks
    assert condition
    checks += 1

base = {'service': {'host': 'local', 'port': 8000},
        'tags': ['base'], 'enabled': True}
override = {'service': {'port': 9000}, 'extra': 1}
result = base | override
check(result is not base and result is not override)
check(result['service'] == {'port': 9000})
check('host' not in result['service'])
check(base['service'] == {'host': 'local', 'port': 8000})
check(list(result) == ['service', 'tags', 'enabled', 'extra'])
check(result['service'] is override['service'])
check(result['tags'] is base['tags'])
result['service']['port'] = 9100
check(override['service']['port'] == 9100)
result['tags'].append('shared')
check(base['tags'] == ['base', 'shared'])
result['enabled'] = False
check(base['enabled'] is True)
check((base | override)['service'] != (override | base)['service'])
check(({} | base)['tags'] is base['tags'])

# Augmented union updates the existing destination and its aliases.
left = {'a': 1}
alias = left
left |= {'a': 2, 'b': 3}
check(alias is left)
check(alias == {'a': 2, 'b': 3})
left |= [('c', 4)]  # Iterable pairs accepted for augmented update.
check(left == {'a': 2, 'b': 3, 'c': 4})
try:
    {} | [('c', 4)]
except TypeError:
    pairs_rejected = True
else:
    pairs_rejected = False
check(pairs_rejected)
check(base | {} == base)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 17 checks passed on CPython 3.13.17 and 3.14.9.
- Covers fresh top-level result, wholesale nested replacement, unchanged base at construction, insertion order, shared nested dictionary/list references, independent top-level reassignment, operand precedence, augmented aliases and pair-iterable operand differences.
- Tested plain dict operands only. No subclasses/operator overrides, custom mappings, malformed iterable update failures, recursive merge, deepcopy, cycles, concurrency, performance or production configuration was tested. No schema validation, deletion semantics or mutation rollback guarantee is supplied.

## Sources
- [Python 3.14 built-in types](https://docs.python.org/3.14/library/stdtypes.html): dict union/augmented union operands, precedence and insertion order. Full original HTML inspected for the dictionary section after readable-fetch limits.
- [PEP 584](https://peps.python.org/pep-0584/): accepted union design, right-wins conflicts and augmented update semantics; performance debate not treated as measured results here.
- [Real Python dictionaries](https://realpython.com/python-dicts/): union and augmented union examples.
- [Single-expression merge question](https://stackoverflow.com/questions/38987/how-do-i-merge-two-dictionaries-in-a-single-expression-in-python): public shallow-merge guidance; old version alternatives not tested.
- [Nested merge question](https://stackoverflow.com/questions/7204805/deep-merge-dictionaries-of-dictionaries-in-python): differing nested/conflict policies; proposed helpers not adopted.
- [GoLinuxCloud merge guide](https://www.golinuxcloud.com/merge-two-python-dict-into-single-expression/): independent shallow-versus-deep explanation; no benchmark claim adopted.
