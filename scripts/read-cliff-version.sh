#!/usr/bin/env bash
set -euo pipefail

CLIFF_TOML="${1:-cliff.toml}"

if [[ ! -f "$CLIFF_TOML" ]]; then
  echo "❌ File not found: $CLIFF_TOML" >&2
  exit 0
fi

VERSION_LINE=$(awk -F '=' '/^# CLIFF_VERSION=/ { gsub(/[" ]/, "", $2); print $2 }' "$CLIFF_TOML" || true)

if [[ -n "$VERSION_LINE" ]]; then
  echo "✅ Extracted CLIFF_VERSION: $VERSION_LINE"
else
  echo "⚠️  No CLIFF_VERSION found in $CLIFF_TOML"
fi

# Output für GitHub Actions / Composite Action
echo "version=${VERSION_LINE:-}" >> "$GITHUB_OUTPUT"
