# Publishing

Pushes and pull requests run validation only. Publishing a non-prerelease GitHub Release triggers publish.yml, which builds and tests before pushing that exact local image to GHCR. Pushing a Git tag alone does not publish an image. No workflow deploys to Coolify.

First release: v5.0.2 -> ghcr.io/innovatics-lab/moodle:5.0.2. Later packaging changes may use v5.0.2-r1 -> :5.0.2-r1. A revision can update container scripts or dependencies while retaining Moodle 5.0.2. Tags are not intentionally reused; the workflow checks whether the version already exists. Registry access checks are not an absolute immutability guarantee: restrict who can publish or delete packages. No latest tag or floating version alias is automatically moved.

The initial workflow builds linux/amd64. Additional platforms require compatible base manifests and validation before being added. The published digest is recorded in the workflow summary; use it to pin production. GitHub's job-scoped GITHUB_TOKEN uses contents:read and packages:write; no personal registry token or server credentials are needed. Verify package visibility after first publication; a public repository does not alone prove the image can be pulled anonymously.

Before publication, review the release source, run CI and complete release gates. Protect the main branch and release tags through repository rules as available. Never recreate a failed release tag at a different commit. A failed test must be fixed and rerun before publication. Test pulling the published artifact before manually preparing a Coolify deployment with backup and rollback.
