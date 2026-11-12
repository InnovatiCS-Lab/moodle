#!/bin/sh
# Root-only, locked first-start initialisation. Never overlays existing core.
set -eu
code=/innovatics/moodle
data=/innovatics/moodledata
seed=/opt/moodle/core
mkdir -p "$code" "$data"
exec 9>"$code/.image-init.lock"
flock -x 9
if [ -e "$code/.image-init-incomplete" ]; then
    echo 'Previous code initialisation was interrupted. Recover or recreate the empty code volume; refusing to serve partial code.' >&2
    exit 1
fi
if [ -z "$(find "$code" -mindepth 1 -maxdepth 1 ! -name .image-init.lock -print -quit)" ]; then
    touch "$code/.image-init-incomplete"
    cp -a "$seed/." "$code/"
    printf '%s\n' '<?php require "/opt/moodle/runtime/config.php";' > "$code/config.php"
    rm "$code/.image-init-incomplete"
fi
if ! cmp -s "$seed/public/version.php" "$code/public/version.php"; then
    echo 'Persistent Moodle core does not match this image. No files were upgraded. Use the documented migration/upgrade procedure.' >&2
    exit 1
fi
expected='<?php require "/opt/moodle/runtime/config.php";'
if [ ! -f "$code/config.php" ] || [ "$(cat "$code/config.php")" != "$expected" ]; then
    echo 'Existing site config.php requires explicit migration to the environment-driven configuration; refusing to overwrite it.' >&2
    exit 1
fi
chown www-data:www-data "$data"
chmod 2770 "$data"
