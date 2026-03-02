#!/usr/bin/env python3
"""
amia_set_issue_milestone.py - Assign a milestone to a GitHub issue.

Sets the milestone on an issue, optionally creating the milestone if it
doesn't exist.

Usage:
    amia_set_issue_milestone.py --repo owner/repo --issue 123 --milestone "v2.0"
    amia_set_issue_milestone.py --repo owner/repo --issue 123 --milestone "v3.0" --create-if-missing
    amia_set_issue_milestone.py --repo owner/repo --issue 123 --clear

Output:
    JSON object with milestone assignment result to stdout.

Example output:
    {
        "issue": 123,
        "milestone": "v2.0",
        "milestone_number": 5,
        "created": false
    }

Exit codes (standardized):
    0 - Success, milestone set/cleared
    1 - Invalid parameters (missing --milestone or --clear)
    2 - Resource not found (milestone not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import subprocess
import sys
from typing import Any


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def get_milestone_by_title(repo: str, title: str) -> dict[str, Any] | None:
    """Find a milestone by its title."""
    escaped_title = title.replace("\\", "\\\\").replace('"', '\\"')
    success, output = run_gh_command([
        "api", f"repos/{repo}/milestones",
        "--jq", f'.[] | select(.title=="{escaped_title}")'
    ])
    if not success or not output:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def create_milestone(repo: str, title: str, description: str | None = None) -> dict[str, Any] | None:
    """Create a new milestone."""
    cmd = ["api", f"repos/{repo}/milestones", "--method", "POST", "-f", f"title={title}"]
    if description:
        cmd.extend(["-f", f"description={description}"])

    success, output = run_gh_command(cmd)
    if not success:
        return None
    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return None


def clear_issue_milestone(repo: str, issue_number: int) -> dict[str, Any]:
    """Remove milestone from an issue."""
    success, output = run_gh_command([
        "api", f"repos/{repo}/issues/{issue_number}",
        "--method", "PATCH",
        "-F", "milestone=null"
    ])
    if not success:
        return {"error": True, "message": output, "code": "CLEAR_FAILED"}

    return {"issue": issue_number, "milestone": None, "cleared": True}


def set_issue_milestone(
    repo: str,
    issue_number: int,
    milestone_title: str,
    create_if_missing: bool = False
) -> dict[str, Any]:
    """Assign a milestone to an issue."""
    created = False

    # Find existing milestone
    milestone = get_milestone_by_title(repo, milestone_title)

    if not milestone:
        if create_if_missing:
            milestone = create_milestone(repo, milestone_title)
            if not milestone:
                return {
                    "error": True,
                    "message": f"Failed to create milestone: {milestone_title}",
                    "code": "MILESTONE_CREATE_FAILED"
                }
            created = True
        else:
            return {
                "error": True,
                "message": f"Milestone not found: {milestone_title}",
                "code": "MILESTONE_NOT_FOUND"
            }

    milestone_number = milestone.get("number")

    # Assign milestone to issue using gh issue edit
    success, output = run_gh_command([
        "issue", "edit", str(issue_number),
        "--repo", repo,
        "--milestone", milestone_title
    ])

    if not success:
        return {"error": True, "message": output, "code": "ASSIGN_FAILED"}

    return {
        "issue": issue_number,
        "milestone": milestone_title,
        "milestone_number": milestone_number,
        "created": created
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Assign a milestone to a GitHub issue.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--milestone", help="Milestone title to assign")
    parser.add_argument("--create-if-missing", action="store_true", help="Create milestone if it doesn't exist")
    parser.add_argument("--clear", action="store_true", help="Remove milestone from issue")

    args = parser.parse_args()

    if args.clear:
        result = clear_issue_milestone(args.repo, args.issue)
    elif args.milestone:
        result = set_issue_milestone(
            repo=args.repo,
            issue_number=args.issue,
            milestone_title=args.milestone,
            create_if_missing=args.create_if_missing
        )
    else:
        result = {"error": True, "message": "Must specify --milestone or --clear", "code": "INVALID_ARGS"}

    print(json.dumps(result, indent=2))

    # Exit with appropriate error code based on error type
    if result.get("error"):
        error_code = result.get("code", "")
        error_msg = result.get("message", "").lower()

        if error_code == "INVALID_ARGS":
            sys.exit(1)  # Invalid parameters
        elif error_code == "MILESTONE_NOT_FOUND" or "not found" in error_msg:
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg:
            sys.exit(4)  # Not authenticated
        else:
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
