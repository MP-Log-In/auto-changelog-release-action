"""CLI module that boots the package runtime for the composite action."""

from __future__ import annotations

from auto_changelog_release_action import action_runtime


def main() -> int:
    """Load environment config and execute the full action runtime."""

    config = action_runtime.config_from_environment()
    action_runtime.run_action_runtime(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
