#!/usr/bin/env python3
"""
Reply to a GitHub PR review thread.

Usage:
    python3 amia_reply_to_thread.py --thread-id PRRT_xxxxx --body "Reply message"
    python3 amia_reply_to_thread.py --thread-id PRRT_xxxxx --body "Fixed" --and-resolve

Output:
    JSON object with success, commentId, and resolved status (if --and-resolve used).

IMPORTANT:
    Replying to a thread does NOT automatically resolve it!
    Use --and-resolve flag to both reply AND resolve in sequence.

Example:
    python3 amia_reply_to_thread.py --thread-id PRRT_kwDOxxx --body "Good catch, fixed!"
    python3 amia_reply_to_thread.py --thread-id PRRT_kwDOxxx --body "Done" --and-resolve

Exit codes (standardized):
    0 - Success, reply posted (and optionally resolved)
    1 - Invalid parameters (bad thread ID format)
    2 - Resource not found (thread does not exist)
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
        raise RuntimeError(f"GraphQL mutation failed: {error_msg}")

    return json.loads(result.stdout)


def get_pr_review_id_for_thread(thread_id: str) -> str:
    """Get the pull request review ID needed for adding a reply comment."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    query = """
    query($nodeId: ID!) {
      node(id: $nodeId) {
        ... on PullRequestReviewThread {
          comments(first: 1) {
            nodes {
              pullRequestReview {
                id
              }
            }
          }
        }
      }
    }
    """

    response = run_graphql_with_variables(query, {"nodeId": thread_id})
    comments = response.get("data", {}).get("node", {}).get("comments", {}).get("nodes", [])

    if not comments:
        raise RuntimeError("Could not find comments in thread")

    review = comments[0].get("pullRequestReview")
    if not review:
        raise RuntimeError("Could not find pull request review for thread")

    return review["id"]


def reply_to_thread(thread_id: str, body: str) -> dict[str, Any]:
    """Add a reply comment to a review thread."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    mutation = """
    mutation($threadId: ID!, $body: String!) {
      addPullRequestReviewThreadReply(input: {
        pullRequestReviewThreadId: $threadId
        body: $body
      }) {
        comment {
          id
          body
        }
      }
    }
    """

    response = run_graphql_with_variables(mutation, {"threadId": thread_id, "body": body})

    if "errors" in response:
        error_messages = [e.get("message", "Unknown error") for e in response["errors"]]
        raise RuntimeError(f"Reply failed: {'; '.join(error_messages)}")

    comment_data = (
        response.get("data", {})
        .get("addPullRequestReviewThreadReply", {})
        .get("comment", {})
    )

    if not comment_data:
        raise RuntimeError("No comment data in response")

    return {
        "success": True,
        "commentId": comment_data.get("id"),
        "body": comment_data.get("body"),
    }


def resolve_thread(thread_id: str) -> bool:
    """Resolve a thread and return success status."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          isResolved
        }
      }
    }
    """

    response = run_graphql_with_variables(mutation, {"threadId": thread_id})
    thread_data = (
        response.get("data", {}).get("resolveReviewThread", {}).get("thread", {})
    )

    return thread_data.get("isResolved", False)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Reply to a GitHub PR review thread."
    )
    parser.add_argument(
        "--thread-id",
        required=True,
        help="GraphQL node ID of the thread (PRRT_xxxxx)",
    )
    parser.add_argument(
        "--body",
        required=True,
        help="Reply message body",
    )
    parser.add_argument(
        "--and-resolve",
        action="store_true",
        help="Also resolve the thread after replying",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if not args.thread_id.startswith("PRRT_"):
        write_output({
            "error": "Invalid thread ID format. Thread IDs should start with 'PRRT_'",
            "code": "INVALID_PARAMS"
        }, "amia_reply_to_thread", args.output_file)
        sys.exit(1)  # Invalid parameters

    try:
        result = reply_to_thread(args.thread_id, args.body)

        if args.and_resolve:
            resolved = resolve_thread(args.thread_id)
            result["resolved"] = resolved
            if not resolved:
                result["warning"] = "Reply succeeded but resolution failed"

        write_output(result, "amia_reply_to_thread", args.output_file)

    except RuntimeError as e:
        error_msg = str(e).lower()
        error_output = {"error": str(e), "success": False}

        # Determine appropriate exit code based on error type
        if "not found" in error_msg or "not exist" in error_msg:
            error_output["code"] = "RESOURCE_NOT_FOUND"
            write_output(error_output, "amia_reply_to_thread", args.output_file)
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg or "credentials" in error_msg:
            error_output["code"] = "NOT_AUTHENTICATED"
            write_output(error_output, "amia_reply_to_thread", args.output_file)
            sys.exit(4)  # Not authenticated
        else:
            error_output["code"] = "API_ERROR"
            write_output(error_output, "amia_reply_to_thread", args.output_file)
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
