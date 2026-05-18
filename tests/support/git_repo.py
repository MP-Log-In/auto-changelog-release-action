from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class LocalGitRepo:
    root: Path

    def run(self, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return completed.stdout.strip()

    def write(self, relative_path: str, content: str) -> Path:
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def commit_all(self, subject: str, body: str | None = None) -> str:
        self.run("add", ".")
        command = ["commit", "-m", subject]
        if body:
            command.extend(["-m", body])
        self.run(*command)
        return self.rev_parse("HEAD")

    def checkout(self, ref_name: str, *, create: bool = False) -> None:
        if create:
            self.run("checkout", "-b", ref_name)
            return
        self.run("checkout", ref_name)

    def add_remote(self, name: str, url: str) -> None:
        self.run("remote", "add", name, url)

    def push(self, remote: str, *refs: str, set_upstream: bool = False) -> None:
        command = ["push"]
        if set_upstream:
            command.append("-u")
        command.extend([remote, *refs])
        self.run(*command)

    def head_subject(self) -> str:
        return self.run("log", "-1", "--pretty=%s")

    def tag(self, name: str, message: str | None = None) -> None:
        if message:
            self.run("tag", "-a", name, "-m", message)
            return
        self.run("tag", name)

    def rev_parse(self, ref_name: str) -> str:
        return self.run("rev-parse", ref_name)

    def resolve_commit(self, ref_name: str) -> str:
        return self.run("rev-list", "-n", "1", ref_name)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")


def init_local_git_repo(tmp_path: Path, *, default_branch: str = "main") -> LocalGitRepo:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    repo = LocalGitRepo(repo_root)
    repo.run("init", "--initial-branch", default_branch)
    repo.run("config", "user.name", "Test User")
    repo.run("config", "user.email", "test@example.invalid")
    return repo


def init_local_bare_remote(tmp_path: Path, *, name: str = "origin.git") -> Path:
    remote_root = tmp_path / name
    remote_root.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["git", "init", "--bare", str(remote_root)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return remote_root
