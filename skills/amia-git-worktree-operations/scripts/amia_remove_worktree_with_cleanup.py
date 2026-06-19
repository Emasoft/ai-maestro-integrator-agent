#!/usr/bin/env python3
"""
Remove a worktree and release all of the resources allocated to it.

This is the full-cleanup path: it stops services bound to the worktree's
allocated ports, tears down its Docker containers/volumes, removes the
worktree, releases the ports from the registry, and deletes the generated
config files.

The registry/service helpers (load_registry, save_registry,
stop_service_on_port) are provided by your port-management module; this script
shows how they compose into one removal routine.

Usage (as a library):
    from amia_remove_worktree_with_cleanup import remove_worktree_with_cleanup
    remove_worktree_with_cleanup("/tmp/worktrees/pr-123")
"""

import subprocess
from pathlib import Path


def remove_worktree_with_cleanup(
    worktree_path: str,
    load_registry,
    save_registry,
    stop_service_on_port,
) -> None:
    """Remove a worktree and free its ports, containers, and config files."""
    worktree = Path(worktree_path)

    # 1. Read the ports allocated to this worktree before removing anything.
    registry = load_registry()
    ports = registry["allocated_ports"].get(worktree_path, {})

    # 2. Stop every service still bound to those ports.
    for _service, port in ports.items():
        stop_service_on_port(port)

    # 3. Stop and remove the worktree's Docker containers and volumes.
    subprocess.run(["docker", "compose", "down", "-v"], cwd=worktree_path)

    # 4. Remove the worktree itself.
    subprocess.run(["git", "worktree", "remove", worktree_path])

    # 5. Release the ports from the registry.
    if worktree_path in registry["allocated_ports"]:
        del registry["allocated_ports"][worktree_path]
        save_registry(registry)

    # 6. Delete the generated configuration files (ignore if already gone).
    (worktree / ".env.worktree").unlink(missing_ok=True)
    (worktree / "docker-compose.yml").unlink(missing_ok=True)

    print(f"Removed worktree: {worktree_path}")
    print(f"Released {len(ports)} port(s)")
