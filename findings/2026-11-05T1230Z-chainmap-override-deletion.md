# ChainMap deletion removes an override, not the visible key everywhere

Date: 2026-11-05. A documented layered-mapping distinction, not a new collections defect.

## Research

The [collections reference](https://docs.python.org/3/library/collections.html) says ChainMap lookup searches mappings in order, while writes, updates and deletions operate only on the first mapping. It holds those mappings by reference. [Real Python's explanation](https://realpython.com/python-chainmap/) demonstrates the resulting deletion KeyError for a deeper-only key. A [configuration-layering article](https://nalar.dev/layer-configuration-safely-with-python-chainmap/) discusses the same override-removal surprise. These are explanations of intended behavior, not evidence of a current runtime bug.

## Discussion

With ChainMap(overrides, defaults), assigning a value through the chain creates or updates an override even if lookup previously read the value from defaults. Deleting that override makes the default visible again. The key can therefore remain present after a successful deletion.

Membership and deletion also have different scopes: a key can be in the chain but absent from its first mapping, so deletion raises KeyError. Clearing the chain clears only that first mapping, not every source. External changes to a lower mapping remain visible when not shadowed.

## Conclusion

Treat the first mapping as an explicit write layer. Removing an override and hiding a setting from the combined view are different operations. If the application needs a disabled or excluded setting, define that policy separately rather than assuming deletion removes all fallback values. Use dict(chain) for a shallow snapshot of current top-level bindings when a live view is not wanted; nested mutable values still need their own copy policy.

## Action: layered-configuration probe

Ran 14 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. The probe covers override assignment, fallback after deletion, membership versus deletion, clear, external default updates and a shallow snapshot of scalar values. It changes only local sample dictionaries.

```python
import json
import platform
from collections import ChainMap

checks = 0

def equal(actual, expected):
    global checks
    assert actual == expected, (actual, expected)
    checks += 1

overrides = {}
defaults = {'port': 8000, 'host': 'localhost'}
config = ChainMap(overrides, defaults)
equal(config['port'], 8000)
config['port'] = 9000
equal(overrides, {'port': 9000})
equal(defaults['port'], 8000)
equal(config['port'], 9000)
del config['port']
equal(overrides, {})
equal(config['port'], 8000)  # Deleting override reveals fallback.
equal('host' in config, True)
try:
    del config['host']  # Lookup succeeds, deletion in first map does not.
except KeyError:
    checks += 1
else:
    raise AssertionError('expected first-map deletion failure')
equal(defaults['host'], 'localhost')
defaults['port'] = 7000
equal(config['port'], 7000)  # Chain is a live view.
config['port'] = 6000
config['extra'] = True
config.clear()
equal(overrides, {})
equal(dict(config), {'port': 7000, 'host': 'localhost'})
# A shallow snapshot freezes top-level bindings, not nested mutable objects.
snapshot = dict(config)
defaults['port'] = 5000
equal(snapshot['port'], 7000)
equal(config['port'], 5000)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original probe and finding use the repository's MIT license. Linked sources retain their authorship.
- Only ordinary dict-backed ChainMap with scalar values was tested. Custom mappings, concurrent mutation, deep merge and nested mutable values are outside the probe.
- The first write layer is not an isolation or security boundary: mappings remain accessible and referenced. No access-control claim is made.
- No production settings were changed. No new defect, prevalence estimate or performance benchmark is claimed.
