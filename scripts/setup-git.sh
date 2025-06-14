#!/usr/bin/env bash
set -euo pipefail

# Optional inputs (positionals) or fallback to environment variables
AUTHOR_NAME="${1:-${CI_COMMIT_AUTHOR_NAME:-CI Bot}}"
AUTHOR_EMAIL="${2:-${CI_COMMIT_AUTHOR_EMAIL:-ci@bot.none}}"

echo "🔧 Setting up git author:"
echo "   Name : $AUTHOR_NAME"
echo "   Email: $AUTHOR_EMAIL"

git config --global user.name "$AUTHOR_NAME"
git config --global user.email "$AUTHOR_EMAIL"

# Check if the values were set correctly
CONFIGURED_NAME=$(git config --global user.name)
CONFIGURED_EMAIL=$(git config --global user.email)

if [[ "$CONFIGURED_NAME" != "$AUTHOR_NAME" ]]; then
  echo "❌ Error: Git username was not set correctly!" >&2
  exit 1
fi

if [[ "$CONFIGURED_EMAIL" != "$AUTHOR_EMAIL" ]]; then
  echo "❌ Error: Git email was not set correctly!" >&2
  exit 1
fi

echo "✅ Git configuration completed successfully."
