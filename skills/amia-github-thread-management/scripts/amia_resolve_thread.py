#!/usr/bin/env python3
"""
Resolve a single GitHub PR review thread.

Usage:
    python3 amia_resolve_thread.py --thread-id PRRT_xxxxx

Output:
    JSON object with success status, threadId, and isResolved state.

Example:
    python3 amia_resolve_thread.py --thread-id PRRT_kwDOxxxxxx

Note:
    This uses the GraphQL resolveReviewThread mutation.
    You must have write access to the repository.

Exit codes (standardized):
    0 - Success, thread resolved
    1 - Invalid parameters (bad thread ID format)
    2 - Resource not found (thread does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (thread already resolved)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import subprocess
import sys
from typing import Any


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


def resolve_thread(thread_id: str) -> dict[str, Any]:
    """Resolve a review thread and return the result."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    mutation = """
    mutation($threadId: ID!) {
      resolveReviewThread(input: {threadId: $threadId}) {
        thread {
          id
          isResolved
        }
      }
    }
    """

    response = run_graphql_with_variables(mutation, {"threadId": thread_id})

    # Check for GraphQL errors
    if "errors" in response:
        error_messages = [e.get("message", "Unknown error") for e in response["errors"]]
        raise RuntimeError(f"Resolution failed: {'; '.join(error_messages)}")

    # Extract result
    resolve_data = response.get("data", {}).get("resolveReviewThread", {})
    thread_data = resolve_data.get("thread", {})

    if not thread_data:
        raise RuntimeError("No thread data in response - thread may not exist")

    is_resolved = thread_data.get("isResolved", False)

    return {
        "success": is_resolved,
        "threadId": thread_data.get("id"),
        "isResolved": is_resolved,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Resolve a single GitHub PR review thread."
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
                "error": "Invalid thread ID format. Thread IDs should start with 'PRRT_'",
                "code": "INVALID_PARAMS"
            }),
            file=sys.stderr,
        )
        sys.exit(1)  # Invalid parameters

    try:
        result = resolve_thread(args.thread_id)
        print(json.dumps(result, indent=2))

        # Exit with error if resolution didn't succeed
        if not result["success"]:
            sys.exit(3)  # API error - resolution failed

    except RuntimeError as e:
        error_msg = str(e).lower()
        error_output = {"error": str(e), "threadId": args.thread_id, "success": False}

        # Determine appropriate exit code based on error type
        if "not found" in error_msg or "not exist" in error_msg:
            error_output["code"] = "RESOURCE_NOT_FOUND"
            print(json.dumps(error_output), file=sys.stderr)
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg or "credentials" in error_msg:
            error_output["code"] = "NOT_AUTHENTICATED"
            print(json.dumps(error_output), file=sys.stderr)
            sys.exit(4)  # Not authenticated
        else:
            error_output["code"] = "API_ERROR"
            print(json.dumps(error_output), file=sys.stderr)
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
