#!/usr/bin/env python3
"""
Assign users to a GitHub Issue.

Usage:
    python3 amia_set_issue_assignee.py --issue 123 --assignees user1 user2
    python3 amia_set_issue_assignee.py --issue 123 --assignees @me
    python3 amia_set_issue_assignee.py --repo owner/repo --issue 123 --assignees user1

Output:
    JSON object with success status and list of applied/failed assignees.

Features:
    - Adds one or more assignees to an issue
    - Supports @me shorthand for current authenticated user
    - Supports --remove to remove assignees instead of adding

Example:
    python3 amia_set_issue_assignee.py --issue 42 --assignees alice bob
    python3 amia_set_issue_assignee.py --issue 42 --assignees @me --remove

Exit Codes:
    0 - Success (all assignees applied)
    1 - Invalid parameters
    2 - Issue not found
    3 - API error (partial or complete failure)
    4 - Not authenticated
"""

import argparse
import json
import subprocess
import sys
from typing import Any


def check_gh_auth() -> bool:
    """Verify gh CLI is authenticated."""
    result = subprocess.run(
        ["gh", "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def get_repo_info() -> str:
    """Get owner/repo from current directory."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to get repo info. Are you in a git repository?")

    data = json.loads(result.stdout)
    return f"{data['owner']['login']}/{data['name']}"


def modify_assignee(issue: int, repo: str, assignee: str, remove: bool = False) -> tuple[bool, str]:
    """Add or remove a single assignee from an issue.

    Returns tuple of (success, error_message).
    """
    action = "--remove-assignee" if remove else "--add-assignee"

    result = subprocess.run(
        ["gh", "issue", "edit", str(issue), "--repo", repo, action, assignee],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 0:
        return True, ""
    else:
        error_msg = result.stderr.strip() or "Unknown error"
        return False, error_msg


def set_issue_assignees(
    issue: int,
    assignees: list[str],
    repo: str | None = None,
    remove: bool = False,
) -> dict[str, Any]:
    """Modify assignees on an issue.

    Args:
        issue: Issue number
        assignees: List of GitHub usernames (supports @me)
        repo: Optional owner/repo string. Inferred from git if not provided.
        remove: If True, remove assignees instead of adding

    Returns:
        Dict with success status and lists of applied/failed assignees
    """
    # Get repo if not provided
    if not repo:
        repo = get_repo_info()

    # Handle empty assignees list
    if not assignees:
        return {
            "success": True,
            "issue": issue,
            "repo": repo,
            "applied": [],
            "failed": [],
            "totalApplied": 0,
            "action": "remove" if remove else "add",
            "message": "No assignees specified",
        }

    applied = []
    failed = []
    errors = {}

    for assignee in assignees:
        success, error = modify_assignee(issue, repo, assignee, remove)
        if success:
            applied.append(assignee)
        else:
            failed.append(assignee)
            errors[assignee] = error
            # Check for "not found" errors to detect issue not existing
            if "could not find" in error.lower() or "not found" in error.lower():
                if "issue" in error.lower():
                    raise RuntimeError(f"NOT_FOUND: Issue #{issue} not found in {repo}")

    action_verb = "removed from" if remove else "assigned to"

    return {
        "success": len(failed) == 0,
        "issue": issue,
        "repo": repo,
        "applied": applied,
        "failed": failed,
        "errors": errors if errors else None,
        "totalApplied": len(applied),
        "action": "remove" if remove else "add",
        "message": f"{len(applied)} user(s) {action_verb} issue #{issue}" if applied else None,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Assign users to a GitHub Issue."
    )
    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="Issue number",
    )
    parser.add_argument(
        "--assignees",
        nargs="+",
        required=True,
        help="GitHub usernames to assign (use @me for current user)",
    )
    parser.add_argument(
        "--repo",
        help="Repository in owner/repo format. Inferred from git if not provided.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove assignees instead of adding",
    )

    args = parser.parse_args()

    # Check authentication first
    if not check_gh_auth():
        print(
            json.dumps({"error": "Not authenticated. Run 'gh auth login' first."}),
            file=sys.stderr,
        )
        sys.exit(4)

    try:
        result = set_issue_assignees(
            issue=args.issue,
            assignees=args.assignees,
            repo=args.repo,
            remove=args.remove,
        )
        print(json.dumps(result, indent=2))

        if not result["success"]:
            sys.exit(3)

    except RuntimeError as e:
        error_str = str(e)
        error_output = {
            "error": error_str,
            "issue": args.issue,
            "success": False,
        }
        print(json.dumps(error_output), file=sys.stderr)

        # Determine exit code based on error type
        if error_str.startswith("NOT_FOUND"):
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
