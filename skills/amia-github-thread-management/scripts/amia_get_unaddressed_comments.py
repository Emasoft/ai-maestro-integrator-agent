#!/usr/bin/env python3
"""
Find review comments that have not received a reply from the PR author.

Usage:
    python3 amia_get_unaddressed_comments.py --owner OWNER --repo REPO --pr NUMBER

Output:
    JSON array of unaddressed comments with threadId, commentId, author, body, path, line.

Example:
    python3 amia_get_unaddressed_comments.py --owner octocat --repo Hello-World --pr 42

Note:
    A comment is considered "unaddressed" if:
    - It's in an unresolved thread
    - It's the root comment (first in thread)
    - The PR author has not replied to it
    - The comment is not minimized

Exit codes (standardized):
    0 - Success, comments returned (may be empty array)
    1 - Invalid parameters (bad PR number, missing args)
    2 - Resource not found (PR does not exist)
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


def run_graphql_with_variables(query: str, variables: dict[str, str]) -> dict[str, Any]:
    """Execute a GraphQL query/mutation using gh CLI with proper variable binding.

    Uses -f parameter binding to prevent GraphQL injection attacks.
    Variables are passed securely via subprocess arguments, NOT string interpolation.
    """
    # Build command with query and all variables as separate -f arguments
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for var_name, var_value in variables.items():
        cmd.extend(["-f", f"{var_name}={var_value}"])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        error_msg = result.stderr.strip() or "Unknown error"
        raise RuntimeError(f"GraphQL query failed: {error_msg}")

    return json.loads(result.stdout)


def get_unaddressed_comments(
    owner: str, repo: str, pr_number: int
) -> list[dict[str, Any]]:
    """Find comments in unresolved threads that PR author hasn't replied to."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    query = """
    query($owner: String!, $repo: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
          author {
            login
          }
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              path
              line
              comments(first: 100) {
                nodes {
                  id
                  body
                  createdAt
                  isMinimized
                  author {
                    login
                  }
                  replyTo {
                    id
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    response = run_graphql_with_variables(query, {
        "owner": owner,
        "repo": repo,
        "prNumber": str(pr_number),  # gh api graphql -f requires string values
    })

    pr_data = response.get("data", {}).get("repository", {}).get("pullRequest")
    if not pr_data:
        raise RuntimeError(f"Pull request #{pr_number} not found in {owner}/{repo}")

    pr_author = pr_data.get("author", {}).get("login", "")
    threads = pr_data.get("reviewThreads", {}).get("nodes", [])

    unaddressed = []

    for thread in threads:
        # Skip resolved threads
        if thread.get("isResolved", False):
            continue

        comments = thread.get("comments", {}).get("nodes", [])
        if not comments:
            continue

        # Get root comment (first in thread, no replyTo)
        root_comment = comments[0]

        # Skip if minimized
        if root_comment.get("isMinimized", False):
            continue

        # Skip if PR author made the root comment (self-review note)
        root_author = root_comment.get("author", {}).get("login", "")
        if root_author == pr_author:
            continue

        # Check if PR author has replied anywhere in thread
        pr_author_replied = False
        for comment in comments[1:]:  # Skip root comment
            comment_author = comment.get("author", {}).get("login", "")
            if comment_author == pr_author:
                pr_author_replied = True
                break

        if not pr_author_replied:
            unaddressed.append({
                "threadId": thread.get("id"),
                "commentId": root_comment.get("id"),
                "author": root_author,
                "body": root_comment.get("body"),
                "path": thread.get("path"),
                "line": thread.get("line"),
                "createdAt": root_comment.get("createdAt"),
            })

    return unaddressed


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Find review comments without replies from the PR author."
    )
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    try:
        comments = get_unaddressed_comments(args.owner, args.repo, args.pr)
        write_output({"unaddressed_comments": comments, "count": len(comments)}, "amia_get_unaddressed_comments", args.output_file)

    except RuntimeError as e:
        error_msg = str(e).lower()
        error_output = {"error": str(e)}

        # Determine appropriate exit code based on error type
        if "not found" in error_msg or "not exist" in error_msg:
            error_output["code"] = "RESOURCE_NOT_FOUND"
            write_output(error_output, "amia_get_unaddressed_comments", args.output_file)
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg or "credentials" in error_msg:
            error_output["code"] = "NOT_AUTHENTICATED"
            write_output(error_output, "amia_get_unaddressed_comments", args.output_file)
            sys.exit(4)  # Not authenticated
        else:
            error_output["code"] = "API_ERROR"
            write_output(error_output, "amia_get_unaddressed_comments", args.output_file)
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
