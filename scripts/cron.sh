#!/bin/sh
set -eu
if [ "${MOODLE_CRON_ENABLED:-no}" != yes ]; then
    echo 'Cron disabled. Set MOODLE_CRON_ENABLED=yes only after reviewing task side effects.' >&2
    exit 1
fi
child=
stop() {
    trap - TERM INT
    if [ -n "$child" ]; then
        kill -TERM "$child" 2>/dev/null || true
        wait "$child" 2>/dev/null || true
    fi
    exit 0
}
trap stop TERM INT
while :; do
    php /innovatics/moodle/admin/cli/cron.php &
    child=$!
    status=0
    wait "$child" || status=$?
    child=
    [ "$status" -eq 0 ] || exit "$status"
    sleep 60 &
    child=$!
    wait "$child"
    child=
done
