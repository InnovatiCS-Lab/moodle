# Container versions

These notes apply to Docker Compose, Coolify and other container environments. Use source and templates from the Git tag matching the image. Git tags preserve previous documentation; individual patch release notes belong in GitHub Releases, not duplicate folders.

## Moodle 5.3

- Images: `ghcr.io/innovatics-lab/moodle:5.3.0` and `:5.3.1`.
- Runtime: PHP 8.4.28 in `5.3.1-r1` (8.4.27 in the original 5.3.0/5.3.1 images), with Apache on Debian Bookworm; build inputs are pinned in the Dockerfile. Composer installs upstream locked dependencies without development packages, plugins or scripts.
- Tested database: MariaDB 11.4.13. Migrating from MariaDB 11.1 requires a logical dump restored into a new database volume; do not reuse its raw volume with the new engine.
- Application volumes: `/innovatics/moodle` and `/innovatics/moodledata`; database storage is separate.
- Web root: `/innovatics/moodle/public`. Themes/plugins belong beneath `public/`; root configuration and vendor dependencies remain outside the served directory.
- Release builds target Linux AMD64; other architectures are not advertised as tested.

### 5.3.0

Upstream tag `v5.3.0`, commit `42622298fe06f9626d988d60b2bf589bd8f850e8`. Moodle reports release `5.3`, database version `2026100500`.

The 5.0.2 → 5.3.0 transition passed local restore rehearsal and production upgrade. It required fresh core, the new public-directory plugin layout and a separate MariaDB 11.4 volume. Preserve compatible extensions and their reviewed patches; do not restore old core or deployment-specific config.php over the target image.

### 5.3.1

Upstream tag `v5.3.1`, commit `cfe123f26fc7071981fe949cb16cd5a08a8234f1`, build 20261112, database version `2026100501`.

The 5.3.0 → 5.3.1 transition passed local rehearsal and production upgrade using the same stack. MariaDB 11.4.13, paths and configuration stayed unchanged. Fresh core and the CLI database upgrade were still required. Private theme patches are not part of the public image.

### 5.3.1-r1

Packaging security update: PHP 8.4.27 → 8.4.28, with the Docker base pinned by digest. Moodle source, database version, MariaDB version and persistent paths are unchanged. Build and validation are required before publication.

After testing and backing up, pause cron and deploy the new image to web and any separate cron container, retaining existing volumes and configuration. No Moodle CLI database upgrade or core-volume replacement is required for this runtime-only revision. Verify the running PHP version, health, login and cron before resuming normal operations. Do not modify PHP inside a running container; rebuild the image instead.

[Upstream 5.3 requirements](https://moodledev.io/general/releases/5.3) · [5.3.1 release notes](https://moodledev.io/general/releases/5.3/5.3.1)

## Upgrade rules for every environment

1. Review target requirements and all custom plugins. Rehearse an isolated restore with email and cron disabled and external integrations restricted.
2. Freeze writers and take a matched database, code, moodledata and deployment backup; verify an off-server copy.
3. Prepare fresh core, preserving compatible extensions and the supported configuration. An image-tag change alone does not upgrade persistent code.
4. Run the CLI database upgrade as `www-data`, purge caches and compare records. Test login, courses, profile editing, files, theme navigation, email and cron.
5. Retain the matched backup. Once a database upgrade has been attempted, old code alone is not a rollback. Account for activity written after reopening before restoring older data.

Coolify console steps and commands live in the single [upgrade runbook](../../coolify/upgrade.md). Other environments apply these rules using their own deployment tooling. See [persistent storage](../persistent-layout.md), [runtime configuration](../runtime.md) and [release policy](../release.md).

### 5.3.1-r2

Adds Ghostscript for assignment PDF annotation and a conversion/rendering check running as `www-data`. Moodle core and PHP versions are unchanged from r1; this image-only update does not require a Moodle database upgrade.
