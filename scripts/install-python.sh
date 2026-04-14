#!/usr/bin/env bash
# install-python.sh – installs the latest Python version through apt
# Usage: sudo ./install-python.sh
set -euo pipefail

if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo "✅ Python ${PYTHON_VERSION} is already installed"
    exit 0
fi

apt update -qq
apt install -yqq python3

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ Python ${PYTHON_VERSION} installed"
