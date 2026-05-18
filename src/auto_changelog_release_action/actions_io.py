"""Helpers for writing values to GitHub and Gitea Actions files."""

from __future__ import annotations


def append_kv(path: str | None, key: str, value: str) -> None:
    """Append one key-value pair to an Actions output or env file."""

    if not path:
        return

    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")
