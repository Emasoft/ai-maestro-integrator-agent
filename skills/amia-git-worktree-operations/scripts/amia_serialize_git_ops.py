#!/usr/bin/env python3
"""
Serialize git operations across worktrees behind a single global lock.

When several agents drive their own worktrees in parallel, the file-level work
is safe to run concurrently but the git operations that touch shared refs
(commit, fetch, push, rebase, merge) must be serialized. Route every such
operation through `safe_git_operation` so only one runs at a time.

Usage (as a library):
    import asyncio
    from amia_serialize_git_ops import safe_git_operation
    asyncio.run(safe_git_operation("/tmp/worktrees/pr-123", ["commit", "-m", "fix"]))
"""

import asyncio
import subprocess

# One global lock shared by every call — the serialization point.
git_lock = asyncio.Lock()


async def safe_git_operation(worktree: str, operation: list[str]) -> None:
    """Run one git operation in `worktree` while holding the global git lock."""
    async with git_lock:
        # Only one git operation executes at a time across all worktrees.
        subprocess.run(["git", "-C", worktree] + operation)


async def _demo() -> None:
    # Two operations requested concurrently run one-after-the-other.
    await asyncio.gather(
        safe_git_operation("/tmp/worktrees/pr-123", ["status"]),
        safe_git_operation("/tmp/worktrees/pr-456", ["status"]),
    )


if __name__ == "__main__":
    asyncio.run(_demo())
