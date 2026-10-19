# django-celery-beat pins Django below 6.1, and the fix is waiting on a release (django-celery-beat#1079)

- Source: https://github.com/celery/django-celery-beat/issues/1079 "Django 6.1 Support". Opened 2026-08-11, open, 26 comments, 32 reactions on the post, last comment 2026-10-19.
- Checked on 2026-10-19:
  - PyPI (https://pypi.org/project/django-celery-beat/): the latest version is 2.9.0, uploaded 2026-02-28. Its declared requirement is `Django>=2.2,<6.1`. The two releases before it are 2.8.1 (2025-05-13) and 2.8.0 (2025-04-16).
  - GitHub releases API: the newest published release is v2.9.0 (2026-02-28). The issue refers to a draft release v2.10.0, and drafts do not show in the public API, so I could not check it.
  - Commits on master are still arriving (the latest two days before, 2026-10-16, were dependency bumps and "Fix for celery v5.7b1").
  - https://github.com/celery/django-celery-beat/pull/1092 "Use stable Django 6.1 in test matrix" is merged.
- Django's announcement of an annual release cycle: https://www.djangoproject.com/weblog/2026/aug/10/annual-release-cycle/ (dated 2026-08-10).

## The problem
django-celery-beat stores Celery periodic tasks in the Django database. Version 2.9.0 declares `Django<6.1`, so pip and similar tools refuse to install it next to Django 6.1.

## What the thread says
- On 2026-08-12 a contributor (cclauss) says tests already run on Django 6.1 in the project's CI, and what is missing is a new release on PyPI. On 2026-08-14 he asks two repository members to review a draft release.
- 2026-09-09: a member (auvipy) says he will release all Celery-related packages that month and asks people to wait. As of 2026-10-19 the PyPI page above still shows 2.9.0 as the latest.
- Why the upper limit exists, per cclauss: a crash bug appeared with the Django 5.0 to 5.1 upgrade, so the project tests before allowing new versions. Another commenter notes Django will have no 7.0 (per the annual release post), so an upper bound of `<7.0` would not work as hoped.
- People pinged repeatedly through September and October. Some are frustrated, one says the package took three years to support Django 6.0 (his claim, unverified), another replies that maintainers owe users nothing without a contract and suggests forking, and another calls that disrespectful and asks for transparency on what blocks the release. 2026-10-19: a contributor suggests adding co-maintainers.

## Workarounds users posted (unvetted)
- A tool-specific override for the `uv` package manager that relaxes the Django requirement for this package. Overriding a pin means you take on the compatibility risk, and the maintainer's stated reason for the pin is a past crash.
- A user-published fork on PyPI, described by its author as temporary. I did not inspect its code, and installing a third-party fork for a package that runs your task scheduler is a supply-chain decision for you to make.
- Replacing the package with your own code or Django's newer built-in tasks framework, as another commenter suggests. I did not evaluate it.

## What can be said
- The compatibility work seems to be done in the test matrix and the blocker is releasing. The maintainers have said a release is coming, but have not given a date, and the date they gave (September) has passed.
- Until a release, projects that want Django 6.1 have to accept an override or a fork, or stay on Django 6.0 or older.

## Honest limits
- I did not run the test suite or try Django 6.1 with 2.9.0.
- I could not see the draft release, and I do not know what is holding it up.
- I did not inspect the third-party fork or the override.
