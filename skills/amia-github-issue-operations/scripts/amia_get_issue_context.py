#!/usr/bin/env python3
"""
amia_get_issue_context.py - Retrieve comprehensive GitHub issue metadata.

Fetches issue details including title, body, state, labels, assignees,
milestone, comments count, and linked pull requests using the gh CLI.

Usage:
    amia_get_issue_context.py --repo owner/repo --issue 123
    amia_get_issue_context.py --repo owner/repo --issue 123 --include-comments

Output:
    JSON object with issue metadata to stdout.

Example output:
    {
        "number": 123,
        "title": "Bug: App crashes on startup",
        "state": "open",
        "labels": ["bug", "P1"],
        "assignees": ["developer1"],
        "milestone": "v2.0",
        "comments_count": 5,
        "linked_prs": [456, 789],
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-02T15:30:00Z"
    }

Exit codes (standardized):
    0 - Success, issue context returned
    1 - Invalid parameters (bad issue number, missing args)
    2 - Resource not found (issue does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def get_issue_context(repo: str, issue_number: int, include_comments: bool = False) -> dict[str, Any]:
    """Fetch comprehensive issue metadata from GitHub."""
    # Build the fields to fetch
    fields = [
        "number", "title", "body", "state", "labels", "assignees",
        "milestone", "comments", "createdAt", "updatedAt", "url"
    ]

    success, output = run_gh_command([
        "issue", "view", str(issue_number),
        "--repo", repo,
        "--json", ",".join(fields)
    ])

    if not success:
        return {"error": True, "message": output, "code": "ISSUE_NOT_FOUND"}

    try:
        issue_data = json.loads(output)
    except json.JSONDecodeError:
        return {"error": True, "message": "Failed to parse issue data", "code": "PARSE_ERROR"}

    # Extract and transform data
    result: dict[str, Any] = {
        "number": issue_data.get("number"),
        "title": issue_data.get("title"),
        "state": issue_data.get("state", "").lower(),
        "labels": [label.get("name") for label in issue_data.get("labels", [])],
        "assignees": [a.get("login") for a in issue_data.get("assignees", [])],
        "milestone": issue_data.get("milestone", {}).get("title") if issue_data.get("milestone") else None,
        "comments_count": len(issue_data.get("comments", [])),
        "created_at": issue_data.get("createdAt"),
        "updated_at": issue_data.get("updatedAt"),
        "url": issue_data.get("url")
    }

    # Find linked PRs from timeline events
    linked_prs = find_linked_prs(repo, issue_number)
    result["linked_prs"] = linked_prs

    # Optionally include comment details
    if include_comments:
        result["comments"] = [
            {
                "id": c.get("id"),
                "author": c.get("author", {}).get("login"),
                "body": c.get("body"),
                "created_at": c.get("createdAt")
            }
            for c in issue_data.get("comments", [])
        ]

    return result


def find_linked_prs(repo: str, issue_number: int) -> list[int]:
    """Find PRs that reference this issue."""
    success, output = run_gh_command([
        "pr", "list",
        "--repo", repo,
        "--search", str(issue_number),
        "--json", "number",
        "--limit", "50"
    ])

    if not success:
        return []

    try:
        prs = json.loads(output)
        return [pr["number"] for pr in prs]
    except (json.JSONDecodeError, KeyError):
        return []


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get comprehensive GitHub issue context and metadata."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/repo format"
    )
    parser.add_argument(
        "--issue",
        type=int,
        required=True,
        help="Issue number to fetch"
    )
    parser.add_argument(
        "--include-comments",
        action="store_true",
        help="Include full comment details in output"
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    result = get_issue_context(args.repo, args.issue, args.include_comments)
    write_output(result, "amia_get_issue_context", args.output_file)

    # Exit with appropriate error code based on error type
    if result.get("error"):
        error_code = result.get("code", "")
        error_msg = result.get("message", "").lower()

        if error_code == "ISSUE_NOT_FOUND" or "not found" in error_msg:
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg or "credentials" in error_msg:
            sys.exit(4)  # Not authenticated
        else:
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
