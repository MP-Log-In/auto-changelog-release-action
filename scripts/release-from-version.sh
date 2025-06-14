#!/usr/bin/env bash
set -euo pipefail

create_release() {
  local -r owner="$1" repo="$2" token="$3" version="$4" body_file="$5"
  local -i max_attempts=3 delay=5 attempt
  local http status

  # Release-Body für die JSON-Payload einlesen
  local body_json
  body_json=$(tail -n +2 "$body_file" | jq -Rs .)

  for (( attempt=1; attempt<=max_attempts; attempt++ )); do
    echo "🚀 Try $attempt/$max_attempts: creating release v$version …"

    http=$(curl -sS \
      -H "Authorization: token $token" \
      -H "Content-Type: application/json" \
      -o resp.json -w '%{http_code}' \
      -X POST "$GITHUB_API_URL/repos/$owner/$repo/releases" \
      -d @- <<EOF
{
  "tag_name": "v$version",
  "target_commitish": "main",
  "name": "Release v$version",
  "body": $body_json,
  "draft": false,
  "prerelease": false
}
EOF
    )

    status=$http
    if [[ $status == 201 ]]; then
      echo "✅ Release created (201)."
      rm -f resp.json
      return 0
    elif [[ $status == 409 ]]; then
      echo "🔁 Release already exists (409) – skipping."
      rm -f resp.json
      return 0
    fi

    echo "⚠️  Release attempt failed (HTTP $status)"
    cat resp.json
    [[ $attempt -lt $max_attempts ]] || { echo "❌ Giving up."; return 1; }
    sleep $((delay*attempt))   # Back-off: 5 s, 10 s, 15 s …
  done
}

VERSION_FILE="VERSION"
CHANGELOG_FILE="CHANGELOG.md"
CLIFF_CONFIG="cliff.toml"
RELEASE_BODY_TMP="$(mktemp)"

# === Schritt 1: Version lesen ===
if [[ ! -f "$VERSION_FILE" ]]; then
  echo "❌ VERSION file not found"
  exit 1
fi
VERSION="$(<"$VERSION_FILE")"
echo "📦 Version: $VERSION"

# === Schritt 2: Changelog für Release erzeugen ===
echo "📄 Generating changelog for tag v$VERSION"
git-cliff -c "$CLIFF_CONFIG" -t "v$VERSION" -o "$CHANGELOG_FILE"

ESCAPED_VERSION="$(echo "$VERSION" | sed 's/\./\\./g')"

awk -v ver="$ESCAPED_VERSION" '
  $0 ~ "^## \\[" ver "\\]" {
    print_flag=1
    line=$0
    sub(/^## /,"",line)
    sub(/\\s*\\(.*\\)/,"",line)
    print line
    next
  }
  $0 ~ "^## \\[" && $0 !~ "^## \\[" ver "\\]" { print_flag=0 }
  print_flag
' "$CHANGELOG_FILE" > "$RELEASE_BODY_TMP"

# === Schritt 3: Changelog committen ===
git add "$CHANGELOG_FILE"
if git diff --cached --quiet; then
  echo "✅ No changes to commit"
else
  echo "📝 Committing updated changelog"
  git commit -m "chore(changelog): update changelog for v$VERSION"
  git push origin main
fi

# === Schritt 4: Tag anlegen, falls nötig ===
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
  echo "🔁 Tag v$VERSION already exists, skipping."
else
  echo "🏷️  Creating annotated tag v$VERSION"
  export GIT_AUTHOR_DATE="$(date --iso-8601=seconds)"
  export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
  git tag -a "v$VERSION" -F "$RELEASE_BODY_TMP" --cleanup=verbatim
  git push origin "v$VERSION"
fi

# === Schritt 5: Release anlegen (mit Retry) ===
OWNER="${GITHUB_REPOSITORY%/*}"
REPO="${GITHUB_REPOSITORY#*/}"
TOKEN="${RELEASE_PUBLISH_TOKEN:-$ACTIONS_RUNTIME_TOKEN}"

if [[ -z "${RELEASE_PUBLISH_TOKEN:-}" ]]; then
  echo "::warning title=Limited Release Propagation::"
  echo "RELEASE_PUBLISH_TOKEN is not set. Using ACTIONS_RUNTIME_TOKEN instead."
  echo "⚠️  Release events may not trigger other workflows if created with the runtime token."
  echo
fi

create_release "$OWNER" "$REPO" "$TOKEN" "$VERSION" "$RELEASE_BODY_TMP"

echo "🎉 Workflow finished successfully."
