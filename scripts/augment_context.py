#!/usr/bin/env python3
import json
import subprocess
import sys

def git_commits_between(parent, merge):
    """Return list of commit hashes between parent and merge (exclusive of parent, inclusive of merge)."""
    out = subprocess.check_output(
        ["git", "rev-list", f"{parent}..{merge}", "--no-merges"],
        text=True
    )
    return [line.strip() for line in out.splitlines() if line.strip()]

def load_context(path=None):
    if path:
        with open(path) as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)

def main(path=None):
    context = load_context(path)
    commits = context[0]["commits"]
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

            if len(parent_ids) >= 2:
                mainline = parent_ids[0]
                children_ids = git_commits_between(mainline, merge_id)

                children = []
                for cid in children_ids:
                    if cid in commits_by_id:
                        children.append(commits_by_id[cid])
                        consumed.add(cid)

                if not c.get("extra") or not isinstance(c["extra"], dict):
                    c["extra"] = {}
                c["extra"]["children"] = children

        new_commits.append(c)

    filtered = [c for c in new_commits if c["id"] not in consumed]
    context[0]["commits"] = filtered

    json.dump(context, sys.stdout, indent=4)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
