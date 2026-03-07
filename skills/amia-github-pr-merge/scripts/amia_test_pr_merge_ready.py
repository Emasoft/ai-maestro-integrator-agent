#!/usr/bin/env python3
"""Check if a GitHub PR is ready to merge using GraphQL.

Exit codes (standardized):
    0 - Success: PR is ready to merge
    1 - Invalid parameters (bad PR number, bad repo format)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip: PR already merged (no action needed)
    6 - Not mergeable (conflicts, CI failing, unresolved threads, reviews needed)

Note: Exit code 6 covers all blocking conditions. Check the JSON output for specific reasons:
      - blocking_reasons contains codes like: CONFLICTS, CI_FAILING, UNRESOLVED_THREADS, CHANGES_REQUESTED

Usage:
    python amia_test_pr_merge_ready.py --pr 123 --repo owner/repo [--ignore-ci] [--ignore-threads]
"""
import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output

QUERY = """query($owner: String!, $repo: String!, $number: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      state merged mergeable mergeStateStatus reviewDecision
      reviewThreads(first: 100) { nodes { isResolved } }
      commits(last: 1) { nodes { commit { statusCheckRollup { state } } } }
    }
  }
}"""


def run_gql(query: str, variables: dict[str, Any]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        cmd.extend(["-F" if isinstance(v, int) else "-f", f"{k}={v}"])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"GraphQL failed: {r.stderr}")
    return json.loads(r.stdout)


def check_ready(owner: str, repo: str, pr_num: int, skip_ci: bool, skip_threads: bool) -> dict:
    pr: dict | None = None
    merge_state: str = "UNKNOWN"
    for _ in range(5):
        data = run_gql(QUERY, {"owner": owner, "repo": repo, "number": pr_num})
        pr = data.get("data", {}).get("repository", {}).get("pullRequest")
        if not pr:
            return {"ready": False, "error": "PR not found", "code": "RESOURCE_NOT_FOUND", "exit_code": 2}
        if pr.get("merged"):
            return {"ready": False, "error": "PR already merged", "code": "ALREADY_MERGED", "exit_code": 5}
        if pr.get("state") != "OPEN":
            return {"ready": False, "error": "PR not open", "code": "NOT_MERGEABLE", "exit_code": 6}
        merge_state = str(pr.get("mergeStateStatus") or "UNKNOWN")
        if merge_state != "UNKNOWN":
            break
        time.sleep(2)

    # Guard: if pr was never assigned (shouldn't happen with range(5) but satisfies type checker)
    if pr is None:
        return {"ready": False, "error": "PR not found after retries", "code": "RESOURCE_NOT_FOUND", "exit_code": 2}

    # CC-P1-A0-006: If merge state is still UNKNOWN after all retries, flag it as blocking
    if merge_state == "UNKNOWN":
        reasons = [{"code": "MERGE_UNKNOWN", "message": "Merge state could not be determined after 5 retries (UNKNOWN)"}]
    else:
        reasons = []
    mergeable = pr.get("mergeable")
    if mergeable == "CONFLICTING":
        reasons.append({"code": "CONFLICTS", "message": "Has merge conflicts"})
    if not skip_ci:
        commits = pr.get("commits", {}).get("nodes", [])
        if commits:
            rollup = commits[0].get("commit", {}).get("statusCheckRollup") or {}
            ci = rollup.get("state")
            if ci and ci not in ("SUCCESS", "PENDING"):
                reasons.append({"code": "CI_FAILING", "message": f"CI: {ci}"})
    if not skip_threads:
        threads = pr.get("reviewThreads", {}).get("nodes", [])
        unresolved = sum(1 for t in threads if not t.get("isResolved"))
        if unresolved:
            reasons.append({"code": "UNRESOLVED_THREADS", "message": f"{unresolved} threads"})
    review = pr.get("reviewDecision")
    if review in ("CHANGES_REQUESTED", "REVIEW_REQUIRED"):
        reasons.append({"code": review, "message": review.replace("_", " ").title()})
    if merge_state in ("BLOCKED", "BEHIND", "DIRTY", "UNSTABLE"):
        reasons.append({"code": f"MERGE_{merge_state}", "message": f"State: {merge_state}"})

    # Determine exit code: 0 if ready, 6 if any blocking reasons
    exit_code = 6 if reasons else 0
    return {"ready": not reasons, "blocking_reasons": reasons, "merge_state_status": merge_state,
            "mergeable": mergeable, "review_decision": review, "exit_code": exit_code}


def main() -> int:
    p = argparse.ArgumentParser(description="Check if PR is ready to merge")
    p.add_argument("--pr", type=int, required=True)
    p.add_argument("--repo", type=str, required=True, help="owner/repo")
    p.add_argument("--ignore-ci", action="store_true")
    p.add_argument("--ignore-threads", action="store_true")
    p.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = p.parse_args()
    try:
        if "/" not in args.repo:
            write_output({"ready": False, "error": "Invalid repo format", "code": "INVALID_PARAMS", "exit_code": 1}, "amia_test_pr_merge_ready", args.output_file)
            return 1  # Invalid parameters
        owner, repo = args.repo.split("/", 1)
        result = check_ready(owner, repo, args.pr, args.ignore_ci, args.ignore_threads)
        write_output(result, "amia_test_pr_merge_ready", args.output_file)
        return result.get("exit_code", 0)
    except ValueError as e:
        write_output({"ready": False, "error": str(e), "code": "INVALID_PARAMS", "exit_code": 1}, "amia_test_pr_merge_ready", args.output_file)
        return 1  # Invalid parameters
    except Exception as e:
        error_msg = str(e).lower()
        if "auth" in error_msg or "login" in error_msg:
            write_output({"ready": False, "error": str(e), "code": "NOT_AUTHENTICATED", "exit_code": 4}, "amia_test_pr_merge_ready", args.output_file)
            return 4  # Not authenticated
        write_output({"ready": False, "error": str(e), "code": "API_ERROR", "exit_code": 3}, "amia_test_pr_merge_ready", args.output_file)
        return 3  # API error

if __name__ == "__main__":
    sys.exit(main())
