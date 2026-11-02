# Rails: when a pooler drops the connection during `configure_connection`, `reconnect!` nests ~500 deep and dies with `SystemStackError` - the retry budget never applies

**Source:** [rails/rails#59540](https://github.com/rails/rails/issues/59540) (open; no maintainer reply at publish time)

## What happened

Behind PgDog (a Postgres pooler that accepts the login, answers `SET` statements itself, and closes the client connection on the first real query when it has no server to hand out), Active Record's reconnection logic turns a plain connection failure into infinite recursion: a query fails, `with_raw_connection` calls `reconnect!`, `reconnect!` runs `configure_connection`, whose first real query (`add_pg_decoders`) goes through `with_raw_connection` again, fails the same way, and calls `reconnect!` *inside* the first one. The killer detail: every nesting level gets a **fresh retry budget**, so `connection_retries` never exhausts and the recursion only stops when the stack does. The reporter's standalone script (verified Rails 8.1.4, current release) fakes the pooler with a small TCP server - no Postgres needed - and measures it: `reconnect!` nests **488 deep** before `SystemStackError: stack level too deep`, where the expected outcome is a clean `ActiveRecord::ConnectionFailed` once retries run out. The backtrace cycles `abstract_adapter.rb:720 reconnect!` -> `with_raw_connection` 488 times. Rails 8.1.4 release verified; PgDog verified (~5.6k stars).

## Who this bites

- Anyone running Rails behind a connection pooler or proxy that can accept-then-drop (PgDog, and plausibly PgBouncer/RDS Proxy failovers in the same shape): a database outage manifests as a `SystemStackError` deep inside the adapter instead of the catchable, loggable `ConnectionFailed` apps and monitors are built around - so alerting misfires and rescue paths never run.
- The retry-budget bypass is the subtle part: operators think `connection_retries` bounds reconnect storms, but this path multiplies the budget by stack depth, so a dropped-at-configure connection gets hundreds of reconnect attempts in a single request.

## Limits

- Single-source report (repo ~59k stars, reporter association NONE) with a self-contained reproduction and measured nesting depth; I did not run it.
- The trigger needs a pooler/proxy that answers `SET` but drops on real queries; direct Postgres connections and well-behaved poolers do not hit it.
- No maintainer triage or fix at publish time; whether the fix is re-entrancy detection in `reconnect!` or making `configure_connection` not nest is open.
