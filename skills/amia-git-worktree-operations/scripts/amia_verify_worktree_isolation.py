#!/usr/bin/env python3
"""
Verify worktree isolation by detecting files written outside worktree boundaries.

This script checks for isolation violations where files may have been accidentally
written to the main repository or other worktrees instead of the assigned worktree.

Usage:
    python amia_verify_worktree_isolation.py --worktree-path /tmp/worktrees/pr-123
    python amia_verify_worktree_isolation.py -w /tmp/worktrees/pr-123 --main-repo /path/to/repo
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


def find_main_repo(worktree_path: str) -> str | None:
    """Find the main repository from a worktree path."""
    git_file = Path(worktree_path) / ".git"
    if not git_file.exists():
        return None

    if git_file.is_file():
        content = git_file.read_text(encoding="utf-8").strip()
        if content.startswith("gitdir:"):
            gitdir = content[7:].strip()
            main_git = Path(gitdir).parent.parent
            return str(main_git.parent)
    return None


def get_git_status(path: str) -> list[str]:
    """Get list of changed files in a git directory."""
    code, stdout, _ = run_git(["status", "--porcelain"], cwd=path)
    if code != 0 or not stdout:
        return []
    return [line.strip() for line in stdout.split("\n") if line.strip()]


def check_main_repo_contamination(
    main_repo: str, worktree_path: str
) -> list[dict[str, Any]]:
    """Check if main repo has unexpected changes (contamination)."""
    violations = []
    changes = get_git_status(main_repo)

    for change in changes:
        # Parse status line (e.g., "M  file.py" or "?? new_file.py")
        if len(change) < 3:
            continue
        status = change[:2].strip()
        filepath = change[3:].strip()

        violations.append(
            {
                "type": "main_repo_contamination",
                "file": filepath,
                "status": status,
                "location": main_repo,
                "expected_location": worktree_path,
            }
        )

    return violations


def check_worktree_status(worktree_path: str) -> dict[str, Any]:
    """Check the status of the worktree itself."""
    status: dict[str, Any] = {
        "path": worktree_path,
        "exists": Path(worktree_path).exists(),
        "is_git_worktree": (Path(worktree_path) / ".git").exists(),
        "uncommitted_changes": [],
        "untracked_files": [],
    }

    if not status["exists"] or not status["is_git_worktree"]:
        return status

    changes = get_git_status(worktree_path)
    for change in changes:
        if len(change) < 3:
            continue
        status_code = change[:2]
        filepath = change[3:].strip()

        if status_code.startswith("??"):
            status["untracked_files"].append(filepath)
        else:
            status["uncommitted_changes"].append(
                {"status": status_code.strip(), "file": filepath}
            )

    return status


def find_other_worktrees(main_repo: str, exclude_path: str) -> list[str]:
    """Find other worktrees for the same repository."""
    code, stdout, _ = run_git(["worktree", "list", "--porcelain"], cwd=main_repo)
    if code != 0:
        return []

    worktrees = []
    current_wt = None

    for line in stdout.split("\n"):
        if line.startswith("worktree "):
            current_wt = line[9:].strip()
            if current_wt != exclude_path and current_wt != main_repo:
                worktrees.append(current_wt)

    return worktrees


def check_cross_worktree_contamination(
    worktrees: list[str], _current_worktree: str
) -> list[dict[str, Any]]:
    """Check if other worktrees have unexpected changes."""
    violations = []

    for wt in worktrees:
        changes = get_git_status(wt)
        if changes:
            violations.append(
                {
                    "type": "cross_worktree_contamination",
                    "worktree": wt,
                    "changes_count": len(changes),
                    "note": "Other worktree has uncommitted changes (may be unrelated)",
                }
            )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify worktree isolation")
    parser.add_argument(
        "-w",
        "--worktree-path",
        type=str,
        required=True,
        help="Path to the worktree to verify",
    )
    parser.add_argument(
        "--main-repo",
        type=str,
        help="Path to main repository (auto-detected if not provided)",
    )
    parser.add_argument(
        "--check-other-worktrees",
        action="store_true",
        help="Also check other worktrees for contamination",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = parser.parse_args()

    worktree_path = str(Path(args.worktree_path).resolve())

    # Check worktree exists
    if not Path(worktree_path).exists():
        result: dict[str, Any] = {
            "status": "error",
            "error": f"Worktree path does not exist: {worktree_path}",
        }
        write_output(result, "amia_verify_worktree_isolation", args.output_file)
        return 1

    # Find main repo
    main_repo = args.main_repo
    if not main_repo:
        main_repo = find_main_repo(worktree_path)

    if not main_repo:
        result = {
            "status": "error",
            "error": "Could not determine main repository",
        }
        write_output(result, "amia_verify_worktree_isolation", args.output_file)
        return 1

    main_repo = str(Path(main_repo).resolve())

    # Collect all violations
    violations = []
    warnings = []

    # Check worktree status
    wt_status = check_worktree_status(worktree_path)
    if wt_status["uncommitted_changes"]:
        warnings.append(
            f"Worktree has {len(wt_status['uncommitted_changes'])} uncommitted changes"
        )
    if wt_status["untracked_files"]:
        warnings.append(
            f"Worktree has {len(wt_status['untracked_files'])} untracked files"
        )

    # Check main repo contamination
    main_violations = check_main_repo_contamination(main_repo, worktree_path)
    violations.extend(main_violations)

    # Check other worktrees if requested
    if args.check_other_worktrees:
        other_wts = find_other_worktrees(main_repo, worktree_path)
        cross_violations = check_cross_worktree_contamination(other_wts, worktree_path)
        violations.extend(cross_violations)

    # Build result
    result_status = "violation" if violations else "clean"
    result = {
        "status": result_status,
        "worktree_path": worktree_path,
        "main_repo": main_repo,
        "worktree_status": wt_status,
        "violations": violations,
        "warnings": warnings,
    }

    write_output(result, "amia_verify_worktree_isolation", args.output_file)
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
