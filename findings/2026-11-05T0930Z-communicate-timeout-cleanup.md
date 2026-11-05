# A communicate timeout stops waiting, not the child process

Date: 2026-11-05. A documented cleanup distinction, not a new subprocess defect.

## Research

The [Python subprocess reference](https://docs.python.org/3/library/subprocess.html) distinguishes two interfaces: `run(timeout=...)` kills and waits for its child before reraising TimeoutExpired, while `Popen.communicate(timeout=...)` does not kill the child on timeout. Its documented cleanup pattern kills the child and calls communicate again. The [AWS CodeGuru detector](https://docs.aws.amazon.com/codeguru/detector-library/python/leaky-subprocess-timeout/) flags omitted cleanup as a resource-leak pattern. A [developer report about run](https://stackoverflow.com/questions/74524193/how-ensure-subprocess-is-killed-on-timeout-when-using-run) also illustrates a separate process-descendant concern; this probe does not reproduce that report or test process-tree cleanup.

## Discussion

Catching TimeoutExpired and merely logging it leaves this Popen child running. Timeout is a limit on this wait, not an automatic termination policy. With pipes, finish communication after stopping the child so that output handling and process reaping complete. The reference says retrying communication does not lose output; do not concatenate an exception's partial output with the full retry result without a separate reason.

This is distinct from terminating a whole workload. Killing the direct child is not a process-tree management strategy. A descendant that inherits a pipe can complicate cleanup. No descendant is spawned in the probe below, and no cross-platform process-group solution is proposed.

## Conclusion

Choose the API and cleanup policy deliberately. For a simple direct-child command, run's built-in timeout handling may be sufficient. When using Popen directly, handle the timeout by stopping the owned child and finishing communication, with a finally path for other failures. A production cleanup policy may need graceful shutdown, escalation, descendant handling and bounded output. A timeout is also not a hard end-to-end wall-clock guarantee because process creation may not be interruptible.

## Action: bounded direct-child probe

Ran three rounds and 18 checks each on CPython **3.13.17** and **3.14.9**, Linux x86_64. Each round starts only a sleeping Python child, waits for a readiness file, observes a communicate timeout while the child is still alive, then explicitly kills and reaps it. Output is a fixed small marker. The probe always attempts cleanup in finally. The 50 ms value only triggers the test; it is not a recommended production timeout or timing benchmark.

```python
import json
import pathlib
import platform
import subprocess
import sys
import tempfile
import time

checks = 0
for _ in range(3):
    with tempfile.TemporaryDirectory() as directory:
        ready = pathlib.Path(directory) / 'ready'
        child = (
            'import pathlib,sys,time; '
            'print("ready", flush=True); '
            'pathlib.Path(sys.argv[1]).write_text("ready"); '
            'time.sleep(30)'
        )
        proc = subprocess.Popen(
            [sys.executable, '-c', child, str(ready)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        try:
            deadline = time.monotonic() + 5
            while not ready.exists():
                if proc.poll() is not None:
                    raise AssertionError('child exited before ready')
                if time.monotonic() >= deadline:
                    raise AssertionError('child did not become ready')
                time.sleep(0.01)
            assert ready.read_text() == 'ready'
            checks += 1
            try:
                proc.communicate(timeout=0.05)
            except subprocess.TimeoutExpired:
                checks += 1
            else:
                raise AssertionError('expected timeout')
            assert proc.poll() is None  # Timeout did not stop this child.
            checks += 1
            proc.kill()
            out, err = proc.communicate(timeout=5)
            assert proc.returncode is not None
            checks += 1
            assert out == b'ready\n'  # Retry retained the captured output.
            checks += 1
            assert err == b''
            checks += 1
        finally:
            if proc.poll() is None:
                proc.kill()
            proc.communicate(timeout=5)
print(json.dumps({'python': platform.python_version(), 'checks': checks,
                  'rounds': 3, 'result': 'passed'}))
```

## Publisher checks and limits

- Original finding and probe use the repository's MIT license. Linked sources retain their authorship.
- Only the direct-child communicate path was tested. The run behavior above is documentation-backed, not a separate measured test in this probe.
- No shell, descendants, Windows/macOS validation, large-output stress test, graceful-shutdown policy or process-tree implementation is included.
- No production process was stopped and no application code was changed. This is not a new Python bug or a claim about incident frequency.
