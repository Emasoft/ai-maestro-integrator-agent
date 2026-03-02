#!/usr/bin/env python3
"""
Get all review threads from a GitHub Pull Request.

Usage:
    python3 amia_get_review_threads.py --owner OWNER --repo REPO --pr NUMBER [--unresolved-only]

Output:
    JSON array of thread objects with id, isResolved, path, line, body (first comment).

Example:
    python3 amia_get_review_threads.py --owner octocat --repo Hello-World --pr 42
    python3 amia_get_review_threads.py --owner octocat --repo Hello-World --pr 42 --unresolved-only

Exit codes (standardized):
    0 - Success, threads returned (may be empty array)
    1 - Invalid parameters (bad PR number, missing args)
    2 - Resource not found (PR does not exist)
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


def get_review_threads(owner: str, repo: str, pr_number: int) -> list[dict[str, Any]]:
    """Fetch all review threads for a pull request."""
    # Use GraphQL variables for secure parameter binding (prevents injection)
    query = """
    query($owner: String!, $repo: String!, $prNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $prNumber) {
          reviewThreads(first: 100) {
            nodes {
              id
              isResolved
              isOutdated
              path
              line
              diffSide
              comments(first: 1) {
                nodes {
                  body
                  author {
                    login
                  }
                  createdAt
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

    # Navigate to threads in response
    pr_data = response.get("data", {}).get("repository", {}).get("pullRequest")
    if not pr_data:
        raise RuntimeError(f"Pull request #{pr_number} not found in {owner}/{repo}")

    threads_data = pr_data.get("reviewThreads", {}).get("nodes", [])

    # Transform to simplified output format
    threads = []
    for thread in threads_data:
        first_comment = None
        comments = thread.get("comments", {}).get("nodes", [])
        if comments:
            first_comment = comments[0]

        threads.append({
            "id": thread.get("id"),
            "isResolved": thread.get("isResolved", False),
            "isOutdated": thread.get("isOutdated", False),
            "path": thread.get("path"),
            "line": thread.get("line"),
            "diffSide": thread.get("diffSide"),
            "body": first_comment.get("body") if first_comment else None,
            "author": first_comment.get("author", {}).get("login") if first_comment else None,
            "createdAt": first_comment.get("createdAt") if first_comment else None,
        })

    return threads


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Get all review threads from a GitHub Pull Request."
    )
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    parser.add_argument(
        "--unresolved-only",
        action="store_true",
        help="Only return unresolved threads",
    )

    args = parser.parse_args()

    try:
        threads = get_review_threads(args.owner, args.repo, args.pr)

        # Filter if requested
        if args.unresolved_only:
            threads = [t for t in threads if not t["isResolved"]]

        # Output as JSON
        print(json.dumps(threads, indent=2))

    except RuntimeError as e:
        error_msg = str(e).lower()
        error_output = {"error": str(e)}

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
