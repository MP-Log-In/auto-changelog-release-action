"""Reads git-cliff versions and materializes cliff.toml from the bundled template."""

from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action.repository import split_repository_slug

CLIFF_VERSION_PREFIX = "# CLIFF_VERSION="
DEFAULT_GITEA_SERVER_URL = "https://git.0xmax42.io"
DEFAULT_CLIFF_CONFIG = "cliff.toml"
CLIFF_TEMPLATE_NAME = "cliff.toml.template"


def extract_cliff_version(text: str) -> str | None:
    """Extract the optional CLIFF_VERSION marker from a cliff config file."""

    for line in text.splitlines():
        if not line.startswith(CLIFF_VERSION_PREFIX):
            continue

        version = line.split("=", 1)[1].replace('"', "").replace(" ", "")
        return version or None

    return None


def read_cliff_version(cliff_path: Path) -> str | None:
    """Read and parse the CLIFF_VERSION marker from disk."""

    return extract_cliff_version(cliff_path.read_text(encoding="utf-8"))


def render_cliff_config_template(
    template_text: str,
    *,
    repository: str,
    server_url: str,
) -> str:
    """Fill the bundled cliff template with repository and server values."""

    owner, repo = split_repository_slug(repository)

    rendered = template_text.replace('owner = "%OWNER%"', f'owner = "{owner}"')
    rendered = rendered.replace('repo = "%REPO%"', f'repo = "{repo}"')
    rendered = rendered.replace("%GITEA_SERVER_URL%", server_url)
    return rendered


def ensure_cliff_config(
    cliff_config_path: Path,
    *,
    template_path: Path,
    repository: str,
    server_url: str,
) -> bool:
    """Create cliff.toml from the template when the file does not exist yet."""

    if cliff_config_path.exists():
        return False

    rendered = render_cliff_config_template(
        template_path.read_text(encoding="utf-8"),
        repository=repository,
        server_url=server_url,
    )
    cliff_config_path.write_text(rendered, encoding="utf-8")
    return True
