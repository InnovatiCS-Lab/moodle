#!/bin/sh
set -eu
if [ "$(id -u)" = 0 ]; then
    /usr/local/bin/init-code.sh
else
    # Non-root CLI/cron must start after the root web initialiser has completed.
    test ! -e /innovatics/moodle/.image-init-incomplete
    cmp -s /opt/moodle/core/public/version.php /innovatics/moodle/public/version.php || {
        echo 'Code volume is not initialised or has a different version. Start web first.' >&2
        exit 1
    }
    test -r /innovatics/moodle/config.php
fi
cd /innovatics/moodle
exec docker-php-entrypoint "$@"
