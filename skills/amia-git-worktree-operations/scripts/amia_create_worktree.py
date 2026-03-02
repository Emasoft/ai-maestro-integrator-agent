#!/usr/bin/env python3
"""
Create a git worktree for a pull request.

This script fetches the PR branch from the remote and creates an isolated
worktree directory for parallel PR processing.

Usage:
    python amia_create_worktree.py --pr 123
    python amia_create_worktree.py --pr 123 --repo /path/to/repo --base-path /custom/path
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def run_git(args: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    """Run a git command and return exit code, stdout, stderr."""
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def find_repo_root(start_path: str | None = None) -> str | None:
    """Find the git repository root from start_path or current directory."""
    code, stdout, _ = run_git(["rev-parse", "--show-toplevel"], cwd=start_path)
    return stdout if code == 0 else None


def fetch_pr_branch(repo: str, pr_number: int) -> tuple[bool, str]:
    """Fetch PR branch from remote. Returns (success, message)."""
    branch_name = f"pr-{pr_number}"
    ref = f"pull/{pr_number}/head:{branch_name}"
    code, _, stderr = run_git(["fetch", "origin", ref], cwd=repo)
    if code != 0:
        return False, f"Failed to fetch PR #{pr_number}: {stderr}"
    return True, f"Fetched PR #{pr_number} as branch {branch_name}"


def create_worktree(repo: str, worktree_path: str, branch: str) -> tuple[bool, str]:
    """Create a worktree at the specified path. Returns (success, message)."""
    code, _stdout, stderr = run_git(
        ["worktree", "add", worktree_path, branch], cwd=repo
    )
    if code != 0:
        if "already checked out" in stderr:
            return False, f"Branch {branch} already checked out in another worktree"
        return False, f"Failed to create worktree: {stderr}"
    return True, f"Created worktree at {worktree_path}"


def verify_worktree(worktree_path: str) -> tuple[bool, str]:
    """Verify the worktree was created successfully."""
    if not Path(worktree_path).is_dir():
        return False, f"Worktree directory does not exist: {worktree_path}"
    git_file = Path(worktree_path) / ".git"
    if not git_file.exists():
        return False, f"Worktree missing .git file: {worktree_path}"
    return True, "Worktree verified successfully"


def main() -> int:
    parser = argparse.ArgumentParser(description="Create worktree for a PR")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", type=str, help="Path to main repository")
    # Use platform-appropriate temp dir instead of hardcoded /tmp (CC-XP-001)
    default_base_path = os.path.join(tempfile.gettempdir(), "worktrees")
    parser.add_argument(
        "--base-path",
        type=str,
        default=default_base_path,
        help=f"Base path for worktrees (default: {default_base_path})",
    )
    parser.add_argument(
        "--branch-name",
        type=str,
        help="Custom branch name (default: pr-<number>)",
    )
    args = parser.parse_args()

    # Determine repository path
    repo = args.repo or find_repo_root()
    if not repo:
        result = {"status": "error", "error": "Not in a git repository"}
        print(json.dumps(result, indent=2))
        return 1

    repo = str(Path(repo).resolve())
    branch_name = args.branch_name or f"pr-{args.pr}"
    worktree_path = str(Path(args.base_path) / f"pr-{args.pr}")

    # Create base path if needed
    Path(args.base_path).mkdir(parents=True, exist_ok=True)

    # Check if worktree already exists
    if Path(worktree_path).exists():
        result = {
            "status": "exists",
            "worktree_path": worktree_path,
            "branch": branch_name,
            "message": "Worktree already exists",
        }
        print(json.dumps(result, indent=2))
        return 0

    # Fetch PR branch
    success, msg = fetch_pr_branch(repo, args.pr)
    if not success:
        result = {"status": "error", "error": msg}
        print(json.dumps(result, indent=2))
        return 1

    # Create worktree
    success, msg = create_worktree(repo, worktree_path, branch_name)
    if not success:
        result = {"status": "error", "error": msg}
        print(json.dumps(result, indent=2))
        return 1

    # Verify worktree
    success, msg = verify_worktree(worktree_path)
    if not success:
        result = {"status": "error", "error": msg}
        print(json.dumps(result, indent=2))
        return 1

    result = {
        "status": "created",
        "worktree_path": worktree_path,
        "branch": branch_name,
        "main_repo": repo,
        "pr_number": args.pr,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
