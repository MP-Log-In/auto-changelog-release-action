# Auto Changelog & Release

This composite action updates your changelog and publishes releases from the version stored in your repository.

It is mainly intended for internal use, but the behavior is straightforward: the runtime detects whether it is running on GitHub Actions or Gitea Actions and uses the matching API and changelog links automatically.

## What it does

- reads the version from a file in your repository
- optionally bumps that version based on commit message patterns
- detects whether the version changed between commits
- generates or updates `CHANGELOG.md`
- creates and publishes a release when a new version is present

If no release is needed, the action updates the unreleased changelog section instead.

## Usage

### GitHub

```yaml
name: Release

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: MP-Log-In/auto-changelog-release-action@v1
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          patch_patterns: |
            ^fix:
            ^chore\(deps\):
```

For normal GitHub usage, pinning to `v1` is the expected setup.

### Gitea

```yaml
name: Auto Changelog & Release

on:
  push:
    branches:
      - "main"

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Release
        uses: https://git.0xmax42.io/actions/auto-changelog-release-action@v1
        with:
          token: ${{ secrets.RELEASE_PUBLISH_TOKEN }}
          allow_non_main_release: "true"
          version_file: pyproject.toml
          version_regex: '^version\s*=\s*"([^"]+)"'
```

The inputs are the same on Gitea and GitHub.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `token` | no | `""` | Explicit GitHub or Gitea token used for the release API call. Changelog commits, branch pushes, and tag pushes still use the runner's configured repository credentials. A release cannot be published without it. |
| `author_name` | no | `""` | Git author name for commits created by the action. |
| `author_email` | no | `""` | Git author email for commits created by the action. |
| `allow_non_main_release` | no | `"false"` | If `true`, the action may publish releases from branches other than `main`. |
| `version_file` | no | `"VERSION"` | File that contains the project version. This is the source of truth for tags, changelog entries, and releases. |
| `version_regex` | no | `"^(.*)$"` | Regular expression used to extract the version from `version_file`. If you leave it empty, the runtime chooses a default based on the file name. |
| `github_sha_override` | no | `""` | Optional override for the commit SHA used when calculating the commit range. Mostly useful for tests or unusual workflows. |
| `major_patterns` | no | `""` | Newline-separated regular expressions that trigger a major version bump. |
| `minor_patterns` | no | `""` | Newline-separated regular expressions that trigger a minor version bump. |
| `patch_patterns` | no | `""` | Newline-separated regular expressions that trigger a patch version bump. |

## Version file and regex

The version file is the source of truth. Tags, changelog entries, and releases are derived from it.

The action does not assume that your version lives in a specific file format. It only needs:

- a file that contains the version value
- a regex that extracts that value reliably

The default setup is a plain `VERSION` file with one version string per file:

```text
1.10.0
```

That works with the default `version_regex` of `^(.*)$`.

If your version is stored somewhere else, point `version_file` to that file and set a matching regex. For example, for a Poetry project:

```yaml
with:
  version_file: pyproject.toml
  version_regex: 'version\s*=\s*"([^"]+)"'
```

If the regex does not match, the action fails instead of guessing.

## Bump logic

Automatic version bumps are driven by commit messages in the current push range.

- patterns are evaluated against commit messages
- patterns are newline-separated regular expressions
- major wins over minor, and minor wins over patch
- if no pattern matches, no automatic bump is created
- if all pattern inputs are empty, bumping is effectively disabled

When a bump is triggered, the action updates `version_file`, commits the change, and continues the release flow with the new version.

If no bump is triggered, the action compares the version value across commits. A release is created only when the version actually changed.

## Notes

- `actions/checkout` or the Gitea equivalent should fetch full history. `fetch-depth: 0` is the safest default.
- The default release branch is `main` unless you enable `allow_non_main_release`.
- Generated commits use the configured git author. If you do not set `author_name` and `author_email`, the runner's git configuration is used.
- On both GitHub and Gitea, changelog-only commits and pushes use the repository credentials already configured on the runner, not the explicit `token` input.
- On release runs, changelog commits, branch pushes, and tag pushes still use the runner's configured repository credentials. The explicit `token` input is only used when creating the remote release over the API.
- There is currently no implicit fallback from release publication to the platform default token. If you want to use GitHub's default token for release publication, pass `${{ secrets.GITHUB_TOKEN }}` explicitly.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).