from __future__ import annotations

import subprocess

import pytest

from auto_changelog_release_action.process_utils import run_command


def test_run_command_logs_stdout_and_stderr_for_failed_process(capsys) -> None:
    with pytest.raises(subprocess.CalledProcessError):
        run_command(
            [
                "python3",
                "-c",
                "import sys; print('out'); print('err', file=sys.stderr); sys.exit(7)",
            ],
        )

    captured = capsys.readouterr()
    assert "External command failed: python3 -c" in captured.err
    assert "Exit code: 7" in captured.err
    assert "--- stdout ---" in captured.err
    assert "out" in captured.err
    assert "--- stderr ---" in captured.err
    assert "err" in captured.err


def test_run_command_logs_missing_executable(capsys) -> None:
    with pytest.raises(FileNotFoundError):
        run_command(["this-command-should-not-exist-12345"])

    captured = capsys.readouterr()
    assert "External command failed: this-command-should-not-exist-12345" in captured.err
    assert "No such file or directory" in captured.err
