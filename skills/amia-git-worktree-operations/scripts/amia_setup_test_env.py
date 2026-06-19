#!/usr/bin/env python3
"""
Create an isolated test environment inside a worktree.

Builds a fresh virtualenv in the worktree and installs the project's runtime
and test dependencies into it, so each worktree's tests run against their own
interpreter and packages.

Usage:
    python amia_setup_test_env.py --worktree-path /tmp/worktrees/pr-123
"""

import argparse
import os
import subprocess
import sys


def setup_test_environment(worktree_path: str) -> None:
    """Create a venv in the worktree and install its dependencies."""
    # Create the virtualenv.
    venv_path = os.path.join(worktree_path, ".venv")
    subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)

    # Resolve the venv's pip.
    pip = os.path.join(venv_path, "bin", "pip")

    # Install runtime and test dependencies.
    subprocess.run([pip, "install", "-r", "requirements.txt"], cwd=worktree_path, check=True)
    subprocess.run([pip, "install", "-r", "requirements-test.txt"], cwd=worktree_path, check=True)

    print(f"Test environment ready: {worktree_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree-path", required=True, help="Path to the worktree")
    args = parser.parse_args()
    setup_test_environment(args.worktree_path)


if __name__ == "__main__":
    main()
