# dataclasses.replace reconstructs an instance rather than cloning all runtime state

Date: 2026-11-05. A documented reconstruction distinction, not a new dataclasses defect.

## Research

The [dataclasses reference](https://docs.python.org/3/library/dataclasses.html) says replace creates a new instance by calling initialization, including post-init processing, and does not copy init=False fields from the original instance. [PEP 557](https://peps.python.org/pep-0557/) explains why copying those fields afterward would overwrite freshly computed derived values. A [historical design issue](https://github.com/ericvsmith/dataclasses/issues/74) records the earlier conflict. That old discussion is design context, not a current unresolved bug or the current implementation's measured output.

## Discussion

For a generated initializer, replacing a Square side recomputes its area through post-init. A runtime note stored in an init=False field is not carried over; the new instance starts with its declared default. Even replace(source) with no changed inputs initializes a new instance again.

This distinction matters when post-init does work beyond assigning derived fields. The probe records calls in a local list only, showing that initialization runs again. It does not perform network, file or database work. Treat replacement as reconstruction and review initialization effects before using it as an object-copy shortcut.

## Conclusion

Use replace when rebuilding from constructor fields is the intended contract. If runtime state must be retained, define an explicit application copy or replacement policy rather than assuming every attribute survives. Do not copy derived fields back blindly: that can contradict the changed constructor inputs. The probe does not pass init=False fields as replacement inputs.

## Action: generated-initializer reconstruction probe

Ran 10 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Tests cover a changed input, recomputed area, a fresh init=False note, unchanged source state, initialization-call recording, replacement without changes. Only a local sample dataclass is used.

```python
import json
import platform
from dataclasses import dataclass, field, replace

initializations = []

@dataclass
class Square:
    side: int
    area: int = field(init=False)
    note: str = field(init=False, default='fresh')

    def __post_init__(self):
        self.area = self.side * self.side
        initializations.append(self.side)

source = Square(2)
source.note = 'runtime note'
checks = 0
assert source.area == 4
checks += 1
changed = replace(source, side=3)
assert changed is not source
checks += 1
assert changed.side == 3
checks += 1
assert changed.area == 9
checks += 1
assert changed.note == 'fresh'
checks += 1
assert source.side == 2 and source.area == 4
checks += 1
assert source.note == 'runtime note'
checks += 1
assert initializations == [2, 3]
checks += 1
unchanged_inputs = replace(source)
assert unchanged_inputs.area == 4 and unchanged_inputs.note == 'fresh'
checks += 1
assert initializations == [2, 3, 2]
checks += 1
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- The sample uses a generated initializer. Custom initialization, InitVar requirements, inheritance, frozen classes, copy.replace dispatch and deep-copy policies and exact rejection exception types are not tested.
- The local call log illustrates repeated initialization, not evidence of real external side effects or a general copying algorithm.
- No production object was changed. No new defect, concurrency guarantee or performance benchmark is claimed.
