# Buffered log records are not snapshots of mutable arguments

Date: 2026-11-13. A logging formatting-boundary finding, not a new Python defect.

## Research

The logging HOWTO says argument formatting is deferred. The handler reference describes MemoryHandler as buffering records and forwarding them to a target on flush. A historical public question about keeping logs in a live object illustrates the distinction: its accepted answer retains unformatted records and shows argument identity, rather than stored text. That is not itself a bug report about mutation or evidence of current production impact.

A python-json-logger maintainer discussion explains lazy message interpolation through LogRecord.getMessage. The practical question here is which state a later formatter sees when a logged object changes after the call returns.

## Discussion

The probe logs successive states of a nested dictionary, then mutates it again before explicitly flushing MemoryHandler. Both passing the dictionary itself and passing a shallow dictionary copy produce its final nested-list state in every buffered line. Copying the outer dictionary does not copy its list.

Deep-copying this small built-in payload or explicitly converting it to text at the call preserves each earlier state. An immediate StreamHandler control also preserves the earlier rendered text. These are snapshot choices with different costs and types, not interchangeable advice to replace lazy logging everywhere.

The base QueueHandler is a separate boundary: its prepare method formats the message before queuing. In the tested build, retrieved message strings keep their earlier states even though arbitrary mutable extra fields still share the original payload. This is not a claim that queueing deeply freezes a record. The probe retrieves from the queue directly, without a listener thread.

One independent logging article linked below broadly places QueueHandler representation work on the listener thread. That does not describe the base QueueHandler message path measured here or its documented prepare behavior. Custom prepare implementations and formatters can change the boundary; no ORM or database behavior was tested.

The prior ancestor-handler finding covers routing and levels and explicitly excludes queue handlers. It does not test argument snapshot timing.

## Conclusion

For event-time facts, log selected immutable values or deliberately capture a bounded, safe representation before the object changes. A shallow outer copy is insufficient for nested mutable values. Deepcopy works for the sample built-ins, but is not a universal logging fix: custom copying behavior, cost and sensitive fields still need an application policy. Avoid logging whole sensitive objects just to obtain a snapshot.

Inspect the actual handler and formatter path. MemoryHandler buffers records, not completed message strings. Base QueueHandler prepares message text before enqueueing, but does not promise to snapshot arbitrary extra fields. Keep lazy formatting where its semantics fit, and capture only the facts that need event-time meaning.

## Action

Original code under this repository's MIT license. Run as a fresh standalone process without optimization so assertions remain enabled. Only StringIO, local dictionaries/lists and an in-process queue are used. The root configuration is not changed.

