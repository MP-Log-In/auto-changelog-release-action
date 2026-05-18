from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


pytestmark = pytest.mark.podman


def test_install_git_cliff_smoke_in_podman() -> None:
    if os.getenv("RUN_PODMAN_TESTS") != "1":
        pytest.skip("Set RUN_PODMAN_TESTS=1 to enable Podman-based installer smoke tests.")

    podman = shutil.which("podman")
    if podman is None:
        pytest.skip("Podman is not available in PATH.")

    repo_root = Path(__file__).resolve().parents[2]
    image = os.getenv("PODMAN_TEST_IMAGE", "docker.io/library/ubuntu:24.04")

    container_script = textwrap.dedent(
        """
        set -euo pipefail
        export DEBIAN_FRONTEND=noninteractive
        apt-get update
        apt-get install -y ca-certificates curl tar grep sed gawk jq python3
        cd /workspace
        export INSTALL_DIR=/tmp/git-cliff-bin
        PYTHONPATH="/workspace/src${PYTHONPATH:+:${PYTHONPATH}}" \
          python3 -c "import os; from auto_changelog_release_action.install_git_cliff import install_git_cliff; install_git_cliff('2.10.1', install_dir=os.environ['INSTALL_DIR'])"
        /tmp/git-cliff-bin/git-cliff --version | grep '^git-cliff 2.10.1'
        """
    ).strip()

    subprocess.run(
        [
            podman,
            "run",
            "--rm",
            "-v",
            f"{repo_root}:/workspace:ro",
            image,
            "bash",
            "-lc",
            container_script,
        ],
        check=True,
    )
