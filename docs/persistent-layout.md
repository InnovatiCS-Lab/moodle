# Persistent code and data

Two application volumes persist across container replacement: `/innovatics/moodle` for code, configuration and plugins, and `/innovatics/moodledata` for uploaded files and runtime data. Database storage is separate.

For Moodle 5.3, Apache serves only `/innovatics/moodle/public`. Plugins and themes live beneath that directory. See [version notes](versions/README.md) for migration differences.

The image carries pristine code in `/opt/moodle/core` and environment-driven configuration in `/opt/moodle/runtime/config.php`. On an empty code volume the entrypoint copies the seed under an exclusive lock and creates the root config.php wrapper. It does not install the database. Interrupted initialisation fails closed.

Existing core is never overlaid on restart. Its `public/version.php` must match the seed and config.php must be the supported wrapper; otherwise startup stops. This is a version guard, not a full integrity or plugin-compatibility audit. Unknown configuration is not overwritten. Compatible extensions persist without rebuilding the image; web-based plugin installation remains disabled.

Upgrades require fresh core and reviewed compatible extensions. Do not overlay an old core tree or blindly copy a Bitnami config.php. Changing only the image tag does not update persistent files or the database. Never delete production volumes to bypass the guard.

Use the [general upgrade rules](versions/README.md#upgrade-rules-for-every-environment) and, for Coolify, the [upgrade runbook](../coolify/upgrade.md). Keep private plugins, patches and site data outside the public image and repository.
