# basicConfig does not update a root logger that already has handlers

Date: 2026-11-06. A documented logging-configuration distinction, not a new logging defect.

## Research

The [Python 3.14 logging reference](https://docs.python.org/3.14/library/logging.html) says basicConfig does nothing when root handlers already exist unless force=True. It also says force removes and closes existing root handlers. Developer questions about [a level not changing](https://stackoverflow.com/questions/32681289/python-logging-wont-set-a-logging-level-using-basicconfig) and [configuration affected by imports](https://stackoverflow.com/questions/73882299/python-logging-messages-not-showing-up-due-to-imports) show the resulting confusion. These reports establish a public problem pattern, not prevalence or a current runtime regression.

## Discussion

Calling basicConfig(level=INFO) after a prior configuration does not simply update the level. In the controlled probe, both the old root level and old handler remain, and the requested new output stream receives nothing. Setting the root level explicitly changes that level without replacing the existing handler or formatter.

force=True is a different operation: it replaces root handlers and closes those removed handlers. That can disrupt output destinations or integrations owned by an application, framework or test runner. It should not be applied blindly in a library merely to make a log message appear. Handler levels, filters, named logger levels and propagation can independently affect real applications; this probe does not diagnose those cases.

## Conclusion

Have the application configure logging early and decide who owns root handlers. If only a level change is intended, change the relevant logger level explicitly and review handler thresholds too. Use forced root reconfiguration only when replacing that configuration is actually intended. Inspect the active logging setup rather than assuming another basicConfig call will overwrite it.

## Action: standalone in-memory configuration probe

Ran 10 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64, as fresh standalone processes. Two StringIO streams and a tracking handler show ignored reconfiguration, explicit level change with retained format, and forced handler replacement/close. The script refuses to run when root handlers already exist and cleans up its own handlers. Do not paste it into a live application or notebook logging session.

```python
# Run as a standalone script: this intentionally configures its root logger.
import io
import json
import logging
import platform

closed = []
class TrackedHandler(logging.StreamHandler):
    def close(self):
        closed.append(self)
        super().close()

root = logging.getLogger()
if root.handlers:
    raise SystemExit('Run in a fresh interpreter with no root handlers.')
old_level = root.level
first = io.StringIO()
second = io.StringIO()
handler = TrackedHandler(first)
checks = 0
try:
    logging.basicConfig(handlers=[handler], level=logging.WARNING,
                        format='first:%(message)s')
    assert root.handlers == [handler]
    checks += 1
    logging.basicConfig(stream=second, level=logging.INFO,
                        format='second:%(message)s')
    assert root.level == logging.WARNING
    checks += 1
    assert root.handlers == [handler]
    checks += 1
    logging.info('hidden')
    assert first.getvalue() == second.getvalue() == ''
    checks += 1
    root.setLevel(logging.INFO)
    logging.info('retained')
    assert first.getvalue() == 'first:retained\n'
    checks += 1
    assert root.handlers == [handler]
    checks += 1
    logging.basicConfig(stream=second, level=logging.INFO,
                        format='second:%(message)s', force=True)
    assert handler not in root.handlers
    checks += 1
    assert handler in closed
    checks += 1
    logging.info('replaced')
    assert second.getvalue() == 'second:replaced\n'
    checks += 1
    assert first.getvalue() == 'first:retained\n'
    checks += 1
finally:
    for current in root.handlers[:]:
        root.removeHandler(current)
        current.close()
    root.setLevel(old_level)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- No real log file, production logger, external service, framework or test-runner configuration was changed.
- No automatic module-level first-call setup, named-logger propagation, handler-level filtering, threads or concurrent reconfiguration is tested.
- Closing a handler is verified by its close method being called, not by assuming that every underlying stream is closed. No new defect or performance claim is made.
