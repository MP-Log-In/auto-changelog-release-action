from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action import action_runtime
from auto_changelog_release_action.version_bump_flow import VersionBumpResult
from auto_changelog_release_action.version_change_flow import VersionChangeResult
from auto_changelog_release_action.versioning import default_version_regex_for_file


def test_run_action_runtime_uses_api_url_for_release_requests(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    config = action_runtime.ActionRuntimeConfig(
        action_path=tmp_path,
        github_output="",
        github_env="",
        author_name="CI Bot",
        author_email="ci@example.invalid",
        allow_non_main_release=False,
        version_file="VERSION",
        version_regex="^(.*)$",
        major_patterns="",
        minor_patterns="",
        patch_patterns="",
        revision_range="before..after",
        github_event_before="before",
        github_sha="after",
        github_ref="refs/heads/main",
        github_api_url="https://api.example.invalid",
        github_server_url="https://example.invalid",
        github_repository="owner/repo",
        release_publish_token="token",
        actions_runtime_token="",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(action_runtime, "configure_git_author", lambda *_args: None)
    monkeypatch.setattr(
        action_runtime,
        "run_version_bump",
        lambda _config: VersionBumpResult(version_bumped=False),
    )
    monkeypatch.setattr(
        action_runtime,
        "run_version_change_detection",
        lambda _config: VersionChangeResult(
            version_changed=True,
            version_before="0.0.1",
            version_after="0.0.2",
        ),
    )
    monkeypatch.setattr(
        action_runtime, "write_version_bump_outputs", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        action_runtime,
        "write_version_change_outputs",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(action_runtime, "ensure_cliff_config", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        action_runtime, "install_git_cliff", lambda *_args, **_kwargs: "git-cliff 2.10.1"
    )

    def fake_run_release_flow(release_config, *, cwd: Path) -> None:
        captured["api_url"] = release_config.api_url
        captured["cwd"] = cwd

    monkeypatch.setattr(action_runtime, "run_release_flow", fake_run_release_flow)
    monkeypatch.setattr(
        action_runtime,
        "run_unreleased_changelog_flow",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("unexpected path")),
    )

    action_runtime.run_action_runtime(config)

    assert captured == {
        "api_url": "https://api.example.invalid",
        "cwd": tmp_path,
    }


def test_run_action_runtime_uses_default_version_regex_when_input_is_blank(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    config = action_runtime.ActionRuntimeConfig(
        action_path=tmp_path,
        github_output="",
        github_env="",
        author_name="CI Bot",
        author_email="ci@example.invalid",
        allow_non_main_release=False,
        version_file="VERSION",
        version_regex="",
        major_patterns="",
        minor_patterns="",
        patch_patterns="",
        revision_range="before..after",
        github_event_before="before",
        github_sha="after",
        github_ref="refs/heads/main",
        github_api_url="",
        github_server_url="https://example.invalid",
        github_repository="owner/repo",
        release_publish_token="",
        actions_runtime_token="",
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(action_runtime, "configure_git_author", lambda *_args: None)

    def fake_run_version_bump(bump_config):
        captured["bump_version_regex"] = bump_config.version_regex
        return VersionBumpResult(version_bumped=False)

    def fake_run_version_change_detection(change_config):
        captured["change_version_regex"] = change_config.version_regex
        return VersionChangeResult(version_changed=False)

    monkeypatch.setattr(action_runtime, "run_version_bump", fake_run_version_bump)
    monkeypatch.setattr(
        action_runtime,
        "run_version_change_detection",
        fake_run_version_change_detection,
    )
    monkeypatch.setattr(
        action_runtime, "write_version_bump_outputs", lambda *_args, **_kwargs: None
    )
    monkeypatch.setattr(
        action_runtime,
        "write_version_change_outputs",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(action_runtime, "ensure_cliff_config", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(
        action_runtime, "install_git_cliff", lambda *_args, **_kwargs: "git-cliff 2.10.1"
    )
    monkeypatch.setattr(
        action_runtime,
        "run_unreleased_changelog_flow",
        lambda *_args, **_kwargs: None,
    )

    action_runtime.run_action_runtime(config)

    expected_regex = default_version_regex_for_file("VERSION")
    assert captured == {
        "bump_version_regex": expected_regex,
        "change_version_regex": expected_regex,
    }
