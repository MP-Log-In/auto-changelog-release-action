#!/usr/bin/env python3
"""
Semantic version bump script based on commit message regex matching.

- Extracts version via regex from a version file
- Supports semver with pre-releases: X.Y.Z-pre.N
- If a pre-release exists, ONLY its counter is incremented
- Otherwise, major/minor/patch bump is applied
- Replaces exactly the regex match (not a blind string replace)
- Exposes whether a bump happened via GITHUB_OUTPUT / GITHUB_ENV
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path
from typing import Iterable, List


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def run_git(args: List[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_commit_messages(revision_range: str) -> List[str]:
    out = run_git(["log", "--format=%B%x00", revision_range])
    return [m.strip() for m in out.split("\x00") if m.strip()]


# ---------------------------------------------------------------------------
# Output helpers (Actions-compatible)
# ---------------------------------------------------------------------------

def append_kv(path: str, key: str, value: str) -> None:
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


# ---------------------------------------------------------------------------
# Pattern handling
# ---------------------------------------------------------------------------

def parse_patterns(raw: str | None) -> List[re.Pattern]:
    if not raw:
        return []
    pats: List[re.Pattern] = []
    for line in raw.splitlines():
        line = line.strip()
        if line:
            pats.append(re.compile(line))
    return pats


def any_match(messages: Iterable[str], patterns: Iterable[re.Pattern]) -> bool:
    return any(p.search(m) for m in messages for p in patterns)


# ---------------------------------------------------------------------------
# Version handling
# ---------------------------------------------------------------------------

PRE_RELEASE_POSTFIXES = {"pre", "alpha", "beta"}

VERSION_RE = re.compile(
    r"""
    ^
    (?P<core>\d+\.\d+\.\d+)
    (?:
        -
        (?P<suffix>(?P<label>[A-Za-z]+)(?:\.(?P<num>\d+))?)
    )?
    $
    """,
    re.VERBOSE,
)


def bump_version(version: str, bump: str) -> str:
    """
    Rules:
    - If a pre-release exists (X.Y.Z-label.N), ONLY increment N
    - Otherwise apply semantic bump to core version
    """
    m = VERSION_RE.match(version)
    if not m:
        raise ValueError(f"Unsupported version format: {version}")

    core = m.group("core")
    suffix = m.group("suffix")
    label = m.group("label")
    num = m.group("num")

    major, minor, patch = map(int, core.split("."))

    if label and num and label in PRE_RELEASE_POSTFIXES:
        return f"{core}-{label}.{int(num) + 1}"

    if bump == "major":
        bumped_core = f"{major + 1}.0.0"
    elif bump == "minor":
        bumped_core = f"{major}.{minor + 1}.0"
    elif bump == "patch":
        bumped_core = f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(bump)

    if suffix:
        return f"{bumped_core}-{suffix}"
    return bumped_core


def replace_version(text: str, regex: str, new_version: str) -> str:
    rx = re.compile(regex, flags=re.MULTILINE)

    def _repl(m: re.Match) -> str:
        if m.lastindex:
            return m.group(0).replace(m.group(1), new_version, 1)
        return new_version

    new_text, count = rx.subn(_repl, text, count=1)
    if count != 1:
        raise RuntimeError("Version regex did not match exactly once")

    return new_text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    version_file = os.environ["VERSION_FILE"]
    version_regex = os.environ["VERSION_REGEX"]

    major_raw = os.environ.get("MAJOR_PATTERNS", "")
    minor_raw = os.environ.get("MINOR_PATTERNS", "")
    patch_raw = os.environ.get("PATCH_PATTERNS", "")

    revision_range = os.environ["RANGE"]
    
    allow_non_main_release=os.environ.get("ALLOW_NON_MAIN_RELEASE", "false").lower() == "true"
    
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    github_env = os.environ.get("GITHUB_ENV", "")
    
    # Check branch condition (keep behavior compatible with your Bash snippet).
    if (not allow_non_main_release) and (os.environ.get("GITHUB_REF", "") != "refs/heads/main"):
        print("🚫 Not on 'main' branch and non-main releases are disabled – skipping version check.")
        append_kv(github_output, "version_bumped", "false")
        append_kv(github_env, "VERSION_BUMPED", "false")
        return

    messages = get_commit_messages(revision_range)
    if not messages:
        append_kv(github_output, "version_bumped", "false")
        append_kv(github_env, "VERSION_BUMPED", "false")
        return

    major_p = parse_patterns(major_raw)
    minor_p = parse_patterns(minor_raw)
    patch_p = parse_patterns(patch_raw)

    bump: str | None = None
    if major_p and any_match(messages, major_p):
        bump = "major"
    elif minor_p and any_match(messages, minor_p):
        bump = "minor"
    elif patch_p and any_match(messages, patch_p):
        bump = "patch"

    if bump is None:
        append_kv(github_output, "version_bumped", "false")
        append_kv(github_env, "VERSION_BUMPED", "false")
        return

    path = Path(version_file)
    content = path.read_text(encoding="utf-8")

    m = re.search(version_regex, content, flags=re.MULTILINE)
    if not m:
        raise RuntimeError("Version regex did not match")

    old_version = m.group(1) if m.lastindex else m.group(0)
    new_version = bump_version(old_version, bump)

    if old_version == new_version:
        append_kv(github_output, "version_bumped", "false")
        append_kv(github_env, "VERSION_BUMPED", "false")
        return

    new_content = replace_version(content, version_regex, new_version)
    path.write_text(new_content, encoding="utf-8")

    run_git(["add", str(path)])
    run_git([
        "commit",
        "-m", f"chore(version): bump version to {new_version}",
        "-m", "Automated version bump based on commit message patterns."
    ])

    append_kv(github_output, "version_bumped", "true")
    append_kv(github_env, "VERSION_BUMPED", "true")
    
    append_kv(github_output, "version_after", new_version)
    append_kv(github_env, "VERSION_AFTER", new_version)

    print(f"Version bumped: {old_version} → {new_version}")


if __name__ == "__main__":
    main()
