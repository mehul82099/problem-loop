# azure-servicebus AutoLockRenewer: one renew call slower than 5 s silently stops renewal for that message (max_workers > 1)

**Source:** [Azure/azure-sdk-for-python#49809](https://github.com/Azure/azure-sdk-for-python/issues/49809) - opened 2026-11-03 by black-snow (GitHub association: NONE, i.e. no affiliation badge on the issue).

## What the report says

When `AutoLockRenewer` (azure-servicebus 7.15.0) runs with `max_workers > 1`, a single `renew_message_lock` call that takes 5 seconds or longer permanently stops renewal for that message. `on_lock_renew_failure` is not called and nothing is logged; the lock expires while the application still holds the message, so the broker redelivers it to another consumer while the first is still processing - the classic duplicate-processing failure mode lock renewal exists to prevent.

The reporter argues 5 s renewals are easy to hit in production: the default retry policy (3 retries, 0.8 s exponential backoff) already exceeds 5 s after two retries plus request time, and a reconnect or slow management-link response does the same. The bug mostly bites consumers holding few messages for a long time - one renewer per message, or a renewer whose other messages were settled - because the queue is empty whenever a renew is in flight.

Their runnable repro (public `register()` API, a fake receiver whose `renew_message_lock` sleeps 6 s): renewal happens exactly once, then never again, and the lock expires. With a 1 s renew, renewal continues normally.

## Root cause (reported, verified against current source)

The reporter's five-step walk through `azure/servicebus/_common/auto_lock_renewer.py` checks out on `main` as of 2026-11-03:

1. `_dispatch_worker` (~line 136) takes the renew task off `_renew_tasks` and, when `max_workers > 1`, submits it to the executor (`self._executor.submit(self._auto_lock_renew_task, ...)`), then updates `_last_activity_timestamp`.
2. While the renew runs in the executor, the task is not in `_renew_tasks`; if it was the only registered renewable, the queue is empty.
3. Once idle for `_dispatcher_timeout` (`= 5`, line 84), the dispatcher clears `_running_dispatcher` and returns (lines 150-153, with the comment that the thread exits so as not to block the main thread).
4. The in-flight task then completes the renew and re-enqueues itself (`self._renew_tasks.put(...)`, ~line 189) - but no dispatcher is running to pick it up. Only a later `register()` restarts the dispatcher via `_init_workers` (line 103 checks `_running_dispatcher.is_set()`).
5. The task didn't fail, so `on_lock_renew_failure` is never invoked.

Their suggested direction: the dispatcher's idle check should account for tasks in flight in the executor (e.g. an outstanding-task counter), not just queue emptiness.

## Two related behaviors the reporter flags (possibly separate issues)

- **Busy-spin with `max_workers=1`**: `_dispatch_worker` then runs `_auto_lock_renew_task` inline (line 143); the task re-enqueues itself before the loop re-checks, so the inner `while not self._renew_tasks.empty()` never exits and never reaches `time.sleep(self._sleep_time)` - the reporter measured ~2.5 s CPU per 3 s wall for one registered message. The code path is consistent with this.
- **Transient recovery reads as clean shutdown**: `_renewable` (line 124) returns `False` when `renewable._receiver._running` is `False`, and per the reporter the receiver clears that flag during transient connection recovery as well as on intentional close - so a concurrent connection error on the same receiver stops renewal for all its messages without `on_lock_renew_failure`. The `_receiver._running` check is verified at line 131; the recovery-clears-flag claim I did not trace further.

## Limits

- The repro was not executed here; the 6 s vs 1 s outputs are quoted from the issue. The mechanism is confirmed by the source reading above, including all cited lines.
- The reporter's association is NONE. As of writing, the only responses are Azure's `github-actions[bot]` routing ping and its automated "Agentic Issue Triage" summary - tooling output, not a human maintainer assessment. No maintainer position or linked fix yet.
- Affected scope per the report is the synchronous `AutoLockRenewer`; whether the async variant shares the dispatcher logic was not assessed.

## Sources

- Issue: <https://github.com/Azure/azure-sdk-for-python/issues/49809>
- auto_lock_renewer.py (main): <https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/servicebus/azure-servicebus/azure/servicebus/_common/auto_lock_renewer.py>
- azure-servicebus on PyPI: <https://pypi.org/project/azure-servicebus/7.15.0/>
