from __future__ import annotations

import pytest

from auto_changelog_release_action.versioning import (
    PRE_RELEASE_LABELS,
    bump_version,
    default_version_regex_for_file,
    detect_bump,
    extract_version,
    parse_patterns,
    parse_version,
    replace_version,
)


def test_parse_version_supports_configured_prerelease() -> None:
    parsed = parse_version("1.2.3-pre.4")

    assert parsed.core == "1.2.3"
    assert parsed.label == "pre"
    assert parsed.tail == "4"
    assert parsed.is_configured_prerelease is True


def test_parse_version_preserves_non_configured_suffix() -> None:
    parsed = parse_version("1.2.3-miktex.26.2")

    assert parsed.suffix == "miktex.26.2"
    assert parsed.label == "miktex"
    assert parsed.is_configured_prerelease is False


def test_parse_version_supports_hyphenated_non_prerelease_suffix() -> None:
    parsed = parse_version("0.1.6-gitea-runner.1.0.4-dev-4-9-g2208e7e")

    assert parsed.core == "0.1.6"
    assert parsed.suffix == "gitea-runner.1.0.4-dev-4-9-g2208e7e"
    assert parsed.label == "gitea-runner"
    assert parsed.tail == "1.0.4-dev-4-9-g2208e7e"
    assert parsed.is_configured_prerelease is False


@pytest.mark.parametrize(
    ("current_version", "bump", "expected"),
    [
        ("1.2.3", "major", "2.0.0"),
        ("1.2.3", "minor", "1.3.0"),
        ("1.2.3", "patch", "1.2.4"),
        ("1.2.3-pre.4", "patch", "1.2.3-pre.5"),
        ("1.2.3-alpha.9", "minor", "1.2.3-alpha.10"),
        ("1.2.3-miktex.26.2", "minor", "1.3.0-miktex.26.2"),
        (
            "0.1.6-gitea-runner.1.0.4-dev-4-9-g2208e7e",
            "patch",
            "0.1.7-gitea-runner.1.0.4-dev-4-9-g2208e7e",
        ),
    ],
)
def test_bump_version_matches_current_rules(
    current_version: str,
    bump: str,
    expected: str,
) -> None:
    assert bump_version(current_version, bump) == expected


def test_extract_version_uses_first_capture_group_when_present() -> None:
    version = extract_version('version = "1.9.1"\n', r'version\s*=\s*"([^"]+)"')

    assert version == "1.9.1"


def test_extract_version_uses_full_match_without_capture_group() -> None:
    version = extract_version("1.9.1\n", r"^(.*)$")

    assert version == "1.9.1"


def test_replace_version_replaces_only_the_first_match() -> None:
    updated = replace_version(
        'version = "1.9.1"\nsecondary = "1.9.1"\n',
        r'version\s*=\s*"([^"]+)"',
        "2.0.0",
    )

    assert updated == 'version = "2.0.0"\nsecondary = "1.9.1"\n'


def test_default_version_regex_for_version_file_matches_current_behavior() -> None:
    regex = default_version_regex_for_file("VERSION")

    assert extract_version("1.9.1\n", regex) == "1.9.1"


def test_detect_bump_prioritizes_major_over_minor_and_patch() -> None:
    messages = [
        "feat: add feature\n\nBREAKING CHANGE: schema updated",
        "fix: patch issue",
    ]

    bump = detect_bump(
        messages,
        major_patterns=parse_patterns(r"BREAKING CHANGE"),
        minor_patterns=parse_patterns(r"^feat:"),
        patch_patterns=parse_patterns(r"^fix:"),
    )

    assert bump == "major"


def test_parse_patterns_ignores_blank_lines() -> None:
    patterns = parse_patterns("\n^feat\n\n^fix\n")

    assert len(patterns) == 2
    assert PRE_RELEASE_LABELS == frozenset({"pre", "alpha", "beta"})
