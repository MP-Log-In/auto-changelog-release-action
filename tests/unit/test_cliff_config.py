from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action.cliff_config import (
    DEFAULT_GITEA_SERVER_URL,
    ensure_cliff_config,
    extract_cliff_version,
    render_cliff_config_template,
    split_repository_slug,
)


def test_extract_cliff_version_reads_comment_value() -> None:
    text = '# CLIFF_VERSION=2.10.1\n[remote.gitea]\nowner = "actions"\n'

    assert extract_cliff_version(text) == "2.10.1"


def test_extract_cliff_version_returns_none_when_comment_missing() -> None:
    assert extract_cliff_version('[remote.gitea]\nowner = "actions"\n') is None


def test_split_repository_slug_matches_shell_behavior() -> None:
    assert split_repository_slug("actions/auto-changelog-release-action") == (
        "actions",
        "auto-changelog-release-action",
    )
    assert split_repository_slug("") == ("", "")
    assert split_repository_slug("standalone") == ("standalone", "standalone")


def test_render_cliff_config_template_replaces_all_placeholders() -> None:
    rendered = render_cliff_config_template(
        'owner = "%OWNER%"\nrepo = "%REPO%"\nurl = "%GITEA_SERVER_URL%"\n',
        repository="actions/auto-changelog-release-action",
        server_url=DEFAULT_GITEA_SERVER_URL,
    )

    assert "%OWNER%" not in rendered
    assert "%REPO%" not in rendered
    assert "%GITEA_SERVER_URL%" not in rendered
    assert 'owner = "actions"' in rendered
    assert 'repo = "auto-changelog-release-action"' in rendered
    assert f'url = "{DEFAULT_GITEA_SERVER_URL}"' in rendered


def test_ensure_cliff_config_writes_rendered_template_when_missing(tmp_path: Path) -> None:
    template_path = tmp_path / "cliff.toml.template"
    template_path.write_text(
        'owner = "%OWNER%"\nrepo = "%REPO%"\nurl = "%GITEA_SERVER_URL%"\n',
        encoding="utf-8",
    )
    cliff_path = tmp_path / "cliff.toml"

    created = ensure_cliff_config(
        cliff_path,
        template_path=template_path,
        repository="actions/auto-changelog-release-action",
        server_url="https://git.example.invalid",
    )

    assert created is True
    assert cliff_path.read_text(encoding="utf-8") == (
        'owner = "actions"\n'
        'repo = "auto-changelog-release-action"\n'
        'url = "https://git.example.invalid"\n'
    )


def test_ensure_cliff_config_preserves_existing_file(tmp_path: Path) -> None:
    template_path = tmp_path / "cliff.toml.template"
    template_path.write_text("ignored", encoding="utf-8")
    cliff_path = tmp_path / "cliff.toml"
    cliff_path.write_text("existing", encoding="utf-8")

    created = ensure_cliff_config(
        cliff_path,
        template_path=template_path,
        repository="actions/auto-changelog-release-action",
        server_url=DEFAULT_GITEA_SERVER_URL,
    )

    assert created is False
    assert cliff_path.read_text(encoding="utf-8") == "existing"
