from __future__ import annotations

from auto_changelog_release_action import __main__ as package_main


def test_main_invokes_action_runtime(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_config_from_environment() -> object:
        captured["config_loaded"] = True
        return object()

    def fake_run_action_runtime(config: object) -> None:
        captured["config"] = config

    monkeypatch.setattr(package_main.action_runtime, "config_from_environment", fake_config_from_environment)
    monkeypatch.setattr(package_main.action_runtime, "run_action_runtime", fake_run_action_runtime)

    result = package_main.main()

    assert result == 0
    assert captured["config_loaded"] is True
    assert captured["config"] is not None