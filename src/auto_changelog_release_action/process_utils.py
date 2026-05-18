"""Shared subprocess wrappers for git and CLI commands used by the action."""

from __future__ import annotations

import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path


def run_command(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
    check: bool = True,
    merge_stderr: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command and capture text output with the action defaults."""

    return subprocess.run(
        list(args),
        cwd=cwd,
        env=dict(env) if env is not None else None,
        input=input_text,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT if merge_stderr else subprocess.PIPE,
    )


def run_command_stdout(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
    check: bool = True,
    merge_stderr: bool = False,
) -> str:
    """Run a command and return stripped stdout."""

    return run_command(
        args,
        cwd=cwd,
        env=env,
        input_text=input_text,
        check=check,
        merge_stderr=merge_stderr,
    ).stdout.strip()


def run_git(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    merge_stderr: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a git command with the shared subprocess settings."""

    return run_command(
        ["git", *args],
        cwd=cwd,
        env=env,
        check=check,
        merge_stderr=merge_stderr,
    )


def run_git_stdout(
    args: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    merge_stderr: bool = False,
) -> str:
    """Run a git command and return stripped stdout."""

    return run_git(
        args,
        cwd=cwd,
        env=env,
        check=check,
        merge_stderr=merge_stderr,
    ).stdout.strip()
