#!/usr/bin/env python3
"""
Check if a GitHub PR is merged using GraphQL as the source of truth.

This script queries the GitHub GraphQL API to determine if a PR has been merged.
Unlike `gh pr view --json state`, GraphQL provides authoritative, real-time data.

Exit codes (standardized):
    0 - Success: PR is NOT merged (still open or closed without merge)
    1 - Invalid parameters (bad PR number, bad repo format)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip: PR IS already merged (merge commit exists)
    6 - Not mergeable (N/A for this script)

Note: Exit code 5 indicates the PR is merged. This allows scripts to check:
      - exit 0: PR needs merging
      - exit 5: PR already merged (idempotency - no action needed)

Usage:
    python amia_test_pr_merged.py --pr 123 --repo owner/repo
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_graphql_query(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    """Execute a GraphQL query using gh CLI."""
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if isinstance(value, int):
            cmd.extend(["-F", f"{key}={value}"])
        else:
            cmd.extend(["-f", f"{key}={value}"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"GraphQL query failed: {result.stderr}")
    return json.loads(result.stdout)


def check_pr_merged(owner: str, repo: str, pr_number: int) -> dict[str, Any]:
    """Check if PR is merged using GraphQL."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $number) {
                id
                number
                title
                state
                merged
                mergedAt
                mergeCommit {
                    oid
                    messageHeadline
                }
                headRefName
                baseRefName
            }
        }
    }
    """
    variables = {"owner": owner, "repo": repo, "number": pr_number}
    data = run_graphql_query(query, variables)

    pr_data = data.get("data", {}).get("repository", {}).get("pullRequest")
    if not pr_data:
        return {
            "error": True,
            "message": f"PR #{pr_number} not found in {owner}/{repo}",
            "merged": False,
            "merge_commit_sha": None,
        }

    merged = pr_data.get("merged", False)
    merge_commit = pr_data.get("mergeCommit", {}) or {}

    return {
        "error": False,
        "pr_number": pr_data.get("number"),
        "title": pr_data.get("title"),
        "state": pr_data.get("state"),
        "merged": merged,
        "merged_at": pr_data.get("mergedAt"),
        "merge_commit_sha": merge_commit.get("oid"),
        "merge_commit_message": merge_commit.get("messageHeadline"),
        "head_ref": pr_data.get("headRefName"),
        "base_ref": pr_data.get("baseRefName"),
    }


def parse_repo(repo_arg: str) -> tuple[str, str]:
    """Parse owner/repo string into (owner, repo) tuple."""
    if "/" not in repo_arg:
        raise ValueError(f"Invalid repo format: {repo_arg}. Expected owner/repo")
    parts = repo_arg.split("/", 1)
    return parts[0], parts[1]


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check if a GitHub PR is merged using GraphQL"
    )
    parser.add_argument(
        "--pr", type=int, required=True, help="PR number to check"
    )
    parser.add_argument(
        "--repo", type=str, required=True, help="Repository in owner/repo format"
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = parser.parse_args()

    try:
        owner, repo = parse_repo(args.repo)
        result = check_pr_merged(owner, repo, args.pr)
        write_output(result, "amia_test_pr_merged", args.output_file)

        if result.get("error"):
            # Check for specific error types
            msg = result.get("message", "").lower()
            if "not found" in msg:
                return 2  # Resource not found
            if "auth" in msg or "login" in msg:
                return 4  # Not authenticated
            return 3  # API error

        # Exit 5 if merged (idempotency - already done), 0 if not merged (success - needs action)
        return 5 if result.get("merged") else 0

    except ValueError as e:
        # Invalid parameters (bad repo format)
        error_result = {"error": True, "message": str(e), "code": "INVALID_PARAMS"}
        write_output(error_result, "amia_test_pr_merged", args.output_file)
        return 1  # Invalid parameters
    except Exception as e:
        error_result = {"error": True, "message": str(e), "code": "API_ERROR"}
        write_output(error_result, "amia_test_pr_merged", args.output_file)
        return 3  # API error


if __name__ == "__main__":
    sys.exit(main())
