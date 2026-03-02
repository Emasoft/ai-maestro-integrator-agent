#!/usr/bin/env python3
"""Enable or disable auto-merge on a GitHub PR using GraphQL.

Exit codes (standardized):
    0 - Success: Auto-merge enabled/disabled
    1 - Invalid parameters (bad PR number, bad repo format)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip: PR already merged (no action needed)
    6 - Not mergeable (PR closed, cannot enable auto-merge)

Usage:
    python amia_set_auto_merge.py --pr 123 --repo owner/repo --enable --merge-method SQUASH
    python amia_set_auto_merge.py --pr 123 --repo owner/repo --disable
"""
import argparse
import json
import subprocess
import sys
from typing import Any

def run_gql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        cmd.extend(["-F" if isinstance(v, int) else "-f", f"{k}={v}"])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"GraphQL failed: {r.stderr}")
    return json.loads(r.stdout)

def get_pr_id(owner: str, repo: str, pr_num: int) -> tuple[str, dict]:
    query = """query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $number) {
          id state merged viewerCanEnableAutoMerge viewerCanDisableAutoMerge
          autoMergeRequest { enabledAt mergeMethod }
        }
      }
    }"""
    data = run_gql(query, {"owner": owner, "repo": repo, "number": pr_num})
    pr = data.get("data", {}).get("repository", {}).get("pullRequest", {})
    return pr.get("id", ""), pr

def enable_auto_merge(pr_id: str, method: str) -> dict:
    mutation = """mutation($prId: ID!, $method: PullRequestMergeMethod!) {
      enablePullRequestAutoMerge(input: {pullRequestId: $prId, mergeMethod: $method}) {
        pullRequest { autoMergeRequest { enabledAt mergeMethod } }
      }
    }"""
    data = run_gql(mutation, {"prId": pr_id, "method": method})
    if "errors" in data:
        return {"success": False, "error": data["errors"][0].get("message", "Error")}
    am = data.get("data", {}).get("enablePullRequestAutoMerge", {}).get("pullRequest", {}).get("autoMergeRequest", {})
    if am and am.get("enabledAt"):
        return {"success": True, "message": "Auto-merge enabled", "merge_method": am.get("mergeMethod")}
    return {"success": False, "error": "Auto-merge not enabled (check repo settings)"}

def disable_auto_merge(pr_id: str) -> dict:
    mutation = """mutation($prId: ID!) {
      disablePullRequestAutoMerge(input: {pullRequestId: $prId}) {
        pullRequest { autoMergeRequest { enabledAt } }
      }
    }"""
    data = run_gql(mutation, {"prId": pr_id})
    if "errors" in data:
        return {"success": False, "error": data["errors"][0].get("message", "Error")}
    am = data.get("data", {}).get("disablePullRequestAutoMerge", {}).get("pullRequest", {}).get("autoMergeRequest")
    return {"success": True, "message": "Auto-merge disabled"} if am is None else {"success": False, "error": "Still active"}

def main() -> int:
    p = argparse.ArgumentParser(description="Enable/disable auto-merge")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--repo", type=str, required=True, help="owner/repo")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--enable", action="store_true")
    g.add_argument("--disable", action="store_true")
    p.add_argument("--merge-method", choices=["MERGE", "SQUASH", "REBASE"], default="SQUASH")
    args = p.parse_args()
    try:
        if "/" not in args.repo:
            print(json.dumps({"success": False, "error": "Invalid repo format", "code": "INVALID_PARAMS"}, indent=2))
            return 1  # Invalid parameters
        owner, repo = args.repo.split("/", 1)
        pr_id, pr_info = get_pr_id(owner, repo, args.pr)
        if not pr_id:
            print(json.dumps({"success": False, "error": "PR not found", "code": "RESOURCE_NOT_FOUND"}, indent=2))
            return 2  # Resource not found
        if pr_info.get("merged"):
            print(json.dumps({"success": False, "error": "PR already merged", "code": "ALREADY_MERGED"}, indent=2))
            return 5  # Idempotency skip - already merged
        if pr_info.get("state") != "OPEN":
            print(json.dumps({"success": False, "error": "PR not open", "code": "NOT_MERGEABLE"}, indent=2))
            return 6  # Not mergeable
        if args.enable:
            if not pr_info.get("viewerCanEnableAutoMerge"):
                print(json.dumps({"success": False, "error": "Cannot enable (check settings)", "code": "NOT_MERGEABLE"}, indent=2))
                return 6  # Not mergeable
            result = enable_auto_merge(pr_id, args.merge_method)
        else:
            if not pr_info.get("viewerCanDisableAutoMerge"):
                result = {"success": True, "message": "Auto-merge was not enabled"} if not pr_info.get("autoMergeRequest") else {"success": False, "error": "Cannot disable"}
            else:
                result = disable_auto_merge(pr_id)
        print(json.dumps(result, indent=2))
        return 0 if result.get("success") else 3  # API error if failed
    except ValueError as e:
        print(json.dumps({"success": False, "error": str(e), "code": "INVALID_PARAMS"}, indent=2))
        return 1  # Invalid parameters
    except Exception as e:
        error_msg = str(e).lower()
        if "auth" in error_msg or "login" in error_msg:
            print(json.dumps({"success": False, "error": str(e), "code": "NOT_AUTHENTICATED"}, indent=2))
            return 4  # Not authenticated
        print(json.dumps({"success": False, "error": str(e), "code": "API_ERROR"}, indent=2))
        return 3  # API error

if __name__ == "__main__":
    sys.exit(main())
