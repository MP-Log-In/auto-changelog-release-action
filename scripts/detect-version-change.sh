#!/usr/bin/env bash
set -euo pipefail

# === Inputs from GitHub/Gitea Action environment ===
GIT_REF="${GITHUB_REF:-}"
COMMIT_BEFORE="${GITHUB_EVENT_BEFORE:-}"
COMMIT_AFTER="${GITHUB_SHA:-}"
VERSION_FILE="VERSION"

echo "🔍 Comparing commits:"
echo "Before: $COMMIT_BEFORE"
echo "After:  $COMMIT_AFTER"

# === Check branch condition ===
if [[ "$GIT_REF" != "refs/heads/main" ]]; then
  echo "Not on 'main' branch – skipping version check."
  echo "version_changed=false" >> "$GITHUB_OUTPUT"
  exit 0
fi

echo "📄 Changed files:"
git diff --name-only "$COMMIT_BEFORE" "$COMMIT_AFTER" || echo "(diff failed)"

if git diff --name-only "$COMMIT_BEFORE" "$COMMIT_AFTER" | grep -q "^$VERSION_FILE$"; then
  echo "✅ VERSION file was changed"
  echo "VERSION_CHANGED=true" >> "$GITHUB_ENV"
  echo "version_changed=true" >> "$GITHUB_OUTPUT"
else
  echo "ℹ️ VERSION file not changed"
  echo "VERSION_CHANGED=false" >> "$GITHUB_ENV"
  echo "version_changed=false" >> "$GITHUB_OUTPUT"
fi
