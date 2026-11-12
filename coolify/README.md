# Coolify

Deploy the published image as a **Docker Compose Empty** service. This is the InnovatiCS image's Coolify integration, not an upstream Moodle distribution.

## New installation

1. Paste [compose.yaml](compose.yaml) into Coolify. Use the file from the Git release tag you are deploying.
2. In **Environment Variables**, set `MOODLE_WWWROOT=https://your-lms.example.org`, `MOODLE_EMAIL_ENABLED=no`, and distinct strong values for `SERVICE_PASSWORD_MOODLEDB` and `SERVICE_PASSWORD_DBROOT`. Confirm generated passwords are populated. Never commit them.
3. In **Domains**, attach your HTTPS hostname to `web`, internal port **80**. Point DNS at the server. Do not publish a database port.
4. Deploy. Database should become healthy; web readiness can fail until Moodle is installed.
5. In Coolify's **Terminal → web**, run the interactive installer:

```sh
runuser -u www-data -- php /innovatics/moodle/admin/cli/install_database.php
```

6. Verify login, file upload/download and HTTPS. Configure SMTP in Moodle, set `MOODLE_EMAIL_ENABLED=yes`, restart the service and test delivery.
7. Add the cron task below and arrange database + code + moodledata backups with an off-server copy.

For an existing site, use [upgrade.md](upgrade.md); **do not run the installer** against a restored database. Bitnami migrations first need the [migration guide](../docs/migration.md): different source paths/configuration are not covered by these commands.

## Cron

In **Scheduled Tasks → Add task**, select service **web**, schedule `* * * * *`, command:

```sh
/usr/sbin/runuser -u www-data -- /usr/bin/flock -n -E 0 /innovatics/moodledata/.scheduled-cron.lock /usr/local/bin/php /innovatics/moodle/admin/cli/cron.php
```

This command runs **inside the container**. From the server shell, prefix it with `docker exec YOUR_WEB_CONTAINER`. Use one scheduler only. A run may remain active for several minutes; the lock skips overlapping executions. Inspect the first execution's log, not just its success badge.

## Versions

Keep one Compose template and one upgrade procedure. Git release tags preserve old templates. Each target's [upgrade notes](../docs/upgrade-5.3.md) record supported source versions, database requirements and layout changes. Do not assume an unlisted version jump works; rehearse it first. Use explicit image versions, never `latest`. Release tags must not be overwritten; our publication workflow checks this, but a tag is not a registry-enforced immutable digest.

## Console locations

- **Environment Variables:** URLs, passwords and email switch.
- **Domains:** HTTPS routing to web port 80; assign the live hostname to only one service.
- **Persistent Storage:** separate code, moodledata and database volumes.
- **Scheduled Tasks:** pause/resume cron.
- **Terminal:** commands inside a selected running container.
- **Runtime Logs:** startup and PHP errors.

See [Coolify services](https://coolify.io/docs/services/) and [scheduled tasks](https://coolify.io/docs/services/operations/scheduled-tasks).
