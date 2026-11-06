# Enum duplicate values are aliases, not distinct states

## Research
A public card-enum question gives TEN and QUEEN the same score, then finds QUEEN displayed as TEN and missing from iteration. Python's Enum rules deliberately make duplicate values aliases of the first name. Shared metadata is not enough to identify separate enum members.

## Discussion
With an ordinary Enum, an alias is the same member object. Lookup by the alias name or shared value returns the canonical member, and its name is canonical. Iteration returns canonical members only; `__members__` includes all declared names, including aliases. Set or dictionary keys using aliases therefore do not preserve separate states.

This is documented behavior, not a new defect. Aliases can be intentional compatibility names. If duplicates are mistakes, the unique decorator rejects them during class creation. If separate identities happen to share a score or label, give each member a distinct value and keep the shared information as separate metadata. The probe uses a simple distinct tuple value, not a general card model.

## Conclusion
Choose whether a second name means the same state or a different state with equal metadata. Inspect `__members__` when auditing names and ordinary iteration when enumerating canonical states. Retain the original spelling separately if the caller's alias spelling matters; the member object alone does not distinguish which alias name was used. Adding uniqueness checks to an existing public enum can reject intentional aliases, so do not make that change blindly.

## Action: executable probe
Original code under this repository's MIT license. Small in-memory ordinary enums only. Run without Python optimization so assertions remain enabled.

```python
from enum import Enum, unique
import json
import platform

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

class Status(Enum):
    READY = 1
    WAITING = 2
    QUEUED = 2

check(Status.QUEUED is Status.WAITING)
check(Status['QUEUED'] is Status.WAITING)
check(Status(2) is Status.WAITING)
check(Status.QUEUED.name == 'WAITING')
check([member.name for member in Status] == ['READY', 'WAITING'])
check(len(Status) == 2)
check(list(Status.__members__) == ['READY', 'WAITING', 'QUEUED'])
check(len(Status.__members__) == 3)
check([name for name, member in Status.__members__.items()
       if name != member.name] == ['QUEUED'])
check(len({Status.WAITING, Status.QUEUED}) == 1)
check(len({Status.WAITING: 'one', Status.QUEUED: 'two'}) == 1)

rejected = False
try:
    @unique
    class Accidental(Enum):
        FIRST = 1
        SECOND = 1
except ValueError:
    rejected = True
check(rejected)

# Distinct identity and shared metadata are different fields.
@unique
class Card(Enum):
    TEN = ('ten', 10)
    QUEEN = ('queen', 10)

check(Card.TEN is not Card.QUEEN)
check(len(Card) == 2)
check(Card.TEN.value[1] == Card.QUEEN.value[1] == 10)
check(Card(('queen', 10)) is Card.QUEEN)
print(json.dumps({'python': platform.python_version(), 'checks': checks}))
```

## Verification and limits
- 16 checks passed on CPython 3.13.17 and 3.14.9.
- Covers alias identity, by-name/value lookup, canonical names, iteration versus all names, set/dict collapse, unique rejection and distinct tuple-valued members sharing metadata.
- No Flag/IntFlag, custom equality/value generation, runtime alias additions, cross-process serialization, schema migration or third-party enum library was tested. Changing member values can affect consumers; the tuple example is a new demonstration, not migration advice.

## Sources
- [Python 3.14 enum](https://docs.python.org/3.14/library/enum.html): canonical iteration, all-name mapping and unique contract.
- [PEP 435](https://peps.python.org/pep-0435/): duplicate-value alias design and lookup semantics.
- [Public duplicate-card-values question](https://stackoverflow.com/questions/31537316/python-enums-with-duplicate-values): concrete distinct-identity versus shared-score problem; third-party alternatives not tested.
- [PyMOTW enum](https://pymotw.com/3/enum/): independent alias and unique examples.
- [PythonTutorial alias guide](https://www.pythontutorial.net/python-oop/python-enum-unique/): independent explanation; the correct mapping name is `__members__`, not the prose typo `__member__`.
- [Real Python enum guide](https://realpython.com/python-enum/): aliases and canonical iteration discussion. The mapping is read-only, as the primary reference states, not an ordinary mutable dictionary.
