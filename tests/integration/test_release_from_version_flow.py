from __future__ import annotations

import io
import json
import os
import stat
import subprocess
import textwrap
import threading
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from auto_changelog_release_action.release_flow import ReleaseConfig, run_release_flow
from tests.support.git_repo import init_local_bare_remote, init_local_git_repo


def write_fake_git_cliff(bin_dir: Path) -> None:
    script_path = bin_dir / "git-cliff"
    script_path.write_text(
        textwrap.dedent(
            """
            #!/usr/bin/env bash
            set -euo pipefail

            if printf '%s\n' "$@" | grep -qx -- '--context'; then
                printf '%s' '[{"version": null, "commits": []}]'
                exit 0
            fi

            if printf '%s\n' "$@" | grep -qx -- '--from-context'; then
                output_path=''
                while [[ $# -gt 0 ]]; do
                    if [[ "$1" == '-o' ]]; then
                        output_path="$2"
                        shift 2
                        continue
                    fi
                    shift
                done

                cat >/dev/null
                printf '%s' "${FAKE_GIT_CLIFF_OUTPUT:-# Changelog\n}" >"${output_path}"
                exit 0
            fi

            echo "unexpected args: $*" >&2
            exit 1
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)


class ReleaseRequestRecorder:
    def __init__(self, status_code: int = 201) -> None:
        self.status_code = status_code
        self.requests: list[dict[str, object]] = []
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._build_handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def _build_handler(self):
        recorder = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length).decode("utf-8")
                recorder.requests.append(
                    {
                        "path": self.path,
                        "headers": dict(self.headers.items()),
                        "body": json.loads(body),
                    }
                )
                self.send_response(recorder.status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"ok": true}')

            def log_message(self, format: str, *args: object) -> None:  # noqa: A003
                return

        return Handler

    @property
    def api_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> ReleaseRequestRecorder:
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


def run_release_from_version(
    repo_root: Path,
    *,
    version_after: str,
    api_url: str,
    fake_output: str,
    github_ref: str = "refs/heads/main",
) -> str:
    action_root = Path(__file__).resolve().parents[2]
    bin_dir = repo_root.parent / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    write_fake_git_cliff(bin_dir)

    original_path = os.environ.get("PATH", "")
    original_output = os.environ.get("FAKE_GIT_CLIFF_OUTPUT")
    os.environ["PATH"] = f"{bin_dir}:{original_path}"
    os.environ["FAKE_GIT_CLIFF_OUTPUT"] = fake_output

    config = ReleaseConfig(
        changelog_file=repo_root / "CHANGELOG.md",
        cliff_config=repo_root / "cliff.toml",
        version=version_after,
        git_branch=github_ref.removeprefix("refs/heads/"),
        api_url=api_url,
        repository_owner="actions",
        repository_name="auto-changelog-release-action",
        publish_token="test-token",
        using_runtime_token=False,
    )

    buffer = io.StringIO()
    try:
        with redirect_stdout(buffer):
            run_release_flow(config, cwd=repo_root)
    finally:
        os.environ["PATH"] = original_path
        if original_output is None:
            os.environ.pop("FAKE_GIT_CLIFF_OUTPUT", None)
        else:
            os.environ["FAKE_GIT_CLIFF_OUTPUT"] = original_output

    return buffer.getvalue()


def remote_branch_head(remote_root: Path, branch: str) -> str:
    completed = subprocess.run(
        ["git", "--git-dir", str(remote_root), "rev-parse", f"refs/heads/{branch}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def remote_tag_exists(remote_root: Path, tag_name: str) -> bool:
    completed = subprocess.run(
        ["git", "--git-dir", str(remote_root), "show-ref", "--tags", tag_name],
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def test_release_from_version_generates_tags_pushes_and_publishes(tmp_path: Path) -> None:
    repo = init_local_git_repo(tmp_path)
    remote_root = init_local_bare_remote(tmp_path)
    repo.add_remote("origin", str(remote_root))
    repo.write("cliff.toml", "test\n")
    repo.commit_all("chore: initial import")
    repo.push("origin", "main", set_upstream=True)

    changelog_output = (
        "# Changelog\n\n"
        "## [1.2.3] (https://example.invalid/compare/v1.2.2..v1.2.3) - 2026-05-10\n"
        "- Added feature\n\n"
        "## [1.2.2] - 2026-05-01\n"
        "- Previous release\n"
    )

    with ReleaseRequestRecorder() as recorder:
        stdout = run_release_from_version(
            repo.root,
            version_after="1.2.3",
            api_url=recorder.api_url,
            fake_output=changelog_output,
        )

    assert "Workflow finished successfully" in stdout
    assert repo.read("CHANGELOG.md") == changelog_output
    assert repo.head_subject() == "chore(changelog): update changelog for v1.2.3"
    assert (
        repo.run("for-each-ref", "refs/tags/v1.2.3", "--format=%(subject)")
        == "[1.2.3] - 2026-05-10 - Added feature"
    )
    assert remote_branch_head(remote_root, "main") == repo.rev_parse("HEAD")
    assert remote_tag_exists(remote_root, "v1.2.3") is True
    assert len(recorder.requests) == 1
    payload = recorder.requests[0]["body"]
    assert recorder.requests[0]["path"] == "/repos/actions/auto-changelog-release-action/releases"
    assert payload == {
        "tag_name": "v1.2.3",
        "target_commitish": "main",
        "name": "Release v1.2.3",
        "body": "- Added feature\n\n",
        "draft": False,
        "prerelease": False,
    }


def test_release_from_version_marks_configured_prereleases(tmp_path: Path) -> None:
    repo = init_local_git_repo(tmp_path)
    remote_root = init_local_bare_remote(tmp_path)
    repo.add_remote("origin", str(remote_root))
    repo.write("cliff.toml", "test\n")
    repo.commit_all("chore: initial import")
    repo.push("origin", "main", set_upstream=True)

    changelog_output = (
        "# Changelog\n\n## [1.2.3-pre.1] (pre-release) - 2026-05-10\n- Preview feature\n"
    )

    with ReleaseRequestRecorder() as recorder:
        stdout = run_release_from_version(
            repo.root,
            version_after="1.2.3-pre.1",
            api_url=recorder.api_url,
            fake_output=changelog_output,
        )

    assert "Detected configured pre-release label" in stdout
    payload = recorder.requests[0]["body"]
    assert payload["tag_name"] == "v1.2.3-pre.1"
    assert payload["prerelease"] is True
