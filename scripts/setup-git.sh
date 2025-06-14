#!/usr/bin/env bash
set -euo pipefail

# Optional inputs (positionals) oder Fallback auf Umgebungsvariablen
AUTHOR_NAME="${1:-${CI_COMMIT_AUTHOR_NAME:-CI Bot}}"
AUTHOR_EMAIL="${2:-${CI_COMMIT_AUTHOR_EMAIL:-ci@example.com}}"

echo "🔧 Setting up git author:"
echo "   Name : $AUTHOR_NAME"
echo "   Email: $AUTHOR_EMAIL"

git config --global user.name "$AUTHOR_NAME"
git config --global user.email "$AUTHOR_EMAIL"
