# Moodle Docker image

Run Moodle with persistent application code and uploaded files, using one image for fresh installations and migrations. Themes and plugins live in the code volume and survive container replacement without rebuilding the image.

Images: `ghcr.io/innovatics-lab/moodle` · [Releases](https://github.com/InnovatiCS-Lab/moodle/releases)

## Features

- Apache, PHP with OPcache, and the PHP extensions required by Moodle.
- Persistent `/innovatics/moodle` and `/innovatics/moodledata` volumes.
- Locked initialisation with protection against interrupted copies and mismatched Moodle versions.
- Environment-based database configuration; explicit database installation and upgrades.
- Separate web and optional cron processes, with graceful cron shutdown.
- For Moodle 5.3, only the `public/` directory is served over HTTP.
- Release builds tested before publication to GitHub Container Registry.

## Versions

- **5.0.2:** published and used for a completed production migration from Bitnami.
- **5.3.0:** this branch targets Moodle 5.3, PHP 8.4 and MariaDB 11.4. Fresh-install tests and a restored-site upgrade have passed locally. Publication and production rollout are separate steps.

Previous source versions are preserved in Git tags, such as `v5.0.2`. Use a version tag to browse or check out its matching Dockerfile, Compose file and documentation. There is no duplicated directory for every release. See [release policy](docs/release.md).

## Build and run locally

```sh
cp .env.example .env
# Edit .env: set distinct, strong DB_PASSWORD and DB_ROOT_PASSWORD values.
docker compose --env-file .env build web
docker compose --env-file .env up -d --wait database
docker compose --env-file .env up -d web
```

Initialise the database interactively, choosing your own administrator credentials:

```sh
docker compose --env-file .env exec --user www-data web \
  php admin/cli/install_database.php
```

Open **http://localhost:8090**. The web health check becomes healthy after installation. This example binds to localhost and disables email and cron. Configuration defaults in `.env.example` are examples, not deployment credentials; keep the real `.env` outside Git.

For existing sites, restore the database, uploaded files and compatible plugins using the [migration guide](docs/migration.md). Do not run the fresh installer against a restored database.

## Validation

```sh
TEST_IMAGE=ghcr.io/innovatics-lab/moodle:5.3.0 python3 tests/test_volumes.py
TEST_IMAGE=ghcr.io/innovatics-lab/moodle:5.3.0 \
  TEST_DB_IMAGE=mariadb:11.4.13 python3 tests/test_install.py
```

For Colima, prefix each command with `DOCKER_CONTEXT=colima`. Tests use disposable resources. They cover concurrent initialisation, persistence, version/configuration guards, fresh database installation, HTTP access boundaries and container replacement.

A restored Moodle 5.0.2 site has also completed the CLI upgrade to 5.3 locally. Site-specific themes and integrations need their own checks; the public image contains no third-party themes or private site data.

## Deployment and upgrades

Use the same image for web and cron. Keep the database on a private network, configure HTTPS at the reverse proxy, and store secrets outside the repository. Startup does not automatically upgrade your database or replace existing Moodle code. Changing the image tag alone is not a complete upgrade procedure.

Before upgrading, back up the database, code and moodledata together and rehearse restoration. See [5.3 upgrade guide](docs/upgrade-5.3.md), [persistent layout](docs/persistent-layout.md) and [runtime configuration](docs/runtime.md).

## License

Packaging code and Moodle are GPL-3.0-or-later. Upstream and dependency notices are retained. See [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).
