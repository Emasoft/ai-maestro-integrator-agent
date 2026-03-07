#!/usr/bin/env python3
"""
amia_post_issue_comment.py - Post a comment on a GitHub issue.

Posts a comment to an issue, with optional idempotency marker to prevent
duplicate comments when run multiple times.

Usage:
    amia_post_issue_comment.py --repo owner/repo --issue 123 --body "Comment text"
    amia_post_issue_comment.py --repo owner/repo --issue 123 --body "Status update" --marker "status-2024-01"

Output:
    JSON object with comment details to stdout.

Example output:
    {
        "comment_id": 12345,
        "url": "https://github.com/owner/repo/issues/123#issuecomment-12345",
        "created": true
    }

When using --marker, if a comment with that marker already exists, the script
returns created: false and provides the existing comment ID.

Exit codes (standardized):
    0 - Success, comment posted (or skipped if marker exists)
    1 - Invalid parameters (missing body, bad issue number)
    2 - Resource not found (repo or issue not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (comment with marker already exists)
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
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def get_issue_comments(repo: str, issue_number: int) -> list[dict[str, Any]]:
    """Get all comments on an issue."""
    success, output = run_gh_command([
        "issue", "view", str(issue_number),
        "--repo", repo,
        "--json", "comments"
    ])
    if not success:
        return []
    try:
        data = json.loads(output)
        return data.get("comments", [])
    except json.JSONDecodeError:
        return []


def find_comment_with_marker(repo: str, issue_number: int, marker: str) -> dict[str, Any] | None:
    """Find an existing comment containing the marker."""
    comments = get_issue_comments(repo, issue_number)
    marker_tag = f"<!-- {marker} -->"

    for comment in comments:
        body = comment.get("body", "")
        if marker_tag in body:
            return comment

    return None


def post_comment(
    repo: str,
    issue_number: int,
    body: str,
    marker: str | None = None
) -> dict[str, Any]:
    """Post a comment to an issue with optional idempotency marker."""
    # Check for existing comment with marker
    if marker:
        existing = find_comment_with_marker(repo, issue_number, marker)
        if existing:
            # Extract comment ID from URL or databaseId
            comment_url = existing.get("url", "")
            comment_id = existing.get("databaseId")

            # If no databaseId, try to extract from URL
            if not comment_id and "issuecomment-" in comment_url:
                try:
                    comment_id = int(comment_url.split("issuecomment-")[-1])
                except ValueError:
                    comment_id = None

            return {
                "comment_id": comment_id,
                "url": comment_url,
                "created": False,
                "message": "Comment with marker already exists"
            }

        # Add marker to body as HTML comment
        marker_tag = f"<!-- {marker} -->"
        body = f"{body}\n\n{marker_tag}"

    # Post the comment via stdin to avoid exposing body in process table
    cmd = ["gh", "issue", "comment", str(issue_number), "--repo", repo, "--body-file", "-"]
    result = subprocess.run(cmd, input=body, capture_output=True, text=True)
    success = result.returncode == 0
    output = result.stdout.strip() if success else result.stderr.strip()

    if not success:
        if "not logged in" in output.lower():
            return {"error": True, "message": output, "code": "AUTH_REQUIRED"}
        if "could not resolve" in output.lower():
            return {"error": True, "message": output, "code": "REPO_NOT_FOUND"}
        return {"error": True, "message": output, "code": "COMMENT_FAILED"}

    # Output is the comment URL
    comment_url = output

    # Extract comment ID from URL
    comment_id = None
    if "issuecomment-" in comment_url:
        try:
            comment_id = int(comment_url.split("issuecomment-")[-1])
        except ValueError:
            pass

    return {
        "comment_id": comment_id,
        "url": comment_url,
        "created": True
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Post a comment on a GitHub issue.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--body", required=True, help="Comment body (supports Markdown)")
    parser.add_argument(
        "--marker",
        help="Idempotency marker - prevents duplicate comments if run multiple times"
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    result = post_comment(
        repo=args.repo,
        issue_number=args.issue,
        body=args.body,
        marker=args.marker
    )

    write_output(result, "amia_post_issue_comment", args.output_file)

    # Check for idempotency skip (marker already exists)
    if result.get("created") is False and not result.get("error"):
        sys.exit(5)  # Idempotency skip - comment with marker already exists

    # Exit with appropriate error code based on error type
    if result.get("error"):
        error_code = result.get("code", "")

        if error_code == "REPO_NOT_FOUND":
            sys.exit(2)  # Resource not found
        elif error_code == "AUTH_REQUIRED":
            sys.exit(4)  # Not authenticated
        else:
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
