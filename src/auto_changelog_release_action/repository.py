"""Helpers for splitting repository slugs into owner and repo names."""

from __future__ import annotations


def split_repository_slug(repository: str) -> tuple[str, str]:
    """Split owner/repo, or duplicate a single token for both parts."""

    if "/" not in repository:
        return repository, repository

    owner, repo = repository.split("/", 1)
    return owner, repo
