#!/usr/bin/env bash
# install-python.sh – installs the latest Python version through apt
# Usage: sudo ./install-python.sh
set -euo pipefail

apt update
apt install -y python3

echo "✅ Python $(python3 --version) installed"