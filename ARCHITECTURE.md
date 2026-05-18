# Architecture

This action is a small Python runtime behind a composite action.

## Entry points

- `action.yml` is the public entry point used by workflows.
- `scripts/install-python.sh` ensures Python is available on the runner.
- `python -m auto_changelog_release_action` starts `src/auto_changelog_release_action/__main__.py`.

## Runtime flow

1. `__main__.py` loads the environment and forwards execution to `action_runtime.py`.
2. `action_runtime.py` resolves inputs, writes action outputs, and coordinates the full run.
3. `git_setup.py` configures the git author for generated commits.
4. `version_bump_flow.py` checks commit messages and may bump the version file.
5. If no bump happened, `version_change_flow.py` compares the version value across commits.
6. `cliff_config.py` reads `CLIFF_VERSION` and creates `cliff.toml` from `cliff.toml.template` when needed.
7. `install_git_cliff.py` downloads and installs the required `git-cliff` binary.
8. `release_flow.py` runs when the version changed and handles release changelog generation, changelog commit, tag creation, and API release publication.
9. `unreleased_changelog.py` runs when no release is needed and updates the unreleased changelog instead.

## Supporting modules

- `versioning.py` contains shared version parsing, bumping, matching, and replacement logic.
- `changelog_context.py` enriches `git-cliff` JSON context with merge metadata and prerelease carry-over.
- `process_utils.py` provides the shared subprocess and git wrappers.
- `repository.py` splits repository slugs into owner and repo names.
- `actions_io.py` writes values to `GITHUB_OUTPUT` and `GITHUB_ENV`.

## Design intent

The workflow contract stays in `action.yml`, while the Python modules keep the execution logic testable, reusable, and independent from shell wrappers.