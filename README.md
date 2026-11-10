# Moodle container baseline

Standard Moodle 5.0.2 container source for a same-version migration rehearsal. Not yet published or approved for production. No third-party themes or site data are included.

## Local validation

Copy .env.example to .env and set separate strong DB_PASSWORD and DB_ROOT_PASSWORD values. Run `docker compose --env-file .env build web`, then `docker compose --env-file .env up -d --wait database`. Start web to initialise the code volume, then install Moodle explicitly using its CLI as www-data. Startup does not initialise or upgrade the database. The example uses http://localhost:8090 and separate named volumes.

The example disables email and cron. It is a local test configuration, not a production deployment. The sanitised source must be built and tested independently before publication.

See [persistent layout](docs/persistent-layout.md), [runtime](docs/runtime.md), [migration](docs/migration.md) and [release status](docs/release.md).

## Licensing

Original packaging code is licensed under GPL-3.0-or-later; see LICENSE. Moodle is GPL-3.0-or-later and retains its upstream notices. Third-party dependencies retain their own licenses. See NOTICE.md.

## Validation

Build the image, then run `TEST_IMAGE=ghcr.io/innovatics-lab/moodle:5.0.2 python3 tests/test_volumes.py`. For Colima, prefix with `DOCKER_CONTEXT=colima`. Tests use uniquely named disposable volumes and no network or database. GitHub Actions runs the same tests without publishing packages. These tests do not replace a full database restore, browser or production deployment test.

First-start code initialisation now requires starting web before running non-root install CLI commands. Web may remain unhealthy until database installation completes. The public image name is ghcr.io/innovatics-lab/moodle:5.0.2; it is not published yet.
