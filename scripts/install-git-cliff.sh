#!/usr/bin/env bash
# install-git-cliff.sh – holt neueste oder gewünschte git-cliff-Binary (x86_64)
# Usage: sudo ./install-git-cliff.sh        # neueste Version
#        sudo ./install-git-cliff.sh 2.9.0  # bestimmte Version
set -euo pipefail

REPO="orhun/git-cliff"
ARCH_OS="x86_64-unknown-linux-gnu"
INSTALL_DIR="/usr/local/bin"
VERSION="${1:-latest}"

need() { command -v "$1" >/dev/null || { echo "$1 fehlt"; exit 1; }; }
need curl; need tar; need grep; need sed; need awk

# 1 Version ermitteln → Release-JSON abrufen
if [[ "$VERSION" == "latest" ]]; then
  API_URL="https://api.github.com/repos/${REPO}/releases/latest"
else
  API_URL="https://api.github.com/repos/${REPO}/releases/tags/v${VERSION}"
fi

echo "🔍 Hole Release-Info ($API_URL)…"
JSON=$(curl -sL "$API_URL")

VERSION=$(echo "$JSON" | grep -m1 '"tag_name":' | sed -E 's/.*"v?([^"]+)".*/\1/')
ASSET_URL=$(echo "$JSON" |
  grep -Eo '"browser_download_url": *"[^"]+' |
  cut -d'"' -f4 |
  grep "${ARCH_OS}\\.tar" | head -n1)

[[ -z "$ASSET_URL" ]] && { echo "❌ passender Asset nicht gefunden"; exit 1; }

ASSET_FILE=$(basename "$ASSET_URL")
echo "📦 Lade git-cliff v${VERSION} (${ASSET_FILE}) …"
TMP=$(mktemp -d)
curl -#L -o "${TMP}/${ASSET_FILE}" "$ASSET_URL"

# 2 Entpacken je nach Endung
case "$ASSET_FILE" in
  *.tar.gz|*.tgz) tar -C "$TMP" -xzf "${TMP}/${ASSET_FILE}" ;;
  *.tar.xz)       tar -C "$TMP" -xJf "${TMP}/${ASSET_FILE}" ;;
  *.zip)          need unzip; unzip -q "${TMP}/${ASSET_FILE}" -d "$TMP" ;;
  *) echo "❌ Unbekanntes Archivformat: $ASSET_FILE"; exit 1 ;;
esac

BIN_PATH=$(find "$TMP" -type f -name git-cliff -perm -u+x | head -n1)
[[ -z "$BIN_PATH" ]] && { echo "❌ Binary nicht gefunden"; exit 1; }

sudo install -m755 "$BIN_PATH" "${INSTALL_DIR}/git-cliff"
echo "✅ git-cliff $(git-cliff --version) installiert unter ${INSTALL_DIR}"
