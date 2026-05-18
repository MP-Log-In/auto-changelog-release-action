from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action.unreleased_changelog import (
    branch_name_from_ref,
    should_generate_unreleased_changelog,
)


def test_branch_name_from_ref_strips_heads_prefix() -> None:
    assert branch_name_from_ref("refs/heads/v1/main") == "v1/main"
    assert branch_name_from_ref("main") == "main"


def test_should_generate_when_changelog_exists(tmp_path: Path) -> None:
    changelog_file = tmp_path / "CHANGELOG.md"
    changelog_file.write_text("existing\n", encoding="utf-8")

    assert should_generate_unreleased_changelog(changelog_file, "feature/demo") is True


def test_should_generate_on_main_even_without_existing_file(tmp_path: Path) -> None:
    changelog_file = tmp_path / "CHANGELOG.md"

    assert should_generate_unreleased_changelog(changelog_file, "main") is True
    assert should_generate_unreleased_changelog(changelog_file, "feature/demo") is False
