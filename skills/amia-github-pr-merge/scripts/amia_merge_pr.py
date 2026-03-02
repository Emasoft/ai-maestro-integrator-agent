#!/usr/bin/env python3
"""
Merge a GitHub PR with the specified strategy.

Pre-verifies merge readiness before attempting merge.

Exit codes (standardized):
    0 - Success: Merge completed
    1 - Invalid parameters (bad PR number, invalid strategy)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip: PR already merged (no action needed)
    6 - Not mergeable (conflicts, closed, blocked)

Usage:
    python amia_merge_pr.py --pr 123 --repo owner/repo --strategy squash
    python amia_merge_pr.py --pr 123 --repo owner/repo --strategy merge --delete-branch
"""

import argparse
import json
import subprocess
import sys
from typing import Any


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


def get_pr_info(owner: str, repo: str, pr_number: int) -> dict[str, Any]:
    """Get PR ID and merge state."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
        repository(owner: $owner, name: $repo) {
            pullRequest(number: $number) {
                id
                state
                merged
                mergeable
                mergeStateStatus
                headRefName
            }
        }
    }
    """
    data = run_graphql_query(query, {"owner": owner, "repo": repo, "number": pr_number})
    return data.get("data", {}).get("repository", {}).get("pullRequest", {})


def merge_pr(
    owner: str,
    repo: str,
    pr_number: int,
    strategy: str,
    delete_branch: bool,
) -> dict[str, Any]:
    """Merge PR using gh CLI (simpler than GraphQL for merge)."""
    # First verify PR is ready
    pr_info = get_pr_info(owner, repo, pr_number)
    if not pr_info:
        return {"success": False, "error": "PR not found"}

    if pr_info.get("merged"):
        return {"success": False, "error": "PR already merged"}
    if pr_info.get("state") != "OPEN":
        return {"success": False, "error": "PR is not open"}

    merge_state = pr_info.get("mergeStateStatus")
    if merge_state in ("CONFLICTING", "DIRTY"):
        return {"success": False, "error": f"Cannot merge: {merge_state}"}

    # Build merge command
    cmd = ["gh", "pr", "merge", str(pr_number), "--repo", f"{owner}/{repo}"]

    strategy_map = {"merge": "--merge", "squash": "--squash", "rebase": "--rebase"}
    if strategy not in strategy_map:
        return {"success": False, "error": f"Invalid strategy: {strategy}"}
    cmd.append(strategy_map[strategy])

    if delete_branch:
        cmd.append("--delete-branch")

    # Execute merge
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip() or "Merge failed",
            "stdout": result.stdout.strip(),
        }

    # Verify merge completed
    pr_after = get_pr_info(owner, repo, pr_number)
    if pr_after.get("merged"):
        return {
            "success": True,
            "message": f"PR #{pr_number} merged successfully",
            "strategy": strategy,
            "branch_deleted": delete_branch,
        }

    return {
        "success": False,
        "error": "Merge command succeeded but PR not showing as merged",
        "stdout": result.stdout.strip(),
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Merge a GitHub PR")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", type=str, required=True, help="Repository (owner/repo)")
    parser.add_argument(
        "--strategy",
        type=str,
        choices=["merge", "squash", "rebase"],
        default="squash",
        help="Merge strategy (default: squash)",
    )
    parser.add_argument(
        "--delete-branch",
        action="store_true",
        help="Delete branch after merge",
    )
    args = parser.parse_args()

    try:
        if "/" not in args.repo:
            print(json.dumps({"success": False, "error": "Invalid repo format", "code": "INVALID_PARAMS"}, indent=2))
            return 1  # Invalid parameters
        owner, repo = args.repo.split("/", 1)
        result = merge_pr(owner, repo, args.pr, args.strategy, args.delete_branch)
        print(json.dumps(result, indent=2))

        if result.get("success"):
            return 0  # Success

        # Determine specific error type
        error_msg = result.get("error", "").lower()
        if "not found" in error_msg:
            return 2  # Resource not found
        if "already merged" in error_msg:
            return 5  # Idempotency skip - already done
        if "not open" in error_msg or "conflicting" in error_msg or "dirty" in error_msg or "cannot merge" in error_msg:
            return 6  # Not mergeable
        if "auth" in error_msg or "login" in error_msg:
            return 4  # Not authenticated
        return 3  # API error

    except ValueError as e:
        print(json.dumps({"success": False, "error": str(e), "code": "INVALID_PARAMS"}, indent=2))
        return 1  # Invalid parameters
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "code": "API_ERROR"}, indent=2))
        return 3  # API error


if __name__ == "__main__":
    sys.exit(main())
