#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
import re

VERSION_RE = re.compile(r"^(v\d+\.\d+\.\d+)(?:-(.+))?$")

def extract_type(raw_message: str) -> str | None:
    m = re.match(r"^(\w+)(?:\([^)]+\))?:", raw_message.strip())
    return m.group(1) if m else None

def git_commits_between(parent, merge):
    """Return list of commit hashes between parent and merge (exclusive of parent, inclusive of merge)."""
    out = subprocess.check_output(
        ["git", "rev-list", f"{parent}..{merge}", "--no-merges"],
        text=True
    )
    return [line.strip() for line in out.splitlines() if line.strip()]

def parse_version_parts(version: str | None):
    if not isinstance(version, str):
        return None
    match = VERSION_RE.match(version.strip())
    if not match:
        return None
    return match.group(1), match.group(2)

def load_context(path=None):
    if path:
        with open(path) as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)

def augment_merge_commits(entry):
    commits = entry.get("commits") or []
    commits_by_id = {c["id"]: c for c in commits}
    new_commits = []
    consumed = set()

    for c in commits:
        if c.get("merge_commit"):
            parents = subprocess.check_output(
                ["git", "rev-list", "--parents", "-n", "1", c["id"]],
                text=True
            ).strip().split()
            merge_id, *parent_ids = parents

            parent_type = extract_type(c["raw_message"])

            if len(parent_ids) >= 2:
                mainline = parent_ids[0]
                children_ids = git_commits_between(mainline, merge_id)

                children = []
                for cid in children_ids:
                    if cid in commits_by_id:
                        child = commits_by_id[cid]
                        child_type = extract_type(child["raw_message"])
                        if child_type and parent_type and child_type != parent_type:
                            if not child.get("extra") or not isinstance(child["extra"], dict):
                                child["extra"] = {}
                            child["extra"]["mismatch_type"] = child_type
                        children.append(child)
                        consumed.add(cid)

                if not c.get("extra") or not isinstance(c["extra"], dict):
                    c["extra"] = {}
                c["extra"]["children"] = children

        new_commits.append(c)

    entry["commits"] = [c for c in new_commits if c["id"] not in consumed]

def collect_prerelease_commits(entries):
    per_base = {}
    per_base_seen = {}

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        parsed = parse_version_parts(entry.get("version"))
        if not parsed:
            continue
        base_version, suffix = parsed
        if not suffix:
            continue

        commits = entry.get("commits")
        if not isinstance(commits, list):
            continue

        bucket = per_base.setdefault(base_version, [])
        seen_ids = per_base_seen.setdefault(base_version, set())
        for commit in commits:
            if not isinstance(commit, dict):
                continue
            commit_id = commit.get("id")
            if not commit_id or commit_id in seen_ids:
                continue

            seen_ids.add(commit_id)
            bucket.append({
                "id": commit_id,
                "tag": entry.get("version"),
                "commit": commit,
            })

    return per_base

def inject_prerelease_commits(entries, prerelease_commits):
    if not prerelease_commits:
        return

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        parsed = parse_version_parts(entry.get("version"))
        if not parsed:
            continue
        base_version, suffix = parsed
        if suffix:
            continue

        bucket = prerelease_commits.get(base_version)
        if not bucket:
            continue

        commits = entry.get("commits")
        if not isinstance(commits, list):
            continue

        existing_ids = {c.get("id") for c in commits if isinstance(c, dict)}
        for payload in bucket:
            commit_id = payload["id"]
            if commit_id in existing_ids:
                continue

            clone = copy.deepcopy(payload["commit"])
            extra = clone.get("extra")
            if not isinstance(extra, dict):
                extra = {}
            extra["from_prerelease"] = payload["tag"]
            clone["extra"] = extra
            commits.append(clone)
            existing_ids.add(commit_id)

def flag_pre_release(entry):
    parsed = parse_version_parts(entry.get("version"))
    if not parsed:
        return

    extra = entry.get("extra") if isinstance(entry.get("extra"), dict) else {}
    extra["pre_release"] = parsed[1] is not None
    entry["extra"] = extra

def main(path=None):
    context = load_context(path)

    for entry in context:
        if isinstance(entry, dict) and "commits" in entry:
            augment_merge_commits(entry)

    prerelease_commits = collect_prerelease_commits(context)
    inject_prerelease_commits(context, prerelease_commits)

    for entry in context:
        if isinstance(entry, dict):
            flag_pre_release(entry)

    json.dump(context, sys.stdout, indent=4)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
