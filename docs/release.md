# Releases and version policy

## Repository structure

`main` contains the current development source. Each release has a Git tag and a GitHub Release that preserve its exact source and documentation. Use a maintenance branch only when an older version requires ongoing fixes; do not duplicate the entire project into version folders.

## Naming

- Git release `v5.3.1` publishes image `ghcr.io/innovatics-lab/moodle:5.3.1`.
- Packaging or dependency fixes for the same Moodle version use `v5.3.1-r1`, then `-r2`, and matching image tags.
- Published version tags must not be moved or overwritten. The workflow checks for an existing registry tag and refuses replacement. This is a workflow guard, not registry-enforced immutability; restrict package write access too.
- Production deployments use an explicitly selected version. No automatic Coolify deployment is triggered.

## CI and publication

Pushes and pull requests run validation only. Publishing a non-prerelease GitHub Release runs the publication workflow: build, volume tests, fresh-install/HTTP tests, registry availability check, then push the tested image. Merely pushing a Git tag does not publish with the current workflow.

Release builds currently target Linux AMD64. Do not advertise ARM64 support until it is built and tested.

## Validation record

5.0.2 was published and deployed following a successful restore rehearsal. 5.3.0 passed local volume and fresh-install tests, a restored-site upgrade and production rollout. The 5.3.1 update must pass its own image tests and restored-site rehearsal; earlier results do not validate the new image.

Before each release, review changes and dependencies, run CI, check for private files and credentials, and review vulnerability scan results. Passing functional tests does not establish that an image has no vulnerabilities. Preserve release notes and rollback instructions alongside the release.
