"""CLI module that boots the package runtime for the composite action."""

from __future__ import annotations

import re

from auto_changelog_release_action import action_runtime
from auto_changelog_release_action.runtime_host import RuntimeHost

PYPROJECT_SECTION_PATTERN = re.compile(r"(?ms)^\[tool\.poetry\]\s*(.*?)(?:^\[|\Z)")
PYPROJECT_VERSION_PATTERN = re.compile(r'^version\s*=\s*"([^"]+)"\s*$', re.MULTILINE)


def resolve_action_version(config: action_runtime.ActionRuntimeConfig) -> str:
    """Resolve the action version from the action's pyproject metadata."""

    pyproject_file = config.action_path / "pyproject.toml"
    try:
        pyproject_text = pyproject_file.read_text(encoding="utf-8")
    except OSError:
        return "unknown"

    section_match = PYPROJECT_SECTION_PATTERN.search(pyproject_text)
    if not section_match:
        return "unknown"

    version_match = PYPROJECT_VERSION_PATTERN.search(section_match.group(1))
    if not version_match:
        return "unknown"

    return version_match.group(1)


def format_runtime_host(host: RuntimeHost) -> str:
    """Format the detected runtime host for startup logging."""

    if host is RuntimeHost.GITHUB:
        return "GitHub"
    return "Gitea"


def main() -> int:
    """Load environment config and execute the full action runtime."""

    config = action_runtime.config_from_environment()
    print(f"Action version: {resolve_action_version(config)}")
    print(f"Detected runtime host: {format_runtime_host(config.host)}")
    action_runtime.run_action_runtime(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
