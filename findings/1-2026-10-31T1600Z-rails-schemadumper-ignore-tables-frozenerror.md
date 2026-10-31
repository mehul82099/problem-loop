# Rails main froze `schema_ignored_tables` for Ractors - and turned a deprecated API's deprecation warning into a boot-killing FrozenError

**Source:** [rails/rails#59480](https://github.com/rails/rails/issues/59480) (open, unlabeled; filed by a Rails contributor; every anchor verified on `main`)

## What happened

Since [rails/rails#57852](https://github.com/rails/rails/pull/57852) ("Freeze configuration", merged) Rails makes config arrays Ractor-shareable in an `after_initialize` hook - verified on `main`: the `active_record.share_configs` initializer calls `ActiveSupport::Ractors.make_shareable` on both `ActiveRecord.query_transformers` and `ActiveRecord.schema_ignored_tables` ([railtie.rb#L469-L478](https://github.com/rails/rails/blob/main/activerecord/lib/active_record/railtie.rb#L469-L478)).

That silently changed what a still-supported deprecated API does. Gems appending to `ActiveRecord::SchemaDumper.ignore_tables` from an `on_load(:active_record)` hook used to get the deprecation warning and a working append (the deprecated accessor exists with its warning, verified at [schema_dumper.rb#L17-L19](https://github.com/rails/rails/blob/main/activerecord/lib/active_record/schema_dumper.rb#L17-L19)). On `main`, whenever Active Record loads **after** initialization - which is development, tests and `bin/rails runner`, but not production where eager loading runs first - the same append hits the already-frozen array and raises `FrozenError: can't modify frozen Array` right after printing the deprecation warning. On 8.1.4 the warning is what you get, no error.

This is not theoretical: the reporter (czj, author_association CONTRIBUTOR) names the real-world breakage - the `actioncable-enhanced-postgresql-adapter` gem (verified to exist on rubygems, v1.0.2), whose railtie appends exactly this way, and whose app "no longer boots in development on main because of it". The repro is a 30-line bundler/inline script. The same initializer freezes `query_transformers`, so any gem appending to that from an `on_load` hook should hit the same wall.

## Who this bites

- Any app on Rails `main` (pre-8.2) whose gems still use the deprecated `SchemaDumper.ignore_tables` or append to `query_transformers` from load hooks: boot fails in development/test while production survives - the worst kind of environment-dependent breakage, because the failure order depends on eager loading.
- The deprecation contract itself: a deprecated API is supposed to keep working while it warns. Freezing the backing array first broke the API before its removal date.

## Limits

- The boot failure and the production-vs-development asymmetry are the reporter's; I verified the freezing initializer, the deprecated accessor, the source PR, the gem's existence, and the v8.1.4 tag, but did not run the repro script (repo ~59k stars).
- The issue is hours old with no comments and no maintainer response; whether the fix is dup-before-freeze, a mutable copy in the deprecated accessor, or an earlier deprecation-removal is open.
- Only the two arrays in that initializer are implicated by the report; other configs frozen by #57852 may have the same shape and are unexamined here.
