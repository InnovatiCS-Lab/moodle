# Same-version migration

Inventory source versions, plugin/theme files, integrations and configuration. Preserve database, moodledata and plugin code together. Take a consistent backup while web and background writes are stopped, then verify archives and off-server checksums.

Restore to new volumes and credentials with email and cron disabled. Account for CREATE DATABASE and USE statements in SQL dumps. Never point rehearsal containers at production databases. Supply all compatible plugin/theme files; checking version.php alone is insufficient. Do not include the source site credentials file in the image.

Restore file ownership for www-data, omit transient caches/sessions, override the site URL, disable restored maintenance mode and purge caches. Validate logins, enrolments, courses, quizzes, files, theme layouts, HTTPS and restart persistence. Review absolute links and integrations.

At cutover take a fresh backup. Keep old deployment/volumes for rollback, with only one stack allowed to write. Before new writes, routing may be returned to the retained source. After new writes, returning to an older database loses changes; plan reconciliation/recovery. Image rollback does not reverse a database upgrade.
