# Baseline release status

Scope: Moodle 5.0.2 same-version container migration. Upgrades are deferred. Pins reproduce the migration baseline; they are not a claim of current security support.

## Verified locally

- Public image build and Apache syntax.
- Empty code/data volume initialisation and persistence across replacement.
- Third-party theme persisted without rebuilding the image.
- Existing site restored into separate code, data and database volumes using the same public image; UI/files and container replacement passed user validation.

Earlier runtime tests covered SMTP delivery, cron SIGTERM shutdown and local HTTPS. These should be repeated for the final persistent-layout deployment, not assumed to prove the final production configuration.

## Remaining release gates

- Test version-mismatch and interrupted-initialisation guards and concurrent startup.
- Finalise packaging-code license and distribution/source notices before publishing.
- Add CI build/validation, image scanning and immutable release identifiers.
- Review source, Git contents and image layers for secrets/private material.
- Validate final Coolify Compose, HTTPS, cron, SMTP and backup/rollback.
- Publish the reviewed artifact, test pulling it, and schedule fresh-backup cutover.

No Git repository or registry package has been created.
