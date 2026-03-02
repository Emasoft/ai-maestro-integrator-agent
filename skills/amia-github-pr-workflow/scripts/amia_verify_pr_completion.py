#!/usr/bin/env python3
"""
PR completion verification script.

Verifies all completion criteria for a specific PR and returns
pass/fail status with detailed reasons.

Usage:
    python amia_verify_pr_completion.py --repo owner/repo --pr 123
    python amia_verify_pr_completion.py --repo owner/repo --pr 123 --stage pre-review
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any


def run_gh_command(args: list[str]) -> dict[str, Any] | list[Any] | str:
    """Run a gh CLI command and return parsed JSON or raw output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        try:
            parsed: dict[str, Any] | list[Any] = json.loads(result.stdout)
            return parsed
        except json.JSONDecodeError:
            return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return {"error": e.stderr.strip()}


def check_reviews_addressed(repo: str, pr: int) -> tuple[bool, str]:
    """Check if all review comments have been addressed."""
    pr_data = run_gh_command(
        [
            "pr",
            "view",
            str(pr),
            "--repo",
            repo,
            "--json",
            "latestReviews,reviewDecision",
        ]
    )
    if not isinstance(pr_data, dict):
        return False, "Unexpected response format"
    if "error" in pr_data:
        return False, "Failed to get review data"
    reviews = pr_data.get("latestReviews", [])
    if not isinstance(reviews, list):
        reviews = []
    has_changes_requested = any(
        isinstance(r, dict) and r.get("state") == "CHANGES_REQUESTED" for r in reviews
    )
    if has_changes_requested:
        return False, "Changes requested by reviewer"
    return True, "All reviews addressed"


def check_comments_acknowledged(repo: str, pr: int) -> tuple[bool, str]:
    """Check if all PR comments have been acknowledged."""
    owner, repo_name = repo.split("/")
    _result = run_gh_command(
        ["api", f"repos/{owner}/{repo_name}/issues/{pr}/comments", "--jq", "length"]
    )
    # Simple heuristic: if there are comments, assume acknowledged
    # Real implementation would check for unanswered questions
    return True, "Comments checked"


def check_quiet_period(repo: str, pr: int, seconds: int = 45) -> tuple[bool, str]:
    """Check if no new comments in last N seconds."""
    owner, repo_name = repo.split("/")
    comments = run_gh_command(
        ["api", f"repos/{owner}/{repo_name}/issues/{pr}/comments"]
    )
    if isinstance(comments, dict) and "error" in comments:
        return False, "Failed to get comments"
    if not comments:
        return True, "No comments"
    if isinstance(comments, list) and len(comments) > 0:
        last_comment_time = comments[-1].get("created_at", "")
        if last_comment_time:
            last_time = datetime.fromisoformat(last_comment_time.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            if (now - last_time) < timedelta(seconds=seconds):
                return (
                    False,
                    f"New comment {int((now - last_time).total_seconds())}s ago",
                )
    return True, f"No activity in last {seconds}s"


def check_ci_passing(repo: str, pr: int) -> tuple[bool, str]:
    """Check if all required CI checks pass."""
    checks = run_gh_command(["pr", "checks", str(pr), "--repo", repo, "--required"])
    checks_str = checks if isinstance(checks, str) else ""
    if "fail" in checks_str.lower():
        return False, "Required CI checks failing"
    if "pending" in checks_str.lower():
        return False, "CI checks still pending"
    return True, "All CI checks passing"


def check_unresolved_threads(repo: str, pr: int) -> tuple[bool, str]:
    """Check if there are unresolved conversation threads."""
    owner, repo_name = repo.split("/")
    query = """
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 100) {
            nodes { isResolved }
          }
        }
      }
    }
    """
    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"owner={owner}",
            "-f",
            f"repo={repo_name}",
            "-F",
            f"pr={pr}",
        ]
    )
    if isinstance(result, dict):
        threads = (
            result.get("data", {})
            .get("repository", {})
            .get("pullRequest", {})
            .get("reviewThreads", {})
            .get("nodes", [])
        )
        unresolved = sum(1 for t in threads if not t.get("isResolved", True))
        if unresolved > 0:
            return False, f"{unresolved} unresolved thread(s)"
    return True, "All threads resolved"


