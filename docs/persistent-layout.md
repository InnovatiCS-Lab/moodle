# Persistent code and data

One image: ghcr.io/innovatics-lab/moodle:5.0.2 (local tag until published). Two application volumes: /innovatics/moodle for code including plugins/themes, /innovatics/moodledata for uploaded data. Database storage is separate.

The image carries pristine Moodle in /opt/moodle/core and runtime configuration in /opt/moodle/runtime/config.php. Apache serves the persistent code through /var/www/html, a symlink. On an empty code volume the root entrypoint copies the seed under an exclusive lock and creates a small config.php wrapper. It does not install the database. An interrupted copy fails closed on the next start.

Existing code is never overlaid on restart. version.php must match the seed and config.php must be the known wrapper; otherwise startup stops with a migration message. The version comparison is a guard, not a full integrity or compatibility audit. Unknown old config.php is not overwritten or printed. Existing extensions persist without an image rebuild. Server-side migration scripts may copy reviewed extension directories into the code volume. Web-based plugin installation remains disabled; code is initially root-owned.

For migration: initialise a NEW code volume from the image, copy compatible third-party extension directories into it (including complete theme config.php files), restore the database and moodledata separately, set permissions and environment, then validate. Do not blindly copy an old Bitnami config.php or overlay the old entire core. Apply any necessary plugin compatibility patches to the private volume through a reviewed migration script.

Upgrades are out of scope for this same-version baseline. Changing the image tag to a different Moodle core does NOT silently update persistent code. A tested explicit upgrade command must be supplied before advertising that workflow. Never remove production volumes to bypass the guard.

Local Compose uses pull_policy: never while this image has not been published. Build first. A community production template will use the released registry artifact, not this local build policy. Existing private test Compose files still use the old layout and are deliberately unchanged until this refactor passes isolated tests.
