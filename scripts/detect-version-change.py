#!/usr/bin/env python3
"""
Check whether the project version changed between two commits.

This is a Python replacement for the Bash snippet you posted, with two key upgrades:
- The "version file" can be configured via ENV (VERSION_FILE).
- The version can be extracted via a configurable regex (VERSION_REGEX) from that file
  at BOTH commits, so you can detect "real" version changes (not just "file touched").

It writes:
- GITHUB_OUTPUT: version_changed=true|false
- GITHUB_ENV:    VERSION_CHANGED=true|false

Additionally (non-breaking extra outputs/envs):
- GITHUB_OUTPUT: version_before=..., version_after=...
- GITHUB_ENV:    VERSION_BEFORE=..., VERSION_AFTER=...
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass
from typing import Optional, Sequence


ZERO_SHA = "0" * 40


@dataclass(frozen=True)
class Ctx:
    git_ref: str
    commit_before: str
    commit_after: str
    allow_non_main_release: bool
    version_file: str
    version_regex: str


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _run(cmd: Sequence[str], check: bool = True) -> subprocess.CompletedProcess:
    # Use text mode for easier parsing and logging.
    return subprocess.run(
        list(cmd),
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def _git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return _run(["git", *args], check=check)


def _append_kv_file(path: str, key: str, value: str) -> None:
    # GitHub/Gitea Actions use file-based outputs/env injection.
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


def _ensure_before_commit(commit_before: str, commit_after: str) -> str:
    """
    Some push events can provide an empty or all-zero 'before' SHA.
    We try to recover a usable parent commit for diffing/version comparison.
    """
    if not commit_before or commit_before == ZERO_SHA:
        try:
            parent = _git("rev-parse", f"{commit_after}^").stdout.strip()
            if parent:
                return parent
        except subprocess.CalledProcessError:
            pass
    return commit_before


def _git_diff_name_only(commit_before: str, commit_after: str) -> list[str]:
    if not commit_before or not commit_after:
        return []
    try:
        out = _git("diff", "--name-only", commit_before, commit_after).stdout
        return [line.strip() for line in out.splitlines() if line.strip()]
    except subprocess.CalledProcessError as e:
        print("📄 Changed files:")
        print("(diff failed)")
        # Print git output for debugging, but do not fail the job.
        if e.stdout:
            print(e.stdout.strip())
        return []


def _git_show_file(commit: str, path: str) -> Optional[str]:
    if not commit or not path:
        return None
    try:
        # This fails if the file does not exist at that commit.
        return _git("show", f"{commit}:{path}").stdout
    except subprocess.CalledProcessError:
        return None


def _extract_version(text: str, pattern: str) -> str:
    """
    Extract the version using a regex.
    Rules:
    - If the regex has capturing groups, the FIRST group is used.
    - Otherwise, the full match is used.
    """
    rx = re.compile(pattern, flags=re.MULTILINE)
    m = rx.search(text)
    if not m:
        raise ValueError("regex did not match")
    if m.lastindex and m.lastindex >= 1:
        return m.group(1).strip()
    return m.group(0).strip()


def _default_version_regex_for_file(version_file: str) -> str:
    """
    A pragmatic default:
    - For plain 'VERSION' files (one token/line), take the first non-empty line.
    - Still generic enough to handle semver/pre-releases like 1.2.3-pre.1.
    """
    if os.path.basename(version_file) == "VERSION":
        # Capture the first non-empty line (trimmed).
        return r"(?m)^\s*([0-9A-Za-z][0-9A-Za-z.\-+~_]*)\s*$"
    # Generic fallback: look for a token that looks like a version-ish string.
    return r"(?m)^\s*([0-9]+(?:\.[0-9]+){1,3}(?:[-+~.][0-9A-Za-z.\-+~_]*)?)\s*$"


def main() -> int:
    ctx = Ctx(
        git_ref=_get_env("GITHUB_REF", ""),
        commit_before=_get_env("GITHUB_EVENT_BEFORE", ""),
        commit_after=_get_env("GITHUB_SHA", ""),
        allow_non_main_release=_env_bool("ALLOW_NON_MAIN_RELEASE", False),
        version_file=_get_env("VERSION_FILE", "VERSION"),
        version_regex=_get_env("VERSION_REGEX", ""),
    )

    if not ctx.version_regex.strip():
        ctx = Ctx(
            **{**ctx.__dict__, "version_regex": _default_version_regex_for_file(ctx.version_file)}
        )

    print("🔍 Comparing commits:")
    print(f"Before: {ctx.commit_before}")
    print(f"After:  {ctx.commit_after}")
    print(f"Ref:    {ctx.git_ref}")
    print(f"Allow release from non-main branches: {str(ctx.allow_non_main_release).lower()}")
    print(f"Version file: {ctx.version_file}")
    print(f"Version regex: {ctx.version_regex}")

    github_output = _get_env("GITHUB_OUTPUT", "")
    github_env = _get_env("GITHUB_ENV", "")

    # Check branch condition (keep behavior compatible with your Bash snippet).
    if (not ctx.allow_non_main_release) and (ctx.git_ref != "refs/heads/main"):
        print("🚫 Not on 'main' branch and non-main releases are disabled – skipping version check.")
        _append_kv_file(github_env, "VERSION_CHANGED", "false")
        _append_kv_file(github_output, "version_changed", "false")
        return 0

    # Recover a usable "before" commit if needed.
    commit_before = _ensure_before_commit(ctx.commit_before, ctx.commit_after)
    commit_after = ctx.commit_after

    # Show changed files (same intent as your Bash).
    changed_files = _git_diff_name_only(commit_before, commit_after)
    print("📄 Changed files:")
    if changed_files:
        for p in changed_files:
            print(p)
    else:
        print("(none)")

    file_changed = ctx.version_file in changed_files

    # Prefer "semantic" detection: compare extracted versions between commits.
    version_before: Optional[str] = None
    version_after: Optional[str] = None
    semantic_compare_ok = False

    before_text = _git_show_file(commit_before, ctx.version_file) if commit_before else None
    after_text = _git_show_file(commit_after, ctx.version_file) if commit_after else None

    if after_text is not None:
        try:
            version_after = _extract_version(after_text, ctx.version_regex)
        except Exception as e:
            print(f"⚠️ Could not extract version from AFTER commit: {e}")

    if before_text is not None:
        try:
            version_before = _extract_version(before_text, ctx.version_regex)
        except Exception as e:
            print(f"⚠️ Could not extract version from BEFORE commit: {e}")

    if version_before is not None and version_after is not None:
        semantic_compare_ok = True

    if semantic_compare_ok:
        version_changed = (version_before != version_after)
        print(f"🔢 Version before: {version_before}")
        print(f"🔢 Version after:  {version_after}")
        if version_changed:
            print("✅ Version value changed (semantic compare)")
        else:
            print("ℹ️ Version value unchanged (semantic compare)")
    else:
        # Fallback to file-change detection to remain robust in edge cases.
        version_changed = file_changed
        if file_changed:
            print("✅ Version file changed (fallback, semantic compare unavailable)")
        else:
            print("ℹ️ Version file not changed (fallback)")

    # Write outputs/envs (compatible + extra helpful fields).
    _append_kv_file(github_env, "VERSION_CHANGED", "true" if version_changed else "false")
    _append_kv_file(github_output, "version_changed", "true" if version_changed else "false")

    if version_before is not None:
        _append_kv_file(github_env, "VERSION_BEFORE", version_before)
        _append_kv_file(github_output, "version_before", version_before)
    if version_after is not None:
        _append_kv_file(github_env, "VERSION_AFTER", version_after)
        _append_kv_file(github_output, "version_after", version_after)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(130)
