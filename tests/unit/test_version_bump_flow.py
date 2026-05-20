from __future__ import annotations

import subprocess

from auto_changelog_release_action import version_bump_flow


def test_get_commit_messages_recovers_from_zero_before_sha(monkeypatch) -> None:
    captured: list[list[str]] = []

    def fake_run_git(args: list[str]) -> str:
        captured.append(args)
        if args == ["rev-parse", "after^"]:
            return "parent"
        if args == ["log", "--format=%B%x00", "parent..after"]:
            return "feat: ship it\x00"
        raise AssertionError(args)

    monkeypatch.setattr(version_bump_flow, "run_git", fake_run_git)

    messages = version_bump_flow.get_commit_messages(f"{version_bump_flow.ZERO_SHA}..after")

    assert messages == ["feat: ship it"]
    assert captured == [
        ["rev-parse", "after^"],
        ["log", "--format=%B%x00", "parent..after"],
    ]


def test_get_commit_messages_falls_back_to_after_commit_when_parent_is_missing(
    monkeypatch,
) -> None:
    captured: list[list[str]] = []

    def fake_run_git(args: list[str]) -> str:
        captured.append(args)
        if args == ["rev-parse", "after^"]:
            raise subprocess.CalledProcessError(128, ["git", *args])
        if args == ["log", "--format=%B%x00", "after"]:
            return "feat: initial commit\x00"
        raise AssertionError(args)

    monkeypatch.setattr(version_bump_flow, "run_git", fake_run_git)

    messages = version_bump_flow.get_commit_messages(f"{version_bump_flow.ZERO_SHA}..after")

    assert messages == ["feat: initial commit"]
    assert captured == [
        ["rev-parse", "after^"],
        ["log", "--format=%B%x00", "after"],
    ]
