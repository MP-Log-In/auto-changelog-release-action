from __future__ import annotations

from auto_changelog_release_action.release_flow import (
    extract_release_notes,
    is_configured_prerelease_version,
    release_api_body,
)


def test_extract_release_notes_matches_current_heading_behavior() -> None:
    changelog_text = (
        "# Changelog\n\n"
        "## [1.2.3] (https://example.invalid/compare/v1.2.2..v1.2.3) - 2026-05-10\n"
        "- Added feature\n\n"
        "## [1.2.2] - 2026-05-01\n"
        "- Previous release\n"
    )

    notes = extract_release_notes(changelog_text, "1.2.3")

    assert notes == "[1.2.3] - 2026-05-10\n- Added feature\n\n"


def test_release_api_body_skips_heading_line() -> None:
    notes = "[1.2.3]\n- Added feature\n\n"

    assert release_api_body(notes) == "- Added feature\n\n"


def test_is_configured_prerelease_version_uses_allowed_labels_only() -> None:
    assert is_configured_prerelease_version("1.2.3-pre.1") is True
    assert is_configured_prerelease_version("1.2.3-alpha.2") is True
    assert is_configured_prerelease_version("1.2.3-beta") is True
    assert is_configured_prerelease_version("1.2.3-miktex.26.2") is False
    assert is_configured_prerelease_version("1.2.3") is False
