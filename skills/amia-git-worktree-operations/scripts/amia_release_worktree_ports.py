#!/usr/bin/env python3
"""
Release a worktree's allocated ports back into the registry.

Removes every port the worktree had reserved from the registry's
``allocated_ports`` list and writes the updated registry back to
``worktrees_registry.json``. Call this during worktree teardown so the ports
become available to future worktrees.

Usage (as a library):
    from amia_release_worktree_ports import release_worktree_ports
    release_worktree_ports(registry, "pr-123")
"""

import json


def release_worktree_ports(registry: dict, worktree_id: str) -> None:
    """Free the worktree's ports in the registry and persist the registry."""
    worktree = registry["worktrees"].get(worktree_id)
    if not worktree or "ports" not in worktree:
        return

    # Drop each of this worktree's ports from the allocated list.
    allocated = registry.get("allocated_ports", [])
    for port in worktree["ports"].values():
        if port in allocated:
            allocated.remove(port)

    registry["allocated_ports"] = allocated

    # Persist the updated registry.
    with open("worktrees_registry.json", "w") as f:
        json.dump(registry, f, indent=2)
