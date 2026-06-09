from __future__ import annotations

import subprocess
from pathlib import Path

from auto_changelog_release_action import __main__ as package_main
from auto_changelog_release_action import action_runtime
from auto_changelog_release_action.runtime_host import RuntimeHost


def make_config(tmp_path: Path, *, host: RuntimeHost) -> action_runtime.ActionRuntimeConfig:
    return action_runtime.ActionRuntimeConfig(
        action_path=tmp_path,
        host=host,
        api_url="https://api.github.com",
        server_url="https://github.com",
        repository="owner/repo",
        git_ref="refs/heads/main",
        github_output="",
        github_env="",
        author_name="",
        author_email="",
        allow_non_main_release=False,
        version_file="VERSION",
        version_regex="^(.*)$",
        major_patterns="",
        minor_patterns="",
        patch_patterns="",
        revision_range="before..after",
        github_event_before="",
        github_sha="",
        release_publish_token="",
    )


def test_main_invokes_action_runtime(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}
    config = make_config(tmp_path, host=RuntimeHost.GITEA)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.poetry]\nversion = "1.10.0"\n',
        encoding="utf-8",
    )

    def fake_config_from_environment() -> action_runtime.ActionRuntimeConfig:
        captured["config_loaded"] = True
        return config

    def fake_run_action_runtime(config: object) -> None:
        captured["config"] = config

    monkeypatch.setattr(
        package_main.action_runtime, "config_from_environment", fake_config_from_environment
    )
    monkeypatch.setattr(package_main.action_runtime, "run_action_runtime", fake_run_action_runtime)

    result = package_main.main()

    assert result == 0
    assert captured["config_loaded"] is True
    assert captured["config"] is not None


def test_main_logs_action_version_and_detected_host(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    config = make_config(
        tmp_path,
        host=RuntimeHost.GITHUB,
    )
    (tmp_path / "VERSION").write_text("9.9.9\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text(
        '[tool.poetry]\nversion = "1.10.0"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(package_main.action_runtime, "config_from_environment", lambda: config)
    monkeypatch.setattr(package_main.action_runtime, "run_action_runtime", lambda _config: None)

    result = package_main.main()

    captured = capsys.readouterr()
    assert result == 0
    assert captured.out.splitlines()[:2] == [
        "Action version: 1.10.0",
        "Detected runtime host: GitHub",
    ]


def test_main_logs_unknown_version_when_pyproject_version_is_missing(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    config = make_config(tmp_path, host=RuntimeHost.GITEA)
    (tmp_path / "pyproject.toml").write_text('[tool.poetry]\nname = "demo"\n', encoding="utf-8")

    monkeypatch.setattr(package_main.action_runtime, "config_from_environment", lambda: config)
    monkeypatch.setattr(package_main.action_runtime, "run_action_runtime", lambda _config: None)

    package_main.main()

    captured = capsys.readouterr()
    assert captured.out.splitlines()[:2] == [
        "Action version: unknown",
        "Detected runtime host: Gitea",
    ]


def test_main_returns_non_zero_for_external_command_failures(
    monkeypatch,
    tmp_path: Path,
    capsys,
) -> None:
    config = make_config(tmp_path, host=RuntimeHost.GITHUB)
    (tmp_path / "pyproject.toml").write_text(
        '[tool.poetry]\nversion = "1.10.0"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(package_main.action_runtime, "config_from_environment", lambda: config)

    def fail(_config) -> None:
        raise subprocess.CalledProcessError(
            128,
            ["git", "fetch", "--tags"],
            stderr="fatal: could not read from remote repository\n",
        )

    monkeypatch.setattr(package_main.action_runtime, "run_action_runtime", fail)

    result = package_main.main()

    captured = capsys.readouterr()
    assert result == 1
    assert "CalledProcessError" not in captured.err
    assert "returned non-zero exit status 128" in captured.err
