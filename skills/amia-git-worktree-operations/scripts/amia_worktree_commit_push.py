#!/usr/bin/env python3
"""
Commit and push changes in a git worktree.

This script stages all changes, commits with a message, and pushes to the remote
branch. It includes safety checks and returns structured status information.

Usage:
    python amia_worktree_commit_push.py --worktree-path /tmp/worktrees/pr-123 --message "Fix bug"
    python amia_worktree_commit_push.py -w /tmp/worktrees/pr-123 -m "Update" --push
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, stderr."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_current_branch(worktree_path: str) -> str | None:
    """Get the current branch name in the worktree."""
    code, stdout, _ = run_git(["branch", "--show-current"], cwd=worktree_path)
    return stdout if code == 0 and stdout else None


def has_changes(worktree_path: str) -> bool:
    """Check if there are any changes to commit."""
    code, stdout, _ = run_git(["status", "--porcelain"], cwd=worktree_path)
    return code == 0 and bool(stdout.strip())


def stage_all_changes(worktree_path: str) -> tuple[bool, str]:
    """Stage all changes in the worktree."""
    code, _stdout, stderr = run_git(["add", "-A"], cwd=worktree_path)
    if code != 0:
        return False, f"Failed to stage changes: {stderr}"
    return True, "Changes staged"


def commit_changes(worktree_path: str, message: str) -> tuple[bool, str, str | None]:
    """Commit staged changes. Returns (success, message, commit_hash)."""
    code, stdout, stderr = run_git(["commit", "-m", message], cwd=worktree_path)
    if code != 0:
        if "nothing to commit" in stderr or "nothing to commit" in stdout:
            return True, "Nothing to commit", None
        return False, f"Commit failed: {stderr}", None

    # Get commit hash
    code, hash_out, _ = run_git(["rev-parse", "HEAD"], cwd=worktree_path)
    commit_hash = hash_out if code == 0 else None

    return True, "Changes committed", commit_hash


def push_changes(worktree_path: str, branch: str) -> tuple[bool, str]:
    """Push changes to remote."""
    code, _stdout, stderr = run_git(["push", "origin", branch], cwd=worktree_path)
    if code != 0:
        return False, f"Push failed: {stderr}"
    return True, "Changes pushed to remote"


def get_remote_status(worktree_path: str) -> dict[str, Any]:
    """Get information about remote tracking status."""
    status: dict[str, Any] = {
        "has_upstream": False,
        "commits_ahead": 0,
        "commits_behind": 0,
    }

    # Check if upstream is set
    code, stdout, _ = run_git(["rev-parse", "--abbrev-ref", "@{u}"], cwd=worktree_path)
    if code == 0 and stdout:
        status["has_upstream"] = True
        status["upstream"] = stdout

        # Get ahead/behind counts
        code, stdout, _ = run_git(
            ["rev-list", "--left-right", "--count", "@{u}...HEAD"], cwd=worktree_path
        )
        if code == 0 and stdout:
            parts = stdout.split()
            if len(parts) == 2:
                status["commits_behind"] = int(parts[0])
                status["commits_ahead"] = int(parts[1])

    return status


def main() -> int:
    parser = argparse.ArgumentParser(description="Commit and push in a worktree")
    parser.add_argument(
        "-w",
        "--worktree-path",
        type=str,
        required=True,
        help="Path to the worktree",
    )
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=True,
        help="Commit message",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Do not push after commit",
    )
    parser.add_argument(
        "--force-empty",
        action="store_true",
        help="Create commit even if no changes",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = parser.parse_args()

    worktree_path = str(Path(args.worktree_path).resolve())
    should_push = not args.no_push

    # Verify worktree exists
    if not Path(worktree_path).exists():
        result: dict[str, Any] = {
            "status": "error",
            "error": f"Worktree not found: {worktree_path}",
        }
        write_output(result, "amia_worktree_commit_push", args.output_file)
        return 1

    # Get current branch
    branch = get_current_branch(worktree_path)
    if not branch:
        result = {"status": "error", "error": "Could not determine current branch"}
        write_output(result, "amia_worktree_commit_push", args.output_file)
        return 1

    # Check for changes
    if not has_changes(worktree_path) and not args.force_empty:
        result = {
            "status": "no_changes",
            "worktree_path": worktree_path,
            "branch": branch,
            "message": "No changes to commit",
        }
        write_output(result, "amia_worktree_commit_push", args.output_file)
        return 0

    # Stage changes
    success, msg = stage_all_changes(worktree_path)
    if not success:
        result = {"status": "error", "error": msg}
        write_output(result, "amia_worktree_commit_push", args.output_file)
        return 1

    # Commit
    success, msg, commit_hash = commit_changes(worktree_path, args.message)
    if not success:
        result = {"status": "error", "error": msg}
        write_output(result, "amia_worktree_commit_push", args.output_file)
        return 1

    result = {
        "status": "committed",
        "worktree_path": worktree_path,
        "branch": branch,
        "commit_hash": commit_hash,
        "message": args.message,
        "pushed": False,
    }

    # Push if requested
    if should_push and commit_hash:
        success, msg = push_changes(worktree_path, branch)
        if not success:
            result["status"] = "commit_only"
            result["push_error"] = msg
        else:
            result["status"] = "pushed"
            result["pushed"] = True

    # Add remote status
    result["remote_status"] = get_remote_status(worktree_path)

    write_output(result, "amia_worktree_commit_push", args.output_file)
    return 0 if result["status"] in ("committed", "pushed", "no_changes") else 1


if __name__ == "__main__":
    sys.exit(main())
