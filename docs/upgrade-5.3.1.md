# Moodle 5.3.0 → 5.3.1

Target: `ghcr.io/innovatics-lab/moodle:5.3.1`, upstream tag `v5.3.1`, commit `cfe123f26fc7071981fe949cb16cd5a08a8234f1` (build 20261112, database version 2026100501).

Keep MariaDB 11.4.13 and the existing PHP 8.4 base for this update. No database-engine version change is needed.

Follow the [Coolify upgrade runbook](../coolify/upgrade.md) using separate destination volumes. Even a patch release requires new core files and the CLI database upgrade; changing only the image tag will trigger the persistent-code version guard.

1. Build and test the image, then rehearse against a recent backup with email and cron disabled.
2. Freeze production writes and take a matched database, code, moodledata and deployment backup.
3. Restore into the new stack. Copy compatible custom plugins from `extracted-code/public/`; do not restore old core, vendor or config.php.
4. Run the CLI upgrade and cache purge. Compare records and test login, profile save, course access, uploads and theme navigation.
5. Switch routing, reopen, verify email, and enable only the new cron task. Retain the old stack and backup for rollback.

The existing Nice theme and private styling are not included in the public image; verify them separately. Do not assume this maintenance release fixes theme compatibility issues.

[Upstream release notes](https://moodledev.io/general/releases/5.3/5.3.1)