```python
import copy
import io
import json
import logging
import logging.handlers
import platform
import queue
import uuid

checks = 0

def check(value):
    global checks
    assert value
    checks += 1

# Standalone named logger: leave the root configuration untouched.
log = logging.getLogger('snapshot_probe_' + uuid.uuid4().hex)
log.setLevel(logging.INFO)
log.propagate = False
formatter = logging.Formatter('%(message)s')
cases = 0
for count in (1, 2, 4):
    for mode in ('reference', 'shallow', 'deep', 'text'):
        output = io.StringIO()
        target = logging.StreamHandler(output)
        target.setFormatter(formatter)
        buffer = logging.handlers.MemoryHandler(
            count + 1, flushLevel=logging.CRITICAL, target=target,
            flushOnClose=False)
        log.addHandler(buffer)
        source = {'items': []}
        expected = []
        try:
            for i in range(count):
                source['items'].append(i)
                if mode == 'reference':
                    argument = source
                elif mode == 'shallow':
                    argument = source.copy()
                elif mode == 'deep':
                    argument = copy.deepcopy(source)
                else:
                    argument = str(source)
                log.info('%s', argument)
                expected.append(str(source))
            check(output.getvalue() == '')
            check(len(buffer.buffer) == count)
            # Mutate only after every logging call returned.
            source['items'].append(99)
            if mode in ('reference', 'shallow'):
                expected = [str(source)] * count
            buffer.flush()
            check(output.getvalue().splitlines() == expected)
            check(len(buffer.buffer) == 0)
            buffer.flush()
            check(output.getvalue().splitlines() == expected)
            cases += 1
        finally:
            log.removeHandler(buffer)
            buffer.close()
            target.close()
            output.close()

# QueueHandler.prepare formats on the producer path in this base class.
# No listener thread or scheduling race is needed to test that boundary.
for count in (1, 2, 4):
    q = queue.Queue()
    handler = logging.handlers.QueueHandler(q)
    handler.setFormatter(formatter)
    log.addHandler(handler)
    source = {'items': []}
    expected = []
    try:
        for i in range(count):
            source['items'].append(i)
            log.info('%s', source, extra={'payload': source})
            expected.append(str(source))
        check(q.qsize() == count)
        source['items'].append(99)
        records = [q.get_nowait() for _ in range(count)]
        check([r.getMessage() for r in records] == expected)
        check(all(r.args is None for r in records))
        # Message text is stable, but arbitrary extra fields are not deep-copied.
        check(all(r.payload is source for r in records))
        check(all(r.payload['items'] == list(range(count)) + [99]
                  for r in records))
        check(q.empty())
        cases += 1
    finally:
        log.removeHandler(handler)
        handler.close()

# Immediate formatting captures each state without buffering.
output = io.StringIO()
handler = logging.StreamHandler(output)
handler.setFormatter(formatter)
log.addHandler(handler)
source = {'items': []}
try:
    log.info('%s', source)
    source['items'].append(99)
    check(output.getvalue() == "{'items': []}\n")
    check(log.handlers == [handler])
finally:
    log.removeHandler(handler)
    handler.close()
    output.close()
check(log.handlers == [])
print(json.dumps({'python': platform.python_version(),
                  'implementation': platform.python_implementation(),
                  'system': platform.system(), 'checks': checks,
                  'buffer_and_queue_cases': cases}))
```

### Verification and limits

Executed on CPython **3.10.12**, Linux: **81 checks passed** across **12 MemoryHandler cases** (four argument policies by one, two or four records), **3 QueueHandler cases**, and an immediate-output control. Checks cover delayed output, record count, complete rendered lines, cleared buffers, repeated flush without duplicate output, stable queued message text, cleared args, shared extra identity and handler cleanup.

Capacity and flush level are chosen to avoid automatic flush before the mutation. Cleanup removes and closes each handler; the uniquely named logger remains registered until process exit. No root configuration, network, real file output, multiprocessing, QueueListener thread, concurrent mutation, custom objects/copy hooks, custom prepare/format overrides, exception formatting, shutdown timing, performance or other interpreter build was tested. These checks do not validate a production logging configuration or prove audit-log safety.

## Publisher

One bounded finding and runnable diagnostic, not a runtime patch, third-party change or claim of widespread incidents. The executable probe was run locally; repository CI is a separate check of its configured suite, not proof that this embedded example ran there.

## Sources

1. [Python logging HOWTO](https://docs.python.org/3.10/howto/logging.html): deferred formatting and argument evaluation distinction.
2. [Python logging handlers](https://docs.python.org/3.10/library/logging.handlers.html): MemoryHandler buffers records and QueueHandler.prepare formats before queuing. The fetched page includes newer-version additions; only these longstanding contracts are used, with measured behavior limited to the named build.
3. [Python logging reference](https://docs.python.org/3.10/library/logging.html): message/args formatting and extra fields on LogRecord.
4. [Python copy reference](https://docs.python.org/3.10/library/copy.html): shallow versus deep copy and custom-copy limitations.
5. [Logging to a live object](https://stackoverflow.com/questions/24307454/python-logging-standard-approach-to-log-to-a-live-object), June 2014: historical community example of retained, unformatted argument references. No answer code was copied.
6. [python-json-logger issue 21](https://github.com/nhairs/python-json-logger/issues/21), August 2024: maintainer explanation of lazy message interpolation. This probe does not install or test that package.
7. [Lazy Formatting and Expensive Log Arguments](https://python-observability.com/python-logging-fundamentals-and-structured-data/logging-performance-and-overhead/lazy-formatting-and-expensive-log-arguments/): independent guidance read as a secondary source, with its broad QueueHandler listener-thread statement not adopted for the base handler message path.
