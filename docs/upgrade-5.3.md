# Moodle 5.3 upgrade rehearsal

Status: local restore and database upgrade completed. Use separate volumes for the production upgrade.

## Verified target

- Moodle v5.3.0, commit `42622298fe06f9626d988d60b2bf589bd8f850e8`.
- PHP 8.4.27 Apache on Debian Bookworm, pinned build input in Dockerfile.
- MariaDB 11.4.13 for testing. Existing MariaDB 11.1 data must be logically exported and restored into a **new** database volume; never reuse its raw volume with the new server.
- Application volumes remain `/innovatics/moodle` and `/innovatics/moodledata`.
- Apache now serves `/innovatics/moodle/public`. Plugins and themes belong under that public directory. Root config.php and vendor dependencies remain outside the web root.
- Composer installs the upstream lock file with development dependencies, scripts and plugins disabled. No dependency update is performed.

Sources: [Moodle 5.3 requirements](https://moodledev.io/general/releases/5.3), [upgrading Moodle](https://docs.moodle.org/503/en/Upgrading_Moodle).

## Rehearsal sequence

1. Build and validate the new image on disposable volumes with a fresh database.
2. Take a current backup of database, code/plugins, moodledata and deployment configuration; verify checksums. Keep it outside the repository.
3. Restore that database into a separate MariaDB 11.4.13 instance and restore moodledata into a separate volume.
4. Initialise a fresh code volume from the new image image. Do not overlay 5.0 core code or copy its config.php. The entrypoint deliberately refuses a different-version code volume.
5. Inventory **all** installed non-core plugins, not just the active theme. Copy only reviewed compatible extensions to their new paths under `public/`. Retain originals and any patches privately. Missing plugins are a stop condition, not permission to uninstall their data.
6. Keep email disabled, cron stopped and browser access local/restricted. External plugin integrations also require review: disabling Moodle email is not a network sandbox.
7. Run Moodle's CLI upgrade as www-data against the restored copy. Capture its output and compare account/course counts before and after.
8. Test login, enrolment, course files, quizzes, uploads, theme layouts, background tasks, TLS proxy behavior and restart persistence. Test both Boost and the site's actual theme.
9. Rehearse rollback by restoring the original matched database, code and data set separately. An upgraded database cannot be rolled back by changing only the image tag.
10. Publish only after the new image passes. Production cutover gets a fresh write-frozen backup and the same rehearsed steps.

## Release gates

- Image build, extension/platform checks, volume guards, fresh install and HTTP security checks pass.
- Same-version restart preserves plugins, files and configuration.
- Real backup upgrade and rollback restoration pass; plugin compatibility is recorded.
- Dependency and image vulnerability findings are reviewed and documented before release.
- No private configuration, site data or proprietary extensions enter the public build context.
- Publish immutable release tags; use a new revision for packaging fixes. Deployment stays manual.

This project does not yet claim an SLA, high availability, security certification or tested support for every architecture. Those require evidence and an ongoing support process.

## Local validation — 11 November 2026

Image `ghcr.io/innovatics-lab/moodle:5.3.0` built successfully on Colima (linux/amd64).

- Shell and Python syntax checks passed.
- `tests/test_volumes.py` passed concurrent initialization, interrupted-copy and version guards, config preservation, and plugin/data persistence.
- `tests/test_install.py` passed a fresh Moodle installation on MariaDB 11.4.13, HTTP readiness, protected-file checks, and container replacement with retained database/data.
- Disposable test containers, volumes and networks were removed by the tests. Existing local restore resources were retained.

The production-backup restore subsequently completed the CLI upgrade from 5.0.2 to 5.3. The restored site contained 25,560 non-deleted accounts and 11 courses; login and course pages were confirmed working. Site-specific theme styling remains under review in the private deployment repository. Vulnerability scanning, other CPU architectures, registry publication and the 5.3 production rollout are not established by these local results.
