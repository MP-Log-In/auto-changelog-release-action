#!/usr/bin/env bash
# install-git-cliff.sh – fetches the latest or specified git-cliff binary (x86_64)
# Usage: sudo ./install-git-cliff.sh        # latest version
#        sudo ./install-git-cliff.sh 2.9.0  # specific version
set -euo pipefail

REPO="orhun/git-cliff"
ARCH_OS="x86_64-unknown-linux-gnu"
INSTALL_DIR="/usr/local/bin"
if [[ -z "${1:-}" ]]; then
  VERSION="2.10.1"
else
  VERSION="$1"
fi

need() { command -v "$1" >/dev/null || { echo "$1 is missing"; exit 1; }; }
need curl; need tar; need grep; need sed; need awk; need jq

# 1 Determine version → Fetch release JSON
if [[ "$VERSION" == "latest" ]]; then
  API_URL="https://api.github.com/repos/${REPO}/releases/latest"
else
  API_URL="https://api.github.com/repos/${REPO}/releases/tags/v${VERSION}"
fi

echo "🔍 Fetching release info ($API_URL)…"
JSON=$(curl -fsSL "$API_URL") || {
  echo "❌ Failed to fetch release info"
  exit 1
}

VERSION=$(jq -r '.tag_name' <<< "$JSON") || {
  echo "❌ Could not extract version"
  exit 1
}

ASSET_URL=$(jq -r '.assets[]?.browser_download_url' <<< "$JSON" |
  grep "${ARCH_OS}\.tar" | head -n1)

if [[ -z "$ASSET_URL" ]]; then
  echo "❌ Matching asset not found for architecture ${ARCH_OS}"
  exit 1
fi

ASSET_FILE=$(basename "$ASSET_URL")
echo "📦 Downloading git-cliff v${VERSION} (${ASSET_FILE}) …"
TMP=$(mktemp -d)
curl -#L -o "${TMP}/${ASSET_FILE}" "$ASSET_URL"

# 2 Extract based on file extension
case "$ASSET_FILE" in
  *.tar.gz|*.tgz) tar -C "$TMP" -xzf "${TMP}/${ASSET_FILE}" ;;
  *.tar.xz)       tar -C "$TMP" -xJf "${TMP}/${ASSET_FILE}" ;;
  *.zip)          need unzip; unzip -q "${TMP}/${ASSET_FILE}" -d "$TMP" ;;
  *) echo "❌ Unknown archive format: $ASSET_FILE"; exit 1 ;;
esac

BIN_PATH=$(find "$TMP" -type f -name git-cliff -perm -u+x | head -n1)
[[ -z "$BIN_PATH" ]] && { echo "❌ Binary not found"; exit 1; }

sudo install -m755 "$BIN_PATH" "${INSTALL_DIR}/git-cliff"
echo "✅ git-cliff $(git-cliff --version) installed in ${INSTALL_DIR}"
