#!/usr/bin/env python3
"""
Get detailed information about a specific PR check.

This script retrieves detailed information about a specific check run
including timing, output summary, and log URLs. Use this to investigate
why a particular check failed or to get more context about check results.

Usage:
    python amia_get_check_details.py --pr 123 --check "build"
    python amia_get_check_details.py --pr 123 --check "test" --include-logs-url
    python amia_get_check_details.py --pr 123 --check "CI / test" --repo owner/repo

Output: JSON to stdout with detailed check information.

Exit codes (standardized):
    0 - Success, check details returned
    1 - Invalid parameters (bad PR number, missing check name)
    2 - Resource not found (PR or check does not exist)
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


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a gh CLI command and return exit code, stdout, stderr."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def get_pr_head_sha(pr_number: int, repo: str | None = None) -> str | None:
    """Get the HEAD SHA of a PR."""
    cmd = ["pr", "view", str(pr_number), "--json", "headRefOid"]
    if repo:
        cmd.extend(["--repo", repo])

    exit_code, stdout, _ = run_gh_command(cmd)
    if exit_code != 0:
        return None

    try:
        data: dict[str, Any] = json.loads(stdout)
        head_ref: str | None = data.get("headRefOid")
        return head_ref
    except json.JSONDecodeError:
        return None


def get_check_runs_for_sha(sha: str, repo: str | None = None) -> list[dict[str, Any]]:
    """Get all check runs for a commit SHA."""
    endpoint = "repos/{owner}/{repo}/commits/" + sha + "/check-runs"
    if repo:
        endpoint = f"repos/{repo}/commits/{sha}/check-runs"

    cmd = ["api", endpoint, "--jq", ".check_runs"]
    exit_code, stdout, _ = run_gh_command(cmd)

    if exit_code != 0:
        return []

    try:
        result: list[dict[str, Any]] = json.loads(stdout) if stdout.strip() else []
        return result
    except json.JSONDecodeError:
        return []


def find_check_by_name(
    check_runs: list[dict[str, Any]], name: str
) -> dict[str, Any] | None:
    """Find a check run by name (case-insensitive partial match)."""
    name_lower = name.lower()

    # Try exact match first
    for check in check_runs:
        if check.get("name", "").lower() == name_lower:
            return check

    # Try partial match
    for check in check_runs:
        if name_lower in check.get("name", "").lower():
            return check

    return None


def format_check_details(
    check: dict[str, Any], include_logs: bool = False
) -> dict[str, Any]:
    """Format check run details for output."""
    started = check.get("started_at")
    completed = check.get("completed_at")

    # Calculate duration if both timestamps available
    duration = None
    if started and completed:
        from datetime import datetime

        try:
            start_dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(completed.replace("Z", "+00:00"))
            duration = int((end_dt - start_dt).total_seconds())
        except (ValueError, TypeError):
            pass

    output = {
        "name": check.get("name"),
        "status": check.get("status"),
        "conclusion": check.get("conclusion"),
        "started_at": started,
        "completed_at": completed,
        "duration_seconds": duration,
        "details_url": check.get("html_url") or check.get("details_url"),
        "external_id": check.get("external_id"),
        "app": check.get("app", {}).get("name") if check.get("app") else None,
    }

    # Include output summary if available
    check_output = check.get("output", {})
    if check_output:
        output["output"] = {
            "title": check_output.get("title"),
            "summary": check_output.get("summary"),
            "text": check_output.get("text"),
            "annotations_count": check_output.get("annotations_count", 0),
        }

    # Include logs URL if requested
    if include_logs:
        # GitHub Actions log URL pattern
        html_url = check.get("html_url", "")
        if html_url and "github.com" in html_url:
            output["logs_url"] = html_url

    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Get details for a specific PR check")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--check", type=str, required=True, help="Check name to find")
    parser.add_argument("--repo", type=str, help="Repository (owner/repo)")
    parser.add_argument(
        "--include-logs-url", action="store_true", help="Include URL to view logs"
    )
    args = parser.parse_args()

    # Get PR HEAD SHA
    sha = get_pr_head_sha(args.pr, args.repo)
    if not sha:
        error = {
            "error": "pr_not_found",
            "code": "RESOURCE_NOT_FOUND",
            "message": f"Could not find PR #{args.pr}",
        }
        print(json.dumps(error), file=sys.stderr)
        return 2  # Resource not found

    # Get check runs
    check_runs = get_check_runs_for_sha(sha, args.repo)
    if not check_runs:
        error = {
            "error": "no_checks",
            "code": "RESOURCE_NOT_FOUND",
            "message": f"No checks found for PR #{args.pr}",
        }
        print(json.dumps(error), file=sys.stderr)
        return 2  # Resource not found (no checks exist)

    # Find the specific check
    check = find_check_by_name(check_runs, args.check)
    if not check:
        available_names: list[str] = [
            str(c.get("name")) for c in check_runs if c.get("name")
        ]
        not_found_error: dict[str, Any] = {
            "error": "check_not_found",
            "code": "RESOURCE_NOT_FOUND",
            "message": f"Check '{args.check}' not found",
            "available_checks": available_names,
        }
        print(json.dumps(not_found_error), file=sys.stderr)
        return 2  # Resource not found

    # Format and output
    details = format_check_details(check, args.include_logs_url)
    details["pr_number"] = args.pr
    details["commit_sha"] = sha

    print(json.dumps(details, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
