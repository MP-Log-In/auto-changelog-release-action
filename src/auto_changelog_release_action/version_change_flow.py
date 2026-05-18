"""Compares version values across commits to decide whether a release should run."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from auto_changelog_release_action.process_utils import run_git
from auto_changelog_release_action.versioning import extract_version

ZERO_SHA = "0" * 40


@dataclass(frozen=True)
class VersionChangeConfig:
    """Inputs required to compare version values across two commits."""

    git_ref: str
    commit_before: str
    commit_after: str
    allow_non_main_release: bool
    version_file: str
    version_regex: str


@dataclass(frozen=True)
class VersionChangeResult:
    """Result of the version change comparison."""

    version_changed: bool
    version_before: str | None = None
    version_after: str | None = None


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run git while merging stderr into stdout for diagnostics."""

    return run_git(args, check=check, merge_stderr=True)


def ensure_before_commit(commit_before: str, commit_after: str) -> str:
    """Recover a usable parent commit when the event payload has no before SHA."""

    if not commit_before or commit_before == ZERO_SHA:
        try:
            parent = git("rev-parse", f"{commit_after}^").stdout.strip()
            if parent:
                return parent
        except subprocess.CalledProcessError:
            pass
    return commit_before


def git_diff_name_only(commit_before: str, commit_after: str) -> list[str]:
    """List changed files without failing the action on diff errors."""

    if not commit_before or not commit_after:
        return []
    try:
        output = git("diff", "--name-only", commit_before, commit_after).stdout
        return [line.strip() for line in output.splitlines() if line.strip()]
    except subprocess.CalledProcessError as error:
        print("📄 Changed files:")
        print("(diff failed)")
        if error.stdout:
            print(error.stdout.strip())
        return []


def git_show_file(commit: str, path: str) -> str | None:
    """Read a file from a specific git revision if it exists."""

    if not commit or not path:
        return None
    try:
        return git("show", f"{commit}:{path}").stdout
    except subprocess.CalledProcessError:
        return None


def run_version_change_detection(config: VersionChangeConfig) -> VersionChangeResult:
    """Compare the version value across commits and report whether it changed."""

    print("🔍 Comparing commits:")
    print(f"Before: {config.commit_before}")
    print(f"After:  {config.commit_after}")
    print(f"Ref:    {config.git_ref}")
    print(f"Allow release from non-main branches: {str(config.allow_non_main_release).lower()}")
    print(f"Version file: {config.version_file}")
    print(f"Version regex: {config.version_regex}")

    if (not config.allow_non_main_release) and (config.git_ref != "refs/heads/main"):
        print(
            "🚫 Not on 'main' branch and non-main releases are disabled – skipping version check."
        )
        return VersionChangeResult(version_changed=False)

    commit_before = ensure_before_commit(config.commit_before, config.commit_after)
    commit_after = config.commit_after
    changed_files = git_diff_name_only(commit_before, commit_after)
    print("📄 Changed files:")
    if changed_files:
        for path in changed_files:
            print(path)
    else:
        print("(none)")

    file_changed = config.version_file in changed_files
    before_text = git_show_file(commit_before, config.version_file) if commit_before else None
    after_text = git_show_file(commit_after, config.version_file) if commit_after else None

    version_before: str | None = None
    version_after: str | None = None
    if after_text is not None:
        try:
            version_after = extract_version(after_text, config.version_regex)
        except ValueError as error:
            print(f"⚠️ Could not extract version from AFTER commit: {error}")
    if before_text is not None:
        try:
            version_before = extract_version(before_text, config.version_regex)
        except ValueError as error:
            print(f"⚠️ Could not extract version from BEFORE commit: {error}")

    if version_before is not None and version_after is not None:
        version_changed = version_before != version_after
        print(f"🔢 Version before: {version_before}")
        print(f"🔢 Version after:  {version_after}")
        if version_changed:
            print("✅ Version value changed (semantic compare)")
        else:
            print("ℹ️ Version value unchanged (semantic compare)")
        return VersionChangeResult(
            version_changed=version_changed,
            version_before=version_before,
            version_after=version_after,
        )

    if file_changed:
        print("✅ Version file changed (fallback, semantic compare unavailable)")
    else:
        print("ℹ️ Version file not changed (fallback)")
    return VersionChangeResult(
        version_changed=file_changed,
        version_before=version_before,
        version_after=version_after,
    )
