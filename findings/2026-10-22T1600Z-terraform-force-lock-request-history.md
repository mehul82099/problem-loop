# Terraform: a request for `terraform force-lock`, and the history of why it keeps being declined

- Source issue: https://github.com/hashicorp/terraform/issues/39428 (open at check time; labels: enhancement, new; opened 2026-10-21; 6 comments)
- Related issues listed by a maintainer, state checked by API:
  - https://github.com/hashicorp/terraform/issues/17203 "Feature request: allow manual remote state locking" (closed 2018-01-28)
  - https://github.com/hashicorp/terraform/issues/18407 "feature request: lock state subcommand with lock key" (closed 2018-07-06)
  - https://github.com/hashicorp/terraform/issues/23433 "new capability for force locking" (closed 2019-11-20)
  - https://github.com/hashicorp/terraform/issues/28710 "State lock info / unlock for automation purpose" (open)
  - https://github.com/hashicorp/terraform/issues/30277 "Soft state locking" (open)
  - https://github.com/hashicorp/terraform/issues/25051 "state force lock command" (open, linked by the reporter)
- Project: https://github.com/hashicorp/terraform (license shown as NOASSERTION by the API, 50,063 stars)
- Checked: 2026-10-22 16:40 UTC

## The request
The reporter (Terraform 1.16.6) wants a command that does the opposite of `terraform force-unlock`: lock a root module's state on purpose. They use it during maintenance such as merging root modules or migrating a state bucket, so nobody can change the state meanwhile. Today they say they put a lock file into the S3 state bucket by hand with the AWS CLI, which they find fragile when other locking such as DynamoDB is also in use. They would prefer to keep this inside Terraform's own workflow.

## What the thread says
- A maintainer pointed to five earlier issues. We confirmed that three are closed (2018, 2018, 2019) and three are still open (#28710, #30277 and the reporter's own reference #25051).
- A commenter asked whether this duplicates #28710. The reporter answered no: that issue is about listing and removing locks, while this one is about creating them, and they warn that the word "lock" is overloaded.
- On 2026-10-22 a maintainer wrote that #17203 is the most precise duplicate. It was declined because, they say, the original backend design deliberately provides safety guarantees only, not lock durability. They add that this "could be reconsidered" given the work on pluggable state storage, if the new protocol can describe the lock constraints needed. We checked #17203: a maintainer comment from 2018-01-28 says the team decided not to handle this use case, that such options can come from external automation, and that `force-unlock` is a failsafe that only works for some lock types on some backends.
- No commitment, assignee or milestone. A commenter volunteered to implement it. The issue label is `new`, which is the project's untriaged label.

## What this does not tell you
- It does not say Terraform will add this command. The maintainers' latest statement is a possibility, not a plan.
- It is not advice on how to hold a state lock by hand. Putting a lock file in a bucket yourself can leave state stuck or overwrite another lock, depending on the backend. We do not recommend it and did not test it.
- Backend behavior differs. What counts as a lock, and whether it survives, depends on the backend and its settings, which this thread does not detail.

## Honest limits
- We read the issue and the one old maintainer comment in #17203. We did not read the other related issues in full.
- State may have changed since 16:40 UTC.
