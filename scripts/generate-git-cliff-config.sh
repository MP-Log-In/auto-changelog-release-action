#!/usr/bin/env bash
set -euo pipefail

CLIFF_CONFIG="cliff.toml"

# Check if cliff.toml exists, if not, copy cliff.toml.template from the Action
if [ ! -f "$CLIFF_CONFIG" ]; then
  echo "cliff.toml not found, using template from action."
  cp "${GITHUB_ACTION_PATH:-${github_action_path:-${{ github.action_path }}}}/cliff.toml.template" "$CLIFF_CONFIG"
  # Replace placeholders in the copied config
  OWNER="${GITHUB_REPOSITORY%/*}"
  REPO="${GITHUB_REPOSITORY#*/}"
  sed -i "s/owner = \"%OWNER%\"/owner = \"$OWNER\"/g" "$CLIFF_CONFIG"
  sed -i "s/repo = \"%REPO%\"/repo = \"$REPO\"/g" "$CLIFF_CONFIG"
fi