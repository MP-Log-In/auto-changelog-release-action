"""Resolves and applies git author settings for automated commits."""

from __future__ import annotations

import os

from auto_changelog_release_action.process_utils import run_command_stdout

DEFAULT_AUTHOR_NAME = "CI Bot"
DEFAULT_AUTHOR_EMAIL = "ci@bot.none"
CI_AUTHOR_NAME_ENV = "CI_COMMIT_AUTHOR_NAME"
CI_AUTHOR_EMAIL_ENV = "CI_COMMIT_AUTHOR_EMAIL"


def run_git_config(*args: str) -> str:
    """Run git config and return stripped stdout."""

    return run_command_stdout(["git", *args])


def resolve_git_author(author_name: str | None, author_email: str | None) -> tuple[str, str]:
    """Resolve author inputs with CI environment and hard-coded fallbacks."""

    resolved_name = author_name or os.getenv(CI_AUTHOR_NAME_ENV) or DEFAULT_AUTHOR_NAME
    resolved_email = author_email or os.getenv(CI_AUTHOR_EMAIL_ENV) or DEFAULT_AUTHOR_EMAIL
    return resolved_name, resolved_email


def configure_git_author(author_name: str | None, author_email: str | None) -> tuple[str, str]:
    """Apply the resolved git author settings and verify the final config."""

    resolved_name, resolved_email = resolve_git_author(author_name, author_email)

    print("🔧 Setting up git author:")
    print(f"   Name : {resolved_name}")
    print(f"   Email: {resolved_email}")

    run_git_config("config", "--global", "user.name", resolved_name)
    run_git_config("config", "--global", "user.email", resolved_email)

    configured_name = run_git_config("config", "--global", "user.name")
    configured_email = run_git_config("config", "--global", "user.email")

    if configured_name != resolved_name:
        raise RuntimeError("❌ Error: Git username was not set correctly!")
    if configured_email != resolved_email:
        raise RuntimeError("❌ Error: Git email was not set correctly!")

    print("✅ Git configuration completed successfully.")
    return resolved_name, resolved_email
