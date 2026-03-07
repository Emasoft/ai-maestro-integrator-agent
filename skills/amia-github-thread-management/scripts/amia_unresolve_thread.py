#!/usr/bin/env python3
"""
Unresolve a single GitHub PR review thread.

Usage:
    python3 amia_unresolve_thread.py --thread-id PRRT_xxxxx

    # Unresolve all resolved threads on a PR
    python3 amia_unresolve_thread.py --pr 123 --all

Output:
    JSON object with success status, threadId, and isResolved state.

Example:
    python3 amia_unresolve_thread.py --thread-id PRRT_kwDOxxxxxx

Note:
    This uses the GraphQL unresolveReviewThread mutation.
    You must have write access to the repository.

Exit Codes:
    0 - Success (thread unresolved or was already unresolved)
    1 - Invalid parameters (missing/malformed thread-id)
    2 - Thread/PR not found
    3 - API error
    4 - Not authenticated
    5 - Idempotency skip (thread already unresolved, treated as success)
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_graphql_with_variables(
    query: str, variables: dict[str, str | int]
) -> dict[str, Any]:
    """Execute a GraphQL query/mutation using gh CLI with proper variable binding.

    Uses -f parameter binding to prevent GraphQL injection attacks.
    Variables are passed securely via subprocess arguments, NOT string interpolation.
    """
    # Build command with query and all variables as separate -f arguments
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for var_name, var_value in variables.items():
        # Use -F for integers, -f for strings
        if isinstance(var_value, int):
            cmd.extend(["-F", f"{var_name}={var_value}"])
        else:
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
        if (
            "not logged in" in error_msg.lower()
            or "authentication" in error_msg.lower()
        ):
            raise RuntimeError(f"AUTH_ERROR: {error_msg}")
        raise RuntimeError(f"GraphQL mutation failed: {error_msg}")

    response: dict[str, Any] = json.loads(result.stdout)
    return response


def get_repo_info() -> tuple[str, str]:
    """Get owner and repo name from current directory."""
    result = subprocess.run(
        ["gh", "repo", "view", "--json", "owner,name"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError("Failed to get repo info. Are you in a git repository?")

    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def unresolve_thread(thread_id: str) -> dict[str, Any]:
    """Unresolve a review thread and return the result."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    mutation = """
    mutation($threadId: ID!) {
      unresolveReviewThread(input: {threadId: $threadId}) {
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
        error_str = "; ".join(error_messages)
        if "could not resolve" in error_str.lower() or "not found" in error_str.lower():
            raise RuntimeError(f"NOT_FOUND: {error_str}")
        raise RuntimeError(f"Unresolve failed: {error_str}")

    # Extract result
    unresolve_data = response.get("data", {}).get("unresolveReviewThread", {})
    thread_data = unresolve_data.get("thread", {})

    if not thread_data:
        raise RuntimeError(
            "NOT_FOUND: No thread data in response - thread may not exist"
        )

    is_resolved = thread_data.get("isResolved", True)

    return {
        "success": not is_resolved,  # Success if thread is now NOT resolved
        "threadId": thread_data.get("id"),
        "isResolved": is_resolved,
        "action": "unresolve",
    }


def get_resolved_threads(pr_number: int, owner: str, repo: str) -> list[dict[str, Any]]:
    """Get all resolved threads on a PR."""
    query = """
    query($owner: String!, $name: String!, $prNumber: Int!) {
        repository(owner: $owner, name: $name) {
            pullRequest(number: $prNumber) {
                reviewThreads(first: 100) {
                    nodes {
                        id
                        isResolved
                        comments(first: 1) {
                            nodes {
                                databaseId
                                author { login }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    response = run_graphql_with_variables(
        query,
        {
            "owner": owner,
            "name": repo,
            "prNumber": pr_number,
        },
    )

    if "errors" in response:
        error_messages = [e.get("message", "Unknown error") for e in response["errors"]]
        raise RuntimeError(f"Failed to query threads: {'; '.join(error_messages)}")

    pr_data = response.get("data", {}).get("repository", {}).get("pullRequest", {})
    if not pr_data:
        raise RuntimeError(f"NOT_FOUND: PR #{pr_number} not found")

    threads = pr_data.get("reviewThreads", {}).get("nodes", [])
    # Return only resolved threads
    return [t for t in threads if t.get("isResolved", False)]


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Unresolve a GitHub PR review thread (mark as open for discussion)."
    )
    parser.add_argument(
        "--thread-id",
        help="GraphQL node ID of the thread (PRRT_xxxxx)",
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number (use with --all to unresolve all resolved threads)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Unresolve all resolved threads on the PR",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    # Validate parameters
    if args.all:
        if not args.pr:
            write_output({"error": "--pr is required when using --all"}, "amia_unresolve_thread", args.output_file)
            sys.exit(1)
    else:
        if not args.thread_id:
            write_output(
                {"error": "--thread-id is required (or use --pr with --all)"},
                "amia_unresolve_thread", args.output_file,
            )
            sys.exit(1)
        # Validate thread ID format
        if not args.thread_id.startswith("PRRT_"):
            write_output(
                {
                    "error": "Invalid thread ID format. Thread IDs should start with 'PRRT_'"
                },
                "amia_unresolve_thread", args.output_file,
            )
            sys.exit(1)

    try:
        if args.all:
            # Unresolve all resolved threads on the PR
            owner, repo = get_repo_info()
            resolved_threads = get_resolved_threads(args.pr, owner, repo)

            if not resolved_threads:
                result = {
                    "success": True,
                    "totalResolved": 0,
                    "unresolved": 0,
                    "failed": 0,
                    "message": f"No resolved threads on PR #{args.pr} to unresolve",
                }
                write_output(result, "amia_unresolve_thread", args.output_file)
                sys.exit(0)

            unresolved_count = 0
            failed_count = 0
            results = []

            for thread in resolved_threads:
                thread_id = thread.get("id")
                if not thread_id or not isinstance(thread_id, str):
                    failed_count += 1
                    results.append(
                        {
                            "success": False,
                            "threadId": thread_id,
                            "error": "Missing or invalid thread ID",
                        }
                    )
                    continue
                try:
                    thread_result = unresolve_thread(thread_id)
                    if thread_result["success"]:
                        unresolved_count += 1
                    else:
                        failed_count += 1
                    results.append(thread_result)
                except RuntimeError as e:
                    failed_count += 1
                    results.append(
                        {
                            "success": False,
                            "threadId": thread_id,
                            "error": str(e),
                        }
                    )

            final_result = {
                "success": failed_count == 0,
                "totalResolved": len(resolved_threads),
                "unresolved": unresolved_count,
                "failed": failed_count,
                "threads": results,
            }
            write_output(final_result, "amia_unresolve_thread", args.output_file)
            sys.exit(0 if failed_count == 0 else 1)

        else:
            # Single thread unresolve
            result = unresolve_thread(args.thread_id)
            write_output(result, "amia_unresolve_thread", args.output_file)

            # Exit with error if unresolve didn't succeed
            if not result["success"]:
                sys.exit(1)

    except RuntimeError as e:
        error_str = str(e)
        error_output = {
            "error": error_str,
            "threadId": args.thread_id if args.thread_id else None,
            "pr": args.pr if args.pr else None,
            "success": False,
        }
        write_output(error_output, "amia_unresolve_thread", args.output_file)

        # Determine exit code based on error type
        if error_str.startswith("AUTH_ERROR"):
            sys.exit(4)
        elif error_str.startswith("NOT_FOUND"):
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
