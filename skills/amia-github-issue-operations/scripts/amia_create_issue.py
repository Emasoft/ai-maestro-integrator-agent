#!/usr/bin/env python3
"""
amia_create_issue.py - Create a new GitHub issue.

Creates a new issue in the specified repository with optional labels,
assignee, and milestone using the gh CLI.

Usage:
    amia_create_issue.py --repo owner/repo --title "Issue title"
    amia_create_issue.py --repo owner/repo --title "Bug" --body "Description" --labels "bug,P1"
    amia_create_issue.py --repo owner/repo --title "Task" --assignee "username" --milestone "v2.0"

Output:
    JSON object with created issue number and URL to stdout.

Example output:
    {
        "number": 124,
        "url": "https://github.com/owner/repo/issues/124"
    }

Exit codes (standardized):
    0 - Success, issue created
    1 - Invalid parameters (missing title, bad repo format)
    2 - Resource not found (repo, milestone not found)
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
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def create_issue(
    repo: str,
    title: str,
    body: str | None = None,
    labels: list[str] | None = None,
    assignee: str | None = None,
    milestone: str | None = None
) -> dict[str, Any]:
    """Create a new GitHub issue with the specified parameters."""
    # Build the command
    cmd = ["issue", "create", "--repo", repo, "--title", title]

    if body:
        cmd.extend(["--body", body])

    if labels:
        cmd.extend(["--label", ",".join(labels)])

    if assignee:
        cmd.extend(["--assignee", assignee])

    if milestone:
        cmd.extend(["--milestone", milestone])

    success, output = run_gh_command(cmd)

    if not success:
        # Check for specific error types
        if "Could not resolve" in output:
            return {"error": True, "message": output, "code": "REPO_NOT_FOUND"}
        if "not logged in" in output.lower():
            return {"error": True, "message": output, "code": "AUTH_REQUIRED"}
        if "milestone" in output.lower():
            return {"error": True, "message": output, "code": "MILESTONE_NOT_FOUND"}
        return {"error": True, "message": output, "code": "CREATE_FAILED"}

    # Output is the issue URL
    issue_url = output

    # Extract issue number from URL
    try:
        issue_number = int(issue_url.rstrip("/").split("/")[-1])
    except (ValueError, IndexError):
        issue_number = None

    return {
        "number": issue_number,
        "url": issue_url
    }


def parse_labels(labels_str: str | None) -> list[str] | None:
    """Parse comma-separated labels string into list."""
    if not labels_str:
        return None
    return [label.strip() for label in labels_str.split(",") if label.strip()]


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new GitHub issue."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/repo format"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="Issue title"
    )
    parser.add_argument(
        "--body",
        help="Issue body/description (supports Markdown)"
    )
    parser.add_argument(
        "--labels",
        help="Comma-separated list of labels to apply"
    )
    parser.add_argument(
        "--assignee",
        help="GitHub username to assign the issue to"
    )
    parser.add_argument(
        "--milestone",
        help="Milestone title to assign the issue to"
    )

    args = parser.parse_args()

    labels = parse_labels(args.labels)

    result = create_issue(
        repo=args.repo,
        title=args.title,
        body=args.body,
        labels=labels,
        assignee=args.assignee,
        milestone=args.milestone
    )

    print(json.dumps(result, indent=2))

    # Exit with appropriate error code based on error type
    if result.get("error"):
        error_code = result.get("code", "")

        if error_code == "REPO_NOT_FOUND" or error_code == "MILESTONE_NOT_FOUND":
            sys.exit(2)  # Resource not found
        elif error_code == "AUTH_REQUIRED":
            sys.exit(4)  # Not authenticated
        else:
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
