#!/usr/bin/env bash
set -euo pipefail

# Optional inputs (positionals) oder Fallback auf Umgebungsvariablen
AUTHOR_NAME="${1:-${CI_COMMIT_AUTHOR_NAME:-CI Bot}}"
AUTHOR_EMAIL="${2:-${CI_COMMIT_AUTHOR_EMAIL:-ci@bot.none}}"

echo "🔧 Setting up git author:"
echo "   Name : $AUTHOR_NAME"
echo "   Email: $AUTHOR_EMAIL"

git config --global user.name "$AUTHOR_NAME"
git config --global user.email "$AUTHOR_EMAIL"

# Prüfung, ob die Werte korrekt gesetzt wurden
CONFIGURED_NAME=$(git config --global user.name)
CONFIGURED_EMAIL=$(git config --global user.email)

if [[ "$CONFIGURED_NAME" != "$AUTHOR_NAME" ]]; then
  echo "❌ Fehler: Git-Benutzername wurde nicht korrekt gesetzt!" >&2
  exit 1
fi

if [[ "$CONFIGURED_EMAIL" != "$AUTHOR_EMAIL" ]]; then
  echo "❌ Fehler: Git-Benutzer-E-Mail wurde nicht korrekt gesetzt!" >&2
  exit 1
fi

echo "✅ Git-Konfiguration erfolgreich abgeschlossen."
