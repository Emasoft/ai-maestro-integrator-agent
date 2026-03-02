#!/usr/bin/env python3
"""
Get a single PR review thread by its GraphQL ID.

Usage:
    python3 amia_get_thread_by_id.py --thread-id PRRT_xxxxx

Output:
    JSON object with thread details including id, body, isResolved,
    isOutdated, path, line numbers, and all comments.

Example:
    python3 amia_get_thread_by_id.py --thread-id PRRT_kwDOxxxxxx

Note:
    Uses GraphQL node query for direct thread lookup.
    Requires read access to the repository.

Exit Codes:
    0 - Success
    1 - Invalid parameters
    2 - Thread not found
    3 - API error
    4 - Not authenticated
"""

import argparse
import json
import subprocess
import sys
from typing import Any


def run_graphql_with_variables(query: str, variables: dict[str, str]) -> dict[str, Any]:
    """Execute a GraphQL query using gh CLI with proper variable binding.

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
        # Check for authentication errors
        if "not logged in" in error_msg.lower() or "authentication" in error_msg.lower():
            raise RuntimeError(f"AUTH_ERROR: {error_msg}")
        raise RuntimeError(f"GraphQL query failed: {error_msg}")

    return json.loads(result.stdout)


def get_thread_by_id(thread_id: str) -> dict[str, Any]:
    """Retrieve detailed information about a review thread by its GraphQL ID."""
    # Use GraphQL node query for direct lookup with inline fragment
    query = """
    query($threadId: ID!) {
        node(id: $threadId) {
            ... on PullRequestReviewThread {
                id
                isResolved
                isOutdated
                path
                line
                startLine
                diffSide
                comments(first: 100) {
                    totalCount
                    nodes {
                        id
                        databaseId
                        body
                        author { login }
                        createdAt
                        updatedAt
                        isMinimized
                        minimizedReason
                    }
                }
            }
        }
    }
    """

    response = run_graphql_with_variables(query, {"threadId": thread_id})

    # Check for GraphQL errors
    if "errors" in response:
        error_messages = [e.get("message", "Unknown error") for e in response["errors"]]
        error_str = "; ".join(error_messages)
        if "could not resolve" in error_str.lower() or "not found" in error_str.lower():
            raise RuntimeError(f"NOT_FOUND: Thread {thread_id} not found")
        raise RuntimeError(f"Query failed: {error_str}")

    # Extract thread data
    thread = response.get("data", {}).get("node")

    # node() returns null if ID doesn't exist or isn't a PullRequestReviewThread
    if not thread or not thread.get("id"):
        raise RuntimeError(f"NOT_FOUND: Thread {thread_id} not found or is not a review thread")

    # Transform comments to consistent format
    comments = []
    comments_data = thread.get("comments", {})
    comment_nodes = comments_data.get("nodes", [])

    for comment in comment_nodes:
        author = comment.get("author")
        comments.append({
            "id": comment.get("databaseId"),
            "nodeId": comment.get("id"),
            "author": author.get("login") if author else None,
            "body": comment.get("body"),
            "createdAt": comment.get("createdAt"),
            "updatedAt": comment.get("updatedAt"),
            "isMinimized": comment.get("isMinimized"),
            "minimizedReason": comment.get("minimizedReason"),
        })

    # Build output
    return {
        "success": True,
        "threadId": thread.get("id"),
        "isResolved": thread.get("isResolved"),
        "isOutdated": thread.get("isOutdated"),
        "path": thread.get("path"),
        "line": thread.get("line"),
        "startLine": thread.get("startLine"),
        "diffSide": thread.get("diffSide"),
        "commentCount": comments_data.get("totalCount", 0),
        "comments": comments,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get a single PR review thread by its GraphQL ID."
    )
    parser.add_argument(
        "--thread-id",
        required=True,
        help="GraphQL node ID of the thread (PRRT_xxxxx)",
    )

    args = parser.parse_args()

    # Validate thread ID format
    if not args.thread_id.startswith("PRRT_"):
        print(
            json.dumps({
                "error": "Invalid thread ID format. Thread IDs should start with 'PRRT_'"
            }),
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        result = get_thread_by_id(args.thread_id)
        print(json.dumps(result, indent=2))

    except RuntimeError as e:
        error_str = str(e)
        error_output = {
            "error": error_str,
            "threadId": args.thread_id,
            "success": False,
        }
        print(json.dumps(error_output), file=sys.stderr)

        # Determine exit code based on error type
        if error_str.startswith("AUTH_ERROR"):
            sys.exit(4)
        elif error_str.startswith("NOT_FOUND"):
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
