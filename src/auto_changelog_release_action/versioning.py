"""Shared parsing and rewrite helpers for semantic version strings and bump patterns."""

from __future__ import annotations

import os
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from re import Pattern
from typing import Literal

VersionBump = Literal["major", "minor", "patch"]

PRE_RELEASE_LABELS = frozenset({"pre", "alpha", "beta"})

VERSION_PATTERN = re.compile(
    r"""
    ^
    (?P<core>\d+\.\d+\.\d+)
    (?:
        -
        (?P<suffix>(?P<label>[A-Za-z][0-9A-Za-z-]*)(?:\.(?P<tail>[0-9A-Za-z][0-9A-Za-z.-]*))?)
    )?
    $
    """,
    re.VERBOSE,
)


@dataclass(frozen=True)
class ParsedVersion:
    """Structured representation of a supported version string."""

    core: str
    major: int
    minor: int
    patch: int
    suffix: str | None
    label: str | None
    tail: str | None

    @property
    def is_configured_prerelease(self) -> bool:
        """Return whether the suffix is a numbered prerelease label we manage."""

        return bool(
            self.label and self.label in PRE_RELEASE_LABELS and self.tail and self.tail.isdigit()
        )


def parse_patterns(raw: str | None) -> list[Pattern[str]]:
    """Compile newline-separated regex patterns and ignore blank lines."""

    if not raw:
        return []

    patterns: list[Pattern[str]] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped:
            patterns.append(re.compile(stripped))
    return patterns


def matches_any(messages: Iterable[str], patterns: Iterable[Pattern[str]]) -> bool:
    """Return whether any pattern matches any commit message."""

    return any(pattern.search(message) for message in messages for pattern in patterns)


def detect_bump(
    messages: Sequence[str],
    *,
    major_patterns: Sequence[Pattern[str]],
    minor_patterns: Sequence[Pattern[str]],
    patch_patterns: Sequence[Pattern[str]],
) -> VersionBump | None:
    """Choose the highest configured bump triggered by the given messages."""

    if major_patterns and matches_any(messages, major_patterns):
        return "major"
    if minor_patterns and matches_any(messages, minor_patterns):
        return "minor"
    if patch_patterns and matches_any(messages, patch_patterns):
        return "patch"
    return None


def parse_version(version: str) -> ParsedVersion:
    """Parse a semantic version with an optional preserved suffix."""

    match = VERSION_PATTERN.match(version)
    if not match:
        raise ValueError(f"Unsupported version format: {version}")

    core = match.group("core")
    major, minor, patch = (int(part) for part in core.split("."))
    return ParsedVersion(
        core=core,
        major=major,
        minor=minor,
        patch=patch,
        suffix=match.group("suffix"),
        label=match.group("label"),
        tail=match.group("tail"),
    )


def bump_version(version: str, bump: VersionBump) -> str:
    """Apply a semantic bump while preserving supported suffix semantics."""

    parsed = parse_version(version)

    if parsed.is_configured_prerelease:
        label = parsed.label
        tail = parsed.tail
        if label is None or tail is None:
            raise AssertionError("configured prerelease requires label and tail")
        return f"{parsed.core}-{label}.{int(tail) + 1}"

    if bump == "major":
        bumped_core = f"{parsed.major + 1}.0.0"
    elif bump == "minor":
        bumped_core = f"{parsed.major}.{parsed.minor + 1}.0"
    else:
        bumped_core = f"{parsed.major}.{parsed.minor}.{parsed.patch + 1}"

    if parsed.suffix:
        return f"{bumped_core}-{parsed.suffix}"
    return bumped_core


def extract_version(text: str, pattern: str) -> str:
    """Extract the version value selected by the configured regex."""

    regex = re.compile(pattern, flags=re.MULTILINE)
    match = regex.search(text)
    if not match:
        raise ValueError("regex did not match")

    if match.lastindex and match.lastindex >= 1:
        return match.group(1).strip()
    return match.group(0).strip()


def replace_version(text: str, pattern: str, new_version: str) -> str:
    """Replace the first configured version match in a text block."""

    regex = re.compile(pattern, flags=re.MULTILINE)

    def replacement(match: re.Match[str]) -> str:
        if match.lastindex:
            return match.group(0).replace(match.group(1), new_version, 1)
        return new_version

    new_text, count = regex.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("Version regex did not match exactly once")
    return new_text


def default_version_regex_for_file(version_file: str) -> str:
    """Return the default extraction regex for a known version file name."""

    if os.path.basename(version_file) == "VERSION":
        return r"(?m)^\s*([0-9A-Za-z][0-9A-Za-z.\-+~_]*)\s*$"
    return r"(?m)^\s*([0-9]+(?:\.[0-9]+){1,3}(?:[-+~.][0-9A-Za-z.\-+~_]*)?)\s*$"
