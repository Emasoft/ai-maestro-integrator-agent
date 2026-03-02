#!/usr/bin/env python3
"""
Safely remove a git worktree after verifying it is clean.

This script checks for uncommitted changes, verifies commits are pushed,
then removes the worktree and prunes stale entries.

Usage:
    python amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123
    python amia_cleanup_worktree.py --worktree-path /tmp/worktrees/pr-123 --force
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, stderr."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def find_main_repo(worktree_path: str) -> str | None:
    """Find the main repository from a worktree path."""
    git_file = Path(worktree_path) / ".git"
    if not git_file.exists():
        return None

    if git_file.is_file():
        content = git_file.read_text(encoding="utf-8").strip()
        if content.startswith("gitdir:"):
            gitdir = content[7:].strip()
            # gitdir points to .git/worktrees/<name>, go up to find main repo
            main_git = Path(gitdir).parent.parent
            return str(main_git.parent)
    return None


def check_uncommitted_changes(worktree_path: str) -> tuple[bool, list[str]]:
    """Check for uncommitted changes. Returns (has_changes, changed_files)."""
    code, stdout, _ = run_git(["status", "--porcelain"], cwd=worktree_path)
    if code != 0:
        return False, []
    if not stdout:
        return False, []
    return True, stdout.split("\n")


def check_unpushed_commits(worktree_path: str) -> tuple[bool, int]:
    """Check for unpushed commits. Returns (has_unpushed, count)."""
    code, stdout, _ = run_git(["rev-list", "@{u}..HEAD", "--count"], cwd=worktree_path)
    if code != 0:
        # No upstream set, assume we should check
        return True, -1
    count = int(stdout) if stdout.isdigit() else 0
    return count > 0, count


def remove_worktree(
    main_repo: str, worktree_path: str, force: bool
) -> tuple[bool, str]:
    """Remove the worktree. Returns (success, message)."""
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(worktree_path)

    code, _stdout, stderr = run_git(args, cwd=main_repo)
    if code != 0:
        return False, f"Failed to remove worktree: {stderr}"
    return True, "Worktree removed successfully"


def prune_worktrees(main_repo: str) -> tuple[bool, str]:
    """Prune stale worktree entries. Returns (success, message)."""
    code, _stdout, stderr = run_git(["worktree", "prune"], cwd=main_repo)
    if code != 0:
        return False, f"Failed to prune worktrees: {stderr}"
    return True, "Stale worktree entries pruned"


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely remove a git worktree")
    parser.add_argument(
        "--worktree-path",
        type=str,
        required=True,
        help="Path to the worktree to remove",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force removal even if worktree has uncommitted changes",
    )
    parser.add_argument(
        "--skip-push-check",
        action="store_true",
        help="Skip checking for unpushed commits",
    )
    args = parser.parse_args()

    worktree_path = str(Path(args.worktree_path).resolve())

    # Check if worktree exists
    if not Path(worktree_path).exists():
        result: dict[str, Any] = {
            "status": "not_found",
            "worktree_path": worktree_path,
            "message": "Worktree does not exist",
        }
        print(json.dumps(result, indent=2))
        return 0

    # Find main repo
    main_repo = find_main_repo(worktree_path)
    if not main_repo:
        result = {
            "status": "error",
            "error": "Could not determine main repository",
        }
        print(json.dumps(result, indent=2))
        return 1

    # Check for uncommitted changes
    has_changes, changed_files = check_uncommitted_changes(worktree_path)
    if has_changes and not args.force:
        result = {
            "status": "blocked",
            "reason": "uncommitted_changes",
            "worktree_path": worktree_path,
            "changed_files": changed_files,
            "message": "Worktree has uncommitted changes. Use --force to override.",
        }
        print(json.dumps(result, indent=2))
        return 1

    # Check for unpushed commits
    if not args.skip_push_check:
        has_unpushed, count = check_unpushed_commits(worktree_path)
        if has_unpushed and not args.force:
            result = {
                "status": "blocked",
                "reason": "unpushed_commits",
                "worktree_path": worktree_path,
                "unpushed_count": count,
                "message": "Worktree has unpushed commits. Use --force to override.",
            }
            print(json.dumps(result, indent=2))
            return 1

    # Remove worktree
    success, msg = remove_worktree(main_repo, worktree_path, args.force)
    if not success:
        result = {"status": "error", "error": msg}
        print(json.dumps(result, indent=2))
        return 1

    # Prune stale entries
    prune_worktrees(main_repo)

    result = {
        "status": "removed",
        "worktree_path": worktree_path,
        "main_repo": main_repo,
        "forced": args.force,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
