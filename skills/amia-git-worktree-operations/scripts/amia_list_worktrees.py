#!/usr/bin/env python3
"""
List all active git worktrees for a repository.

This script parses the output of 'git worktree list' and returns structured
information about each worktree including path, commit, and branch.

Usage:
    python amia_list_worktrees.py
    python amia_list_worktrees.py --repo-path /path/to/repo
    python amia_list_worktrees.py --format table
"""

import argparse
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


def find_repo_root(start_path: str | None = None) -> str | None:
    """Find the git repository root from start_path or current directory."""
    code, stdout, _ = run_git(["rev-parse", "--show-toplevel"], cwd=start_path)
    return stdout if code == 0 else None


def parse_worktree_line(line: str) -> dict[str, Any] | None:
    """Parse a single line from 'git worktree list' output."""
    if not line.strip():
        return None
    parts = line.split()
    if len(parts) < 2:
        return None

    worktree = {
        "path": parts[0],
        "commit": parts[1] if len(parts) > 1 else None,
        "branch": None,
        "is_bare": False,
        "is_detached": False,
    }

    # Check for branch in brackets or (bare) or (detached HEAD)
    for part in parts[2:]:
        if part.startswith("[") and part.endswith("]"):
            worktree["branch"] = part[1:-1]
        elif part == "(bare)":
            worktree["is_bare"] = True
        elif "detached" in part.lower():
            worktree["is_detached"] = True

    return worktree


def get_worktree_status(worktree_path: str) -> dict[str, Any]:
    """Get additional status info for a worktree."""
    status: dict[str, Any] = {
        "clean": True,
        "uncommitted_changes": 0,
        "untracked_files": 0,
    }

    code, stdout, _ = run_git(["status", "--porcelain"], cwd=worktree_path)
    if code == 0 and stdout:
        lines = stdout.split("\n")
        status["clean"] = False
        status["uncommitted_changes"] = sum(
            1 for line in lines if not line.startswith("??")
        )
        status["untracked_files"] = sum(1 for line in lines if line.startswith("??"))

    return status


def list_worktrees(
    repo_path: str, include_status: bool = False
) -> list[dict[str, Any]]:
    """List all worktrees for the repository."""
    code, stdout, _stderr = run_git(["worktree", "list"], cwd=repo_path)
    if code != 0:
        return []

    worktrees = []
    for line in stdout.split("\n"):
        wt = parse_worktree_line(line)
        if wt:
            if include_status:
                wt["status"] = get_worktree_status(wt["path"])
            worktrees.append(wt)

    return worktrees


def format_table(worktrees: list[dict[str, Any]]) -> str:
    """Format worktrees as a table."""
    if not worktrees:
        return "No worktrees found."

    lines = []
    lines.append("=" * 80)
    lines.append(f"{'Path':<40} {'Branch':<20} {'Commit':<12} {'Status':<8}")
    lines.append("-" * 80)

    for wt in worktrees:
        branch = wt.get("branch") or ("(detached)" if wt.get("is_detached") else "-")
        commit = (wt.get("commit") or "-")[:10]
        status = "clean" if wt.get("status", {}).get("clean", True) else "dirty"
        lines.append(f"{wt['path']:<40} {branch:<20} {commit:<12} {status:<8}")

    lines.append("=" * 80)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="List git worktrees")
    parser.add_argument("--repo-path", type=str, help="Path to main repository")
    parser.add_argument(
        "--format",
        choices=["json", "table"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--include-status",
        action="store_true",
        help="Include status info for each worktree",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = parser.parse_args()

    # Determine repository path
    repo = args.repo_path or find_repo_root()
    if not repo:
        result: dict[str, Any] = {"status": "error", "error": "Not in a git repository"}
        write_output(result, "amia_list_worktrees", args.output_file)
        return 1

    repo = str(Path(repo).resolve())
    worktrees = list_worktrees(repo, include_status=args.include_status)

    if args.format == "table":
        print(format_table(worktrees))
    else:
        result = {
            "status": "success",
            "main_repo": repo,
            "worktree_count": len(worktrees),
            "worktrees": worktrees,
        }
        write_output(result, "amia_list_worktrees", args.output_file)

    return 0


if __name__ == "__main__":
    sys.exit(main())
