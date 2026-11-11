# A shelve value is not a live database row

Date: 2026-11-12. Documented persistence semantics, not a new database defect.

## Research

A [public developer question](https://stackoverflow.com/questions/41661085/shelve-writes-blank-lists-dictionarys) reports appended lists and nested dictionary changes not being saved. The [Python 3.10 shelve reference](https://docs.python.org/3.10/library/shelve.html) explains why: without writeback, mutation of a retrieved object is not an assignment to the shelf. Its example retrieves, changes and assigns the value back.

With writeback=True, accessed entries are cached and written at sync/close. That cache is not a changed-row tracker: the docs warn about memory use and slow closing because all accessed entries are written back. The independent [PyMOTW write-back explanation](https://pymotw.com/2/shelve/) describes the same tradeoff. Its Python 2 example syntax is historical; the diagnostic below is Python 3.

[Closed CPython issue 50004](https://github.com/python/cpython/issues/50004) clarifies that writeback is additional to normal assignment writes, not a promise that assignments only remain in memory until close. The [exact v3.10.12 implementation](https://github.com/python/cpython/blob/v3.10.12/Lib/shelve.py) serializes on __setitem__, caches retrieved values when enabled, and empties the cache after sync writes it. This explains a second boundary: a reference held across sync can be detached from the shelf's new cache.

The [pickle security warning](https://docs.python.org/3.10/library/pickle.html) matters here. Loading an untrusted shelf can execute code. This probe opens only shelves it creates itself, containing plain built-in values.

## Discussion

The diagnostic starts with [0], or a dictionary containing that list, and retrieves a value into a local reference. It appends 1, optionally syncs, then appends 2. It either keeps the old reference or reloads after sync. Finally it optionally assigns the value back, closes, and reopens read-only to inspect persistence.

| writeback | lifecycle | no final assignment | final assignment |
| --- | --- | --- | --- |
| False | no sync | [0] | [0, 1, 2] |
| True | no sync | [0, 1, 2] | [0, 1, 2] |
| False | sync, keep reference | [0] | [0, 1, 2] |
| True | sync, keep reference | [0, 1] | [0, 1, 2] |
| False | sync, reload | [0] | [0, 2] |
| True | sync, reload | [0, 1, 2] | [0, 1, 2] |

The table shows the stored list, directly or inside the nested dictionary. Reloading after sync with writeback=False discards the unsaved first append; assigning that reloaded object later cannot recover it. With writeback=True, sync saves the first append but empties the cache. Mutating the old local reference afterward does not automatically put it back in the cache. No concurrent reader/writer is used to infer these results.

## Conclusion

Use retrieve/change/assign when explicit persistence is intended. If using writeback, understand its cache lifetime and capacity cost. After sync, deliberately reload or reassign before expecting later local mutations to persist. Do not infer that sync is a transaction, a crash-safety guarantee, or a lock. The docs do not support concurrent read/write access to a shelf; this report proposes no concurrency workaround.

## Action

**96 checks passed across 24 fixtures** on installed CPython **3.10.12**, Linux, backend reported by dbm.whichdb as **dbm.ndbm**. The matrix crosses writeback off/on, list/nested-dictionary values, no-sync/keep-after-sync/reload-after-sync, and final assignment off/on. Checks cover repeated retrieval identity, reopened persisted content, key set and unchanged initialization input. Every fixture has a unique temporary directory, and all backend files are cleaned by that directory's context manager. No user-supplied path, shelf or serialized content is read.

Run `python3 shelve_mutation_matrix.py`:

```python
# Original MIT diagnostic. Only self-created shelves are opened.
import copy
import dbm
import json
import platform
import shelve
import tempfile
from pathlib import Path

checks = 0
results = []
backends = set()


def check(value):
    global checks
    if not value:
        raise AssertionError('check failed')
    checks += 1


def initial(shape):
    return [0] if shape == 'list' else {'events': [0]}


def add(value, shape, number):
    (value if shape == 'list' else value['events']).append(number)


for writeback in (False, True):
    for shape in ('list', 'nested-dict'):
        for mode in ('no-sync', 'sync-held', 'sync-reload'):
            for assign in (False, True):
                with tempfile.TemporaryDirectory(prefix='owned-shelf-') as root:
                    filename = str(Path(root) / 'sample')
                    source = initial(shape)
                    before = copy.deepcopy(source)
                    with shelve.open(filename, writeback=writeback) as shelf:
                        shelf['sample'] = source
                    backends.add(dbm.whichdb(filename))
                    with shelve.open(filename, writeback=writeback) as shelf:
                        held = shelf['sample']
                        check((held is shelf['sample']) == writeback)
                        add(held, shape, 1)
                        if mode != 'no-sync':
                            shelf.sync()
                            if mode == 'sync-reload':
                                held = shelf['sample']
                        add(held, shape, 2)
                        if assign:
                            shelf['sample'] = held
                    expected = initial(shape)
                    if mode == 'no-sync':
                        if writeback or assign:
                            add(expected, shape, 1)
                            add(expected, shape, 2)
                    elif mode == 'sync-held':
                        if assign:
                            add(expected, shape, 1)
                            add(expected, shape, 2)
                        elif writeback:
                            add(expected, shape, 1)
                    else:
                        if writeback:
                            add(expected, shape, 1)
                            add(expected, shape, 2)
                        elif assign:
                            add(expected, shape, 2)
                    # Never overlap readers with an open writer.
                    with shelve.open(filename, flag='r') as shelf:
                        observed = shelf['sample']
                        check(observed == expected)
                        check(set(shelf.keys()) == {'sample'})
                    check(source == before)
                    results.append({'writeback': writeback, 'shape': shape,
                                    'mode': mode, 'assign': assign,
                                    'persisted': observed})
print(json.dumps({'python': platform.python_version(), 'platform': platform.system(),
                  'backends': sorted(backends), 'checks': checks,
                  'cases': len(results), 'results': results}, indent=2))
```

## Publisher and limits

Original diagnostic is MIT licensed. Only the named installed build/backend and ordinary context-managed closes were executed. Documentation pages currently identify a newer 3.10 patch release; implementation source is pinned to the tested version. No other dbm backend, Python version, Windows/macOS, concurrency, process crash, disk-full/error recovery, durability, memory benchmark, arbitrary object graph, external alias persistence, database migration or transactional helper is claimed. In-memory identity checks are implementation observations on this build, not a cross-backend performance promise. The result does not recommend shelve for untrusted input or production multi-writer storage.
