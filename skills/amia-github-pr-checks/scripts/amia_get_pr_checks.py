#!/usr/bin/env python3
"""
Get all check statuses for a GitHub Pull Request.

This script retrieves CI/CD check statuses for a PR and categorizes them
into passing, failing, pending, and skipped. Use this to determine if
a PR is ready for merge or to get an overview of CI status.

Usage:
    python amia_get_pr_checks.py --pr 123
    python amia_get_pr_checks.py --pr 123 --required-only
    python amia_get_pr_checks.py --pr 123 --summary-only
    python amia_get_pr_checks.py --pr 123 --repo owner/repo

Output: JSON to stdout with check details and summary counts.

Exit codes (standardized):
    0 - Success, check data returned
    1 - Invalid parameters (bad PR number, missing required args)
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


def run_gh_command(args: list[str]) -> tuple[int, str, str]:
    """Run a gh CLI command and return exit code, stdout, stderr."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr


def get_pr_checks(pr_number: int, repo: str | None = None) -> dict[str, Any]:
    """Fetch all checks for a PR using gh CLI."""
    cmd = ["pr", "checks", str(pr_number), "--json",
           "name,state,description,bucket,link,startedAt,completedAt"]
    if repo:
        cmd.extend(["--repo", repo])

    exit_code, stdout, stderr = run_gh_command(cmd)

    if exit_code != 0:
        if "Could not find" in stderr or "not found" in stderr.lower():
            return {"error": "pr_not_found", "message": stderr.strip()}
        return {"error": "gh_error", "message": stderr.strip()}

    try:
        return {"checks": json.loads(stdout) if stdout.strip() else []}
    except json.JSONDecodeError as e:
        return {"error": "json_parse_error", "message": str(e)}


def get_required_checks(repo: str | None = None, branch: str = "main") -> list[str]:
    """Get list of required check names from branch protection."""
    cmd = ["api", f"repos/{{owner}}/{{repo}}/branches/{branch}/protection"]
    if repo:
        cmd = ["api", f"repos/{repo}/branches/{branch}/protection"]

    exit_code, stdout, stderr = run_gh_command(cmd)
    if exit_code != 0:
        return []  # No branch protection or error

    try:
        protection = json.loads(stdout)
        contexts = protection.get("required_status_checks", {}).get("contexts", [])
        return contexts
    except (json.JSONDecodeError, KeyError):
        return []


def categorize_checks(checks: list[dict], required_names: list[str]) -> dict[str, Any]:
    """Categorize checks into passing, failing, pending, skipped."""
    passing = []
    failing = []
    pending = []
    skipped = []

    for check in checks:
        check_info = {
            "name": check.get("name", "unknown"),
            "state": check.get("state", "unknown"),
            "bucket": check.get("bucket", "unknown"),
            "required": check.get("name", "") in required_names,
            "link": check.get("link", ""),
            "description": check.get("description", "")
        }

        bucket = check.get("bucket", "").lower()
        state = check.get("state", "").lower()

        if bucket == "pass" or state == "success":
            passing.append(check_info)
        elif bucket == "fail" or state in ("failure", "error"):
            failing.append(check_info)
        elif bucket == "pending" or state in ("pending", "queued", "in_progress"):
            pending.append(check_info)
        elif bucket == "skipping" or state == "skipped":
            skipped.append(check_info)
        else:
            pending.append(check_info)  # Unknown state treated as pending

    return {
        "passing": passing,
        "failing": failing,
        "pending": pending,
        "skipped": skipped
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Get PR check statuses")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", type=str, help="Repository (owner/repo)")
    parser.add_argument("--required-only", action="store_true",
                        help="Only show required checks")
    parser.add_argument("--summary-only", action="store_true",
                        help="Only show summary counts")
    args = parser.parse_args()

    # Fetch checks
    result = get_pr_checks(args.pr, args.repo)
    if "error" in result:
        error_type = result["error"]
        result["code"] = error_type.upper()
        print(json.dumps(result), file=sys.stderr)
        if error_type == "pr_not_found":
            return 2  # Resource not found
        if "auth" in result.get("message", "").lower():
            return 4  # Not authenticated
        return 3  # API error

    checks = result.get("checks", [])
    required_names = get_required_checks(args.repo)
    categorized = categorize_checks(checks, required_names)

    # Filter to required only if requested
    if args.required_only:
        for key in ["passing", "failing", "pending", "skipped"]:
            categorized[key] = [c for c in categorized[key] if c["required"]]

    # Calculate summary
    all_checks = (categorized["passing"] + categorized["failing"] +
                  categorized["pending"] + categorized["skipped"])
    required_checks = [c for c in all_checks if c["required"]]
    required_failing = [c for c in categorized["failing"] if c["required"]]
    required_pending = [c for c in categorized["pending"] if c["required"]]

    output = {
        "pr_number": args.pr,
        "total_checks": len(all_checks),
        "passing": len(categorized["passing"]),
        "failing": len(categorized["failing"]),
        "pending": len(categorized["pending"]),
        "skipped": len(categorized["skipped"]),
        "all_passing": len(categorized["failing"]) == 0 and len(categorized["pending"]) == 0,
        "required_passing": len(required_failing) == 0 and len(required_pending) == 0,
        "required_count": len(required_checks)
    }

    if not args.summary_only:
        output["checks"] = all_checks

    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