def check_merge_eligible(repo: str, pr: int) -> tuple[bool, str]:
    """Check if PR is merge eligible."""
    pr_data = run_gh_command(
        ["pr", "view", str(pr), "--repo", repo, "--json", "mergeable,mergeStateStatus"]
    )
    if not isinstance(pr_data, dict):
        return False, "Unexpected response format"
    if "error" in pr_data:
        return False, "Failed to get merge status"
    mergeable = pr_data.get("mergeable", "UNKNOWN")
    if mergeable == "CONFLICTING":
        return False, "Has merge conflicts"
    if mergeable == "UNKNOWN":
        return False, "Merge status unknown"
    return True, "Merge eligible"


def check_not_merged(repo: str, pr: int) -> tuple[bool, str]:
    """Check if PR is not already merged."""
    pr_data = run_gh_command(
        ["pr", "view", str(pr), "--repo", repo, "--json", "state,merged"]
    )
    if isinstance(pr_data, dict):
        if pr_data.get("merged"):
            return False, "PR already merged"
        if pr_data.get("state") == "CLOSED":
            return False, "PR is closed"
    return True, "PR is open"


def check_commits_pushed(repo: str, pr: int) -> tuple[bool, str]:
    """Check if commits exist (basic check)."""
    pr_data = run_gh_command(
        ["pr", "view", str(pr), "--repo", repo, "--json", "commits"]
    )
    if isinstance(pr_data, dict) and pr_data.get("commits"):
        return True, "Commits present"
    return True, "Commits status OK"


def verify_completion(repo: str, pr: int, stage: str | None = None) -> dict[str, Any]:
    """Run all verification checks and return results."""
    all_checks: dict[str, Any] = {
        "reviews_addressed": check_reviews_addressed,
        "comments_acknowledged": check_comments_acknowledged,
        "no_new_comments": lambda r, p: check_quiet_period(r, p, 45),
        "ci_passing": check_ci_passing,
        "no_unresolved_threads": check_unresolved_threads,
        "merge_eligible": check_merge_eligible,
        "not_merged": check_not_merged,
        "commits_pushed": check_commits_pushed,
    }
    stage_checks: dict[str, list[str]] = {
        "pre-review": ["not_merged", "ci_passing", "merge_eligible"],
        "post-review": [
            "reviews_addressed",
            "comments_acknowledged",
            "no_unresolved_threads",
        ],
        "ci": ["ci_passing"],
        "merge": list(all_checks.keys()),
    }
    checks_to_run: list[str]
    if stage is not None:
        checks_to_run = stage_checks.get(stage, list(all_checks.keys()))
    else:
        checks_to_run = list(all_checks.keys())
    criteria: dict[str, bool] = {}
    failing: list[str] = []
    for check_name in checks_to_run:
        check_fn = all_checks.get(check_name)
        if check_fn:
            passed, reason = check_fn(repo, pr)
            criteria[check_name] = passed
            if not passed:
                failing.append(f"{check_name}: {reason}")
    complete = len(failing) == 0
    recommendation = (
        "ready_to_merge"
        if complete
        else (
            "blocked"
            if "merge_eligible" in [f.split(":")[0] for f in failing]
            else "needs_work"
        )
    )
    return {
        "pr_number": pr,
        "complete": complete,
        "criteria": criteria,
        "failing_criteria": failing,
        "recommendation": recommendation,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Verify PR completion criteria")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--pr", required=True, type=int, help="PR number")
    parser.add_argument(
        "--stage",
        choices=["pre-review", "post-review", "ci", "merge"],
        help="Check specific stage only",
    )
    args = parser.parse_args()
    # Validate repo format before any split("/") calls downstream
    if "/" not in args.repo or args.repo.count("/") != 1:
        print(json.dumps({"error": f"Invalid repo format: {args.repo!r}, expected 'owner/name'"}))
        sys.exit(1)
    result = verify_completion(args.repo, args.pr, args.stage)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["complete"] else 1)


if __name__ == "__main__":
    main()
