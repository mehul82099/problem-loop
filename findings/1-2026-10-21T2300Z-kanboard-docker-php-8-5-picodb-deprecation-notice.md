# Kanboard Docker image: PHP 8.5 deprecation notice shown on MySQL/MariaDB setups

- Source issue: https://github.com/kanboard/kanboard/issues/5931 (open at check time; label: triage needed; opened 2026-10-21 22:01 UTC; 6 comments)
- Project: https://github.com/kanboard/kanboard (MIT, 9,918 stars per the API)
- Releases checked by API: v1.2.55 (2026-10-21 00:57 UTC) and v1.2.56 (2026-10-21 21:28 UTC)
- Checked: 2026-10-21 23:35 UTC

## Problem
A user running the Kanboard Docker image with MariaDB says a message appears in the page header:

`Deprecated: Constant PDO::MYSQL_ATTR_INIT_COMMAND is deprecated since 8.5, use Pdo\Mysql::ATTR_INIT_COMMAND instead in /var/www/app/libs/picodb/lib/PicoDb/Driver/Mysql.php on line 86`

They also say the same text shows up in the container's PHP-FPM error output. They filed it as a bug against v1.2.55.

## What we could check
- The PHP manual's page on features deprecated in PHP 8.5 lists `PDO::MYSQL_ATTR_INIT_COMMAND` among the `PDO::MYSQL_ATTR_*` constants, so the notice text is consistent with the PHP side. (https://www.php.net/manual/en/migration85.deprecated.php)
- In the Kanboard repository, `libs/picodb/lib/PicoDb/Driver/Mysql.php` uses `PDO::MYSQL_ATTR_INIT_COMMAND` on line 86 in the `v1.2.56` tag, so the code the notice points at is the bundled PicoDb library, as one commenter says.
- The `v1.2.55` Dockerfile installs PHP 8.4 packages (`php84`). The `v1.2.56` Dockerfile installs PHP 8.5 (`php85`), and its release notes list a security fix titled "Upgrade the Docker image and runtime configuration from PHP 8.4 to PHP 8.5", citing PHP 8.5.12 and CVE-2026-109618 and CVE-2026-109619. The commit behind it is dated 2026-10-21 21:00 UTC.
- A deprecation about PHP 8.5 can only show up on 8.5. The reporter's path mention, `/etc/php85/conf.d/local.ini` in a comment, and the notice itself fit the 1.2.56 image, not 1.2.55. The issue says v1.2.55, so there is a mismatch. They may have pulled a moving tag. We did not pull any images and cannot say which they ran.
- The v1.2.56 Docker config sets `display_errors = stderr` and `error_reporting = E_ALL` (as a commenter says) in its `local.ini`, with errors also logged to stderr.

## What commenters said
One commenter hand-edited the bundled PicoDb file inside the container to use the new constant. Another pointed to `display_errors = stderr` and said the setting is documented to work only for CGI, CLI and phpdbg SAPIs, and that the deprecated call comes from the PicoDb library. No maintainer had replied at check time. We do not relay the file edit or any change to PHP error settings as advice.

## What this means for readers
- By the evidence above, the notice is most likely a side effect of the Kanboard image moving to PHP 8.5, which was done in the same release as a PHP security upgrade, while a bundled library still uses a constant that PHP 8.5 deprecates. This is our reading, not a maintainer statement.
- A deprecation notice is a warning about future removal. It does not mean the database connection is failing. The reporter does not say anything else is broken.

## Honest limits
- We did not run Kanboard or its images, and did not confirm what the image tag served.
- We did not check whether other database drivers or other bundled libraries trigger similar notices.
- No fix or maintainer response was visible at 23:35 UTC.
