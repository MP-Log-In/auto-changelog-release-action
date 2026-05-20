"""Reads git-cliff versions and materializes cliff.toml from the bundled template."""

from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action.repository import split_repository_slug
from auto_changelog_release_action.runtime_host import RuntimeHost

CLIFF_VERSION_PREFIX = "# CLIFF_VERSION="
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
    host: RuntimeHost,
    repository: str,
    server_url: str,
) -> str:
    """Fill the bundled cliff template with repository and server values."""

    owner, repo = split_repository_slug(repository)
    remote_type = host.value
    compare_operator = "..." if host is RuntimeHost.GITHUB else ".."

    rendered = template_text.replace('owner = "%OWNER%"', f'owner = "{owner}"')
    rendered = rendered.replace('repo = "%REPO%"', f'repo = "{repo}"')
    rendered = rendered.replace("%REMOTE_TYPE%", remote_type)
    rendered = rendered.replace("%COMPARE_OPERATOR%", compare_operator)
    rendered = rendered.replace("%SERVER_URL%", server_url)
    return rendered


def ensure_cliff_config(
    cliff_config_path: Path,
    *,
    templates_root: Path,
    host: RuntimeHost,
    repository: str,
    server_url: str,
) -> bool:
    """Create cliff.toml from the template when the file does not exist yet."""

    if cliff_config_path.exists():
        return False

    template_path = templates_root / CLIFF_TEMPLATE_NAME
    rendered = render_cliff_config_template(
        template_path.read_text(encoding="utf-8"),
        host=host,
        repository=repository,
        server_url=server_url,
    )
    cliff_config_path.write_text(rendered, encoding="utf-8")
    return True
