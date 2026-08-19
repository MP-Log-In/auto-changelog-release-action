from __future__ import annotations

from pathlib import Path

from auto_changelog_release_action import install_git_cliff as installer


def test_install_git_cliff_uses_existing_binary_without_fetching(
    tmp_path: Path,
    monkeypatch,
) -> None:
    binary_path = tmp_path / "git-cliff"
    binary_path.write_text(
        "#!/bin/sh\nprintf '%s\\n' 'git-cliff 2.10.1'\n",
        encoding="utf-8",
    )
    binary_path.chmod(0o755)
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setattr(
        installer,
        "fetch_release_info",
        lambda _version: (_ for _ in ()).throw(AssertionError("GitHub must not be queried")),
    )

    result = installer.install_git_cliff("2.10.1")

    assert result == "2.10.1"
