# Runtime

Required variables: MOODLE_DB_NAME, MOODLE_DB_USER, MOODLE_DB_PASSWORD, MOODLE_DB_PREFIX, MOODLE_WWWROOT. Host defaults to database, port to 3306. Persistent files live at /innovatics/moodledata.

MOODLE_EMAIL_ENABLED=yes explicitly enables Moodle email; default is disabled. This does not block other external plugin requests. Configure SMTP privately through Moodle or a reviewed configuration extension.

MOODLE_SSL_PROXY=yes is for a trusted TLS-terminating proxy. Do not publicly expose the backend directly. Use a fixed canonical URL such as https://lms.example.com. Purge caches after URL changes and test redirects, assets and secure cookies.

Cron uses the same image, database and data volume, runs as www-data, and requires MOODLE_CRON_ENABLED=yes. Set stop_signal: SIGTERM on cron and a sufficient stop_grace_period. Preserve Apache’s stop signal for web. The local example keeps cron disabled even if its profile is selected; explicitly change that only on reviewed test data.

Keep compatible themes/plugins in /innovatics/moodle using a reviewed server-side migration script; no private image is required. Do not mount an entire old core code tree over the updated image. No automatic database upgrade occurs at startup.
