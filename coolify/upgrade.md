# Coolify upgrade runbook

For this image → this image, using a **new stack and new volumes**. Run server commands in **Bash as root on the Docker host**. Run sections separately; stop at any error. Rehearse the same procedure on an isolated copy first.

Read the target notes: [5.0.2 → 5.3.0](../docs/upgrade-5.3.md). Never change only the image tag on an old code volume, or attach a newer MariaDB to the old raw database volume.

## 1. Prepare, while the live site stays open

- Pull the target Moodle and MariaDB images from the target Compose template.
- Create a new Coolify service using [compose.yaml](compose.yaml), with new volumes/passwords, the **source database prefix**, and `MOODLE_EMAIL_ENABLED=no`.
- For existing sites, set both `MARIADB_DATABASE` and `MOODLE_DB_NAME` to the source database name. Keep `MOODLE_DB_USER` and `MARIADB_USER` equal. This template defaults to `moodle` / `mdl_`.
- Set `MOODLE_WWWROOT` to the live HTTPS URL. Remove generated domains; do not attach the live domain yet. Keep the destination inaccessible to users and cron disabled.
- Deploy to initialise the new volumes, then stop only its web container. An empty database means web readiness may fail; inspect logs rather than waiting for a fresh installer.
- Confirm disk space for both stacks and backups. Record the source environment, plugins and integration settings privately.

Set actual container names from `docker ps -a` (not display names):

```bash
set -euo pipefail
OLD_WEB='web-REPLACE_OLD_SERVICE_ID'
OLD_DB='database-REPLACE_OLD_SERVICE_ID'
NEW_WEB='web-REPLACE_NEW_SERVICE_ID'
NEW_DB='database-REPLACE_NEW_SERVICE_ID'
TARGET_IMAGE='ghcr.io/innovatics-lab/moodle:5.3.0'
BACKUP="/root/moodle-backups/$(date -u +%Y%m%dT%H%M%SZ)"
umask 077
mkdir -p "$BACKUP"
docker stop --time 60 "$NEW_WEB"
docker inspect "$OLD_WEB" "$OLD_DB" "$NEW_WEB" "$NEW_DB" >/dev/null
df -h /
free -h
```

## 2. Freeze writes and back up

In Coolify disable the **old scheduled cron task**. Pause external workers/imports/webhooks that write to Moodle. Enable maintenance, then wait for active cron/CLI jobs to finish; `docker top` is a process snapshot, not a scheduler lock.

```bash
docker exec --user www-data "$OLD_WEB" php /innovatics/moodle/admin/cli/maintenance.php --enable
docker top "$OLD_WEB" -eo pid,user,etime,args
```

Once workers have finished, stop old web; keep old database running for the dump. No other service may write to it during this backup.

```bash
docker stop --time 60 "$OLD_WEB"
docker inspect "$OLD_WEB" "$OLD_DB" > "$BACKUP/containers.private.json"
# Copy/export the old Coolify Compose and environment configuration into
# $BACKUP/deployment/ privately before proceeding (contains secrets).
mkdir -p "$BACKUP/deployment"
```

Copy the actual service configuration directory shown by Coolify into that directory. Then:

```bash
test -n "$(ls -A "$BACKUP/deployment")"
docker exec "$OLD_DB" sh -ec '
  export MYSQL_PWD="$MARIADB_ROOT_PASSWORD"
  exec mariadb-dump -u root --single-transaction --quick --routines --events --triggers --hex-blob "$MARIADB_DATABASE"
' | gzip > "$BACKUP/database.sql.gz"
docker run --rm --network none --volumes-from "$OLD_WEB":ro   --entrypoint tar "$TARGET_IMAGE" -C /innovatics/moodle -czf - . > "$BACKUP/moodle-code.tar.gz"
docker run --rm --network none --volumes-from "$OLD_WEB":ro   --entrypoint tar "$TARGET_IMAGE" -C /innovatics/moodledata -czf - . > "$BACKUP/moodledata.tar.gz"
gzip -t "$BACKUP/database.sql.gz"
tar -tzf "$BACKUP/moodle-code.tar.gz" >/dev/null
tar -tzf "$BACKUP/moodledata.tar.gz" >/dev/null
tar -C "$BACKUP" -czf "$BACKUP/deployment-config.tar.gz" deployment
(cd "$BACKUP" && sha256sum database.sql.gz moodle-code.tar.gz moodledata.tar.gz deployment-config.tar.gz containers.private.json > SHA256SUMS && sha256sum -c SHA256SUMS)
```

Copy the backup to a separate machine/storage and verify `SHA256SUMS` there (`shasum -a 256 -c SHA256SUMS` on macOS). **Continue only after that succeeds.** The old site remains stopped throughout restoration and cutover.

## 3. Restore the new stack

