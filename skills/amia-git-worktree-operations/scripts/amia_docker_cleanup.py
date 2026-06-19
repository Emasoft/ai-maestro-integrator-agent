#!/usr/bin/env python3
"""
Stop and remove the Docker containers belonging to a worktree.

Containers are matched by name (the worktree name is expected to appear in
each container's name, e.g. via a `name=<worktree>` compose project prefix).
Call this from a worktree-removal routine so containers do not outlive the
worktree they were created for.

Usage:
    python amia_docker_cleanup.py --worktree-name pr-123
"""

import argparse
import subprocess


def cleanup_docker(worktree_name: str) -> int:
    """Stop and remove Docker containers whose name contains worktree_name."""
    # Find containers tagged with the worktree name.
    result = subprocess.run(
        ["docker", "ps", "-a", "--filter", f"name={worktree_name}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )

    containers = [c for c in result.stdout.strip().split("\n") if c]

    for container in containers:
        # Stop then remove each container.
        subprocess.run(["docker", "stop", container])
        subprocess.run(["docker", "rm", container])

    print(f"Cleaned up {len(containers)} container(s) for: {worktree_name}")
    return len(containers)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree-name", required=True, help="Worktree name to match in container names")
    args = parser.parse_args()
    cleanup_docker(args.worktree_name)


if __name__ == "__main__":
    main()
