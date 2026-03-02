#!/usr/bin/env python3
"""
Wait for all PR checks to complete with exponential backoff.

This script polls GitHub for PR check status until all checks complete
or a timeout is reached. Uses exponential backoff to efficiently use
API quota while still catching quick completions.

Usage:
    python amia_wait_for_checks.py --pr 123 --timeout 600
    python amia_wait_for_checks.py --pr 123 --required-only --timeout 300
    python amia_wait_for_checks.py --pr 123 --interval 60 --fail-fast

Output: JSON to stdout with final status and timing information.

Exit codes (standardized):
    0 - Success, all checks completed (may include failures - check JSON output)
    1 - Invalid parameters (bad PR number, bad timeout value)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout waiting for checks)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)

Note: Timeout waiting for checks returns exit code 3 (API error / timeout).
      Check the JSON output's timed_out field for details.
"""

import argparse
import json
import random
import subprocess
import sys
import time
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
    """Fetch current check status for a PR."""
    cmd = ["pr", "checks", str(pr_number), "--json",
           "name,state,bucket,link,startedAt,completedAt"]
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


def analyze_checks(checks: list[dict]) -> dict[str, Any]:
    """Analyze check status and determine if complete."""
    passing = []
    failing = []
    pending = []

    for check in checks:
        name = check.get("name", "unknown")
        bucket = check.get("bucket", "").lower()
        state = check.get("state", "").lower()

        info = {"name": name, "state": state, "bucket": bucket,
                "link": check.get("link", "")}

        if bucket == "pass" or state == "success":
            passing.append(info)
        elif bucket == "fail" or state in ("failure", "error"):
            failing.append(info)
        elif bucket in ("pending", "") or state in ("pending", "queued", "in_progress"):
            pending.append(info)
        else:
            passing.append(info)  # Skipped/neutral treated as non-blocking

    all_complete = len(pending) == 0
    has_failures = len(failing) > 0

    return {
        "complete": all_complete,
        "has_failures": has_failures,
        "passing": passing,
        "failing": failing,
        "pending": pending
    }


def calculate_backoff(attempt: int, base: float, multiplier: float,
                      max_interval: float) -> float:
    """Calculate backoff interval with jitter."""
    interval = min(base * (multiplier ** attempt), max_interval)
    # Add jitter: 50-100% of interval
    return interval * (0.5 + random.random() * 0.5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for PR checks to complete")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", type=str, help="Repository (owner/repo)")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="Max wait time in seconds (default: 1800)")
    parser.add_argument("--interval", type=int, default=10,
                        help="Initial poll interval in seconds (default: 10)")
    parser.add_argument("--required-only", action="store_true",
                        help="Only wait for required checks")
    parser.add_argument("--fail-fast", action="store_true",
                        help="Exit immediately on first failure")
    args = parser.parse_args()

    start_time = time.time()
    attempt = 0
    max_interval = 120.0
    multiplier = 1.5

    while True:
        elapsed = time.time() - start_time

        # Check timeout
        if elapsed >= args.timeout:
            result = get_pr_checks(args.pr, args.repo)
            checks = result.get("checks", [])
            analysis = analyze_checks(checks)

            output = {
                "pr_number": args.pr,
                "completed": False,
                "timed_out": True,
                "code": "TIMEOUT",
                "wait_time_seconds": int(elapsed),
                "checks_summary": {
                    "passing": len(analysis["passing"]),
                    "failing": len(analysis["failing"]),
                    "pending": len(analysis["pending"])
                },
                "pending_checks": [c["name"] for c in analysis["pending"]]
            }
            print(json.dumps(output, indent=2))
            return 3  # API error / timeout

        # Fetch current status
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
        analysis = analyze_checks(checks, args.required_only)

        # Fail-fast check
        if args.fail_fast and analysis["has_failures"]:
            output = {
                "pr_number": args.pr,
                "completed": True,
                "timed_out": False,
                "final_status": "failure",
                "early_exit": True,
                "wait_time_seconds": int(elapsed),
                "checks_summary": {
                    "passing": len(analysis["passing"]),
                    "failing": len(analysis["failing"]),
                    "pending": len(analysis["pending"])
                },
                "failed_checks": [c["name"] for c in analysis["failing"]]
            }
            print(json.dumps(output, indent=2))
            return 0

        # Check if complete
        if analysis["complete"]:
            final_status = "failure" if analysis["has_failures"] else "all_passing"
            output = {
                "pr_number": args.pr,
                "completed": True,
                "timed_out": False,
                "final_status": final_status,
                "wait_time_seconds": int(elapsed),
                "checks_summary": {
                    "passing": len(analysis["passing"]),
                    "failing": len(analysis["failing"]),
                    "pending": 0
                }
            }
            if analysis["has_failures"]:
                output["failed_checks"] = [c["name"] for c in analysis["failing"]]
            print(json.dumps(output, indent=2))
            return 0

        # Wait with backoff
        wait_time = calculate_backoff(attempt, args.interval, multiplier, max_interval)
        time.sleep(wait_time)
        attempt += 1


if __name__ == "__main__":
    sys.exit(main())
