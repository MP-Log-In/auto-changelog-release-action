#!/usr/bin/env bash
# install-python.sh – installs the latest Python version through apt
# Usage: sudo ./install-python.sh
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
    echo "ℹ️ Python $(python3 --version) is already installed"
    exit 0
fi

apt update
apt install -y python3

echo "✅ Python $(python3 --version) installed"