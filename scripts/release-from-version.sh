#!/usr/bin/env bash
set -euo pipefail

VERSION_FILE="VERSION"
CHANGELOG_FILE="CHANGELOG.md"
CLIFF_CONFIG="cliff.toml"
RELEASE_BODY_TMP="$(mktemp)"
BODY_OUTPUT_VAR="changelog_body_path"

# === Schritt 1: Read version from VERSION ===
if [[ ! -f "$VERSION_FILE" ]]; then
  echo "❌ VERSION file not found"
  exit 1
fi
VERSION="$(<"$VERSION_FILE")"
echo "📦 Version: $VERSION"

# === Schritt 2: Generate changelog for release ===
echo "📄 Generating changelog for tag v$VERSION"
git-cliff -c "$CLIFF_CONFIG" -t "v$VERSION" -o "$CHANGELOG_FILE"

ESCAPED_VERSION="$(echo "$VERSION" | sed 's/\./\\./g')"

awk -v ver="$ESCAPED_VERSION" '
  $0 ~ "^## \\[" ver "\\]" {
    print_flag=1
    line = $0
    sub(/^## /, "", line)
    sub(/\\s*\\(.*\\)/, "", line)  # entfernt z. B. "(...)" oder "(*)"
    print line
    next
  }
  $0 ~ "^## \\[" && $0 !~ "^## \\[" ver "\\]" {
    print_flag=0
  }
  print_flag
' "$CHANGELOG_FILE" > "$RELEASE_BODY_TMP"

# === Schritt 3: Commit updated changelog ===
git add "$CHANGELOG_FILE"
if git diff --cached --quiet; then
  echo "✅ No changes to commit"
else
  echo "📝 Committing updated changelog"
  git commit -m "chore(changelog): update changelog for v$VERSION"
  git push origin main
fi

# === Schritt 4: Create tag if not exists ===
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
  echo "🔁 Tag v$VERSION already exists, skipping."
else
  echo "🏷️  Creating annotated tag v$VERSION"
  export GIT_AUTHOR_DATE="$(date --iso-8601=seconds)"
  export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
  git tag -a "v$VERSION" -F "$RELEASE_BODY_TMP" --cleanup=verbatim
  git push origin "v$VERSION"
fi

# === Schritt 5: Create Gitea release ===
OWNER="$(echo "$GITHUB_REPOSITORY" | cut -d/ -f1)"
REPO="$(echo "$GITHUB_REPOSITORY" | cut -d/ -f2)"
TOKEN="${RELEASE_PUBLISH_TOKEN:-$ACTIONS_RUNTIME_TOKEN}"

if [[ -z "${RELEASE_PUBLISH_TOKEN:-}" ]]; then
  echo "::warning title=Limited Release Propagation::"
  echo "RELEASE_PUBLISH_TOKEN is not set. Using ACTIONS_RUNTIME_TOKEN instead."
  echo "⚠️  Release events may not trigger other workflows if created with the runtime token."
  echo
fi

# Prüfen, ob Release bereits existiert
if curl -sf "$GITHUB_API_URL/repos/$OWNER/$REPO/releases/tags/v$VERSION" \
  -H "Authorization: token $TOKEN" > /dev/null; then
  echo "🔁 Release for tag v$VERSION already exists, skipping."
  exit 0
fi

echo "🚀 Creating Gitea release for v$VERSION"

RELEASE_BODY=$(tail -n +2 "$RELEASE_BODY_TMP" | jq -Rs .)

curl -X POST "$GITHUB_API_URL/repos/$OWNER/$REPO/releases" \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "tag_name": "v$VERSION",
  "target_commitish": "main",
  "name": "Release v$VERSION",
  "body": $RELEASE_BODY,
  "draft": false,
  "prerelease": false
}
EOF

echo "✅ Release for tag $VERSION created successfully."
