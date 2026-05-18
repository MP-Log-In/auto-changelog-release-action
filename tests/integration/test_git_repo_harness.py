from __future__ import annotations

from tests.support.git_repo import init_local_git_repo


def test_local_git_repo_can_create_commits_and_tags(tmp_path) -> None:
    repo = init_local_git_repo(tmp_path)
    repo.write("VERSION", "1.9.1\n")

    first_commit = repo.commit_all("chore: initial import")
    repo.tag("v1.9.1", message="Release v1.9.1")

    repo.write("VERSION", "1.9.2\n")
    second_commit = repo.commit_all("fix: patch release")

    assert first_commit != second_commit
    assert repo.read("VERSION") == "1.9.2\n"
    assert repo.resolve_commit("v1.9.1") == first_commit
