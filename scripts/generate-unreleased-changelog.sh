#!/usr/bin/env bash
set -euo pipefail

CHANGELOG_FILE="CHANGELOG.md"
CLIFF_CONFIG="cliff.toml"
GIT_BRANCH="${GITHUB_REF##refs/heads/}"

# === Step 1: Generate Changelog (only if file exists or on main) ===
if [[ -f "$CHANGELOG_FILE" || "$GIT_BRANCH" == "main" ]]; then
  echo "📄 Generating $CHANGELOG_FILE using git-cliff..."
  git-cliff -c "$CLIFF_CONFIG" --context \
|   "${GITHUB_ACTION_PATH}/scripts/augment_context.py" \
|   git-cliff -c "$CLIFF_CONFIG" --from-context - -o "$CHANGELOG_FILE"
else
  echo "ℹ️  $CHANGELOG_FILE does not exist and branch is not 'main'. Skipping generation."
  exit 0
fi

# === Step 2: Commit and push changes if any ===
git add "$CHANGELOG_FILE"

if git diff --cached --quiet; then
  echo "✅ No changes to commit – changelog is up to date."
else
  echo "✍️  Committing updated $CHANGELOG_FILE..."
  git commit -m "chore(changelog): update unreleased changelog"
  echo "🚀 Pushing to origin/$GIT_BRANCH..."
  git push origin "$GIT_BRANCH"
fi
