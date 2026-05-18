"""Detects semantic version bumps from commit messages and updates the version file."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from auto_changelog_release_action.process_utils import run_git_stdout
from auto_changelog_release_action.versioning import (
    bump_version,
    detect_bump,
    parse_patterns,
    replace_version,
)


@dataclass(frozen=True)
class VersionBumpConfig:
    """Inputs required to decide and apply a version bump."""

    version_file: str
    version_regex: str
    major_patterns_raw: str
    minor_patterns_raw: str
    patch_patterns_raw: str
    revision_range: str
    allow_non_main_release: bool
    git_ref: str


@dataclass(frozen=True)
class VersionBumpResult:
    """Result of a version bump attempt."""

    version_bumped: bool
    version_after: str | None = None


def run_git(args: list[str]) -> str:
    """Run git and return stripped stdout."""

    return run_git_stdout(args)


def get_commit_messages(revision_range: str) -> list[str]:
    """Return commit messages from the configured revision range."""

    output = run_git(["log", "--format=%B%x00", revision_range])
    return [message.strip() for message in output.split("\x00") if message.strip()]


def run_version_bump(config: VersionBumpConfig) -> VersionBumpResult:
    """Detect and commit a version bump when the configured patterns match."""

    if (not config.allow_non_main_release) and (config.git_ref != "refs/heads/main"):
        print(
            "🚫 Not on 'main' branch and non-main releases are disabled – skipping version check."
        )
        return VersionBumpResult(version_bumped=False)

    messages = get_commit_messages(config.revision_range)
    if not messages:
        return VersionBumpResult(version_bumped=False)

    bump = detect_bump(
        messages,
        major_patterns=parse_patterns(config.major_patterns_raw),
        minor_patterns=parse_patterns(config.minor_patterns_raw),
        patch_patterns=parse_patterns(config.patch_patterns_raw),
    )
    if bump is None:
        return VersionBumpResult(version_bumped=False)

    path = Path(config.version_file)
    content = path.read_text(encoding="utf-8")
    match = re.search(config.version_regex, content, flags=re.MULTILINE)
    if not match:
        raise RuntimeError("Version regex did not match")

    old_version = match.group(1) if match.lastindex else match.group(0)
    new_version = bump_version(old_version, bump)
    if old_version == new_version:
        return VersionBumpResult(version_bumped=False)

    path.write_text(
        replace_version(content, config.version_regex, new_version),
        encoding="utf-8",
    )
    run_git(["add", str(path)])
    run_git(
        [
            "commit",
            "-m",
            f"chore(version): bump version to {new_version}",
            "-m",
            "Automated version bump based on commit message patterns.",
        ]
    )
    print(f"Version bumped: {old_version} → {new_version}")
    return VersionBumpResult(version_bumped=True, version_after=new_version)
