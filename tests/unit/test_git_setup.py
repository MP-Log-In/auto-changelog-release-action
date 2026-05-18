from __future__ import annotations

from auto_changelog_release_action import git_setup


def test_configure_git_author_prefers_explicit_values_over_ci_env(monkeypatch) -> None:
    captured_commands: list[tuple[str, ...]] = []
    state = {
        "user.name": "",
        "user.email": "",
    }

    monkeypatch.setenv(git_setup.CI_AUTHOR_NAME_ENV, "Env Bot")
    monkeypatch.setenv(git_setup.CI_AUTHOR_EMAIL_ENV, "env@example.invalid")

    def fake_run_git_config(*args: str) -> str:
        captured_commands.append(args)
        if args == ("config", "--global", "user.name", "Explicit Bot"):
            state["user.name"] = "Explicit Bot"
            return ""
        if args == ("config", "--global", "user.email", "explicit@example.invalid"):
            state["user.email"] = "explicit@example.invalid"
            return ""
        if args == ("config", "--global", "user.name"):
            return state["user.name"]
        if args == ("config", "--global", "user.email"):
            return state["user.email"]
        raise AssertionError(f"unexpected git config call: {args}")

    monkeypatch.setattr(git_setup, "run_git_config", fake_run_git_config)

    configured = git_setup.configure_git_author("Explicit Bot", "explicit@example.invalid")

    assert configured == ("Explicit Bot", "explicit@example.invalid")
    assert captured_commands[:2] == [
        ("config", "--global", "user.name", "Explicit Bot"),
        ("config", "--global", "user.email", "explicit@example.invalid"),
    ]


def test_configure_git_author_uses_ci_env_when_inputs_are_blank(monkeypatch) -> None:
    monkeypatch.setenv(git_setup.CI_AUTHOR_NAME_ENV, "Env Bot")
    monkeypatch.setenv(git_setup.CI_AUTHOR_EMAIL_ENV, "env@example.invalid")

    resolved = git_setup.resolve_git_author("", "")

    assert resolved == ("Env Bot", "env@example.invalid")


def test_configure_git_author_uses_defaults_when_ci_env_is_missing(monkeypatch) -> None:
    monkeypatch.delenv(git_setup.CI_AUTHOR_NAME_ENV, raising=False)
    monkeypatch.delenv(git_setup.CI_AUTHOR_EMAIL_ENV, raising=False)

    resolved = git_setup.resolve_git_author(None, None)

    assert resolved == (git_setup.DEFAULT_AUTHOR_NAME, git_setup.DEFAULT_AUTHOR_EMAIL)