Verify the destination database has **zero tables**. If not, stop and investigate; never import twice.

```bash
docker exec "$NEW_DB" sh -ec '
  export MYSQL_PWD="$MARIADB_ROOT_PASSWORD"
  mariadb -u root "$MARIADB_DATABASE" -Nse "SHOW TABLES"
'
# The command above must produce no table names.
gzip -dc "$BACKUP/database.sql.gz" | docker exec -i "$NEW_DB" sh -ec '
  export MYSQL_PWD="$MARIADB_ROOT_PASSWORD"
  exec mariadb -u root "$MARIADB_DATABASE"
'
docker run --rm -i --network none --volumes-from "$NEW_WEB"   --entrypoint tar "$TARGET_IMAGE" -C /innovatics/moodledata -xzf - < "$BACKUP/moodledata.tar.gz"
docker run --rm --network none --volumes-from "$NEW_WEB"   --entrypoint chown "$TARGET_IMAGE" -R www-data:www-data /innovatics/moodledata
mkdir "$BACKUP/extracted-code"
tar -xzf "$BACKUP/moodle-code.tar.gz" -C "$BACKUP/extracted-code"
```

Restore **only compatible custom plugins/themes**, never the old core, vendor directory or config.php. Use your reviewed plugin inventory; this cannot safely be inferred from folder names. For 5.3, the destination plugin root is `/innovatics/moodle/public`. Example for one reviewed theme from a 5.0 backup:

```bash
# Replace YOUR_THEME. Repeat for every reviewed extension in its proper directory.
docker cp "$BACKUP/extracted-code/theme/YOUR_THEME" "$NEW_WEB:/innovatics/moodle/public/theme/"
```

For a source using the public layout, source plugins are under `extracted-code/public/`. Apply any rehearsed compatibility patches. Account for all installed plugins before upgrade; do not uninstall missing plugins merely to bypass a warning.

## 4. Upgrade, still closed to users

Start new web without a public route. Restored moodledata retains CLI maintenance mode. Keep email and cron disabled.

```bash
docker start "$NEW_WEB"
docker exec --user www-data "$NEW_WEB" php /innovatics/moodle/admin/cli/maintenance.php --enable
docker exec --user www-data "$NEW_WEB" php /innovatics/moodle/admin/cli/upgrade.php --non-interactive 2>&1 | tee "$BACKUP/upgrade.log"
docker exec --user www-data "$NEW_WEB" php /innovatics/moodle/admin/cli/purge_caches.php
```

Compare user/course counts in old and new databases, substituting your table prefix if different:

```bash
for dbcontainer in "$OLD_DB" "$NEW_DB"; do
  echo "$dbcontainer"
  docker exec "$dbcontainer" sh -ec '
    export MYSQL_PWD="$MARIADB_ROOT_PASSWORD"
    mariadb -u root "$MARIADB_DATABASE" -e "SELECT COUNT(*) AS accounts FROM mdl_user WHERE deleted=0; SELECT COUNT(*) AS courses FROM mdl_course WHERE id<>1;"
  '
done
```

An upgrade error is a stop condition. Keep the log and resolve it on the new stack. Do not run the fresh installer.

## 5. Cut over in Coolify

1. Remove the live domain from the **old** service. Keep it stopped; do not restart it to apply routing changes.
2. Attach the live HTTPS domain to **new web**, internal port **80**, and apply/restart the new service. Confirm no competing old route remains.
3. Disable Moodle maintenance on new web:

```bash
docker exec --user www-data "$NEW_WEB" php /innovatics/moodle/admin/cli/maintenance.php --disable
docker ps --filter "name=$NEW_WEB" --format 'table {{.Names}}	{{.Status}}'
```

4. Test HTTPS, login, courses, quiz/assignment access, upload/download and theme navigation. Reopening enables new writes: note the cutover time.
5. Set `MOODLE_EMAIL_ENABLED=yes` and restart new service. Test SMTP, review queued notifications/quota, then enable **one** cron task on new web using the [setup command](README.md#cron). Inspect its log.
6. Keep old containers/volumes and verified backups through your retention window. Take a new backup of the upgraded site. Do not prune volumes during rollout.

## Rollback

**Before reopening/new writes:** stop new web and its scheduler, remove its domain, reattach the domain to the unchanged old service, start old web, disable its maintenance and resume its cron. Its old database and volumes must be intact.

**After new writes:** stop writes first and back up the new stack. Switching back loses those changes unless reconciled. Plan recovery from the matched old database/code/moodledata backup plus new activity; never point old code at the upgraded database. Do not delete either stack while resolving this.

Upstream: [Moodle upgrade procedure](https://docs.moodle.org/500/en/Upgrade). These commands target this image's paths and MariaDB container environment, not arbitrary third-party images.
