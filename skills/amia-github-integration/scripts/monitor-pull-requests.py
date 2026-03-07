#!/usr/bin/env python3
"""
monitor-pull-requests.py - Monitor PR status and report check results.

Single-shot scan of open PRs, filtering by check status states.
Reports which PRs have failing, pending, or successful checks.

Usage:
    python scripts/monitor-pull-requests.py --repo owner/repo --watch-states pending,failed
    python scripts/monitor-pull-requests.py --repo owner/repo --watch-states all
    python scripts/monitor-pull-requests.py --repo owner/repo --watch-states failed --label priority

Output:
    JSON object with PR status report to stdout.

Example output:
    {
        "repo": "owner/repo",
        "watch_states": ["pending", "failed"],
        "total_open_prs": 5,
        "matching_prs": 2,
        "prs": [
            {
                "number": 42,
                "title": "Add feature X",
                "state": "OPEN",
                "check_status": "FAILURE",
                "failing_checks": ["lint", "test-unit"],
                "action": "Needs attention: 2 checks failing"
            }
        ]
    }

Exit codes (standardized):
    0 - Success, report generated
    1 - Invalid parameters (bad repo format)
    2 - No open PRs found
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Not applicable
    6 - Not applicable
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


# Map gh check conclusion values to simplified states
STATE_MAP = {
    "SUCCESS": "success",
    "FAILURE": "failed",
    "ERROR": "failed",
    "CANCELLED": "failed",
    "TIMED_OUT": "failed",
    "PENDING": "pending",
    "QUEUED": "pending",
    "IN_PROGRESS": "pending",
    "NEUTRAL": "success",
    "SKIPPED": "success",
    "STALE": "pending",
}


def classify_check(conclusion: str | None, status: str | None) -> str:
    """Classify a check run into a simplified state."""
    if conclusion:
        return STATE_MAP.get(conclusion.upper(), "pending")
    if status:
        return STATE_MAP.get(status.upper(), "pending")
    return "pending"


def monitor_prs(
    repo: str,
    watch_states: list[str],
    label: str | None = None,
) -> dict[str, Any]:
    """Fetch open PRs and their check statuses."""
    cmd = [
        "pr", "list", "--repo", repo,
        "--state", "open",
        "--json", "number,title,statusCheckRollup,labels",
        "--limit", "100",
    ]
    if label:
        cmd.extend(["--label", label])

    success, output = run_gh_command(cmd)
    if not success:
        if "not logged in" in output.lower():
            return {"error": True, "message": output, "code": "AUTH_REQUIRED"}
        return {"error": True, "message": output, "code": "API_ERROR"}

    try:
        prs = json.loads(output)
    except json.JSONDecodeError:
        return {"error": True, "message": f"Could not parse PR data: {output[:200]}", "code": "API_ERROR"}

    watch_all = "all" in watch_states
    matching: list[dict[str, Any]] = []

    for pr in prs:
        checks = pr.get("statusCheckRollup", []) or []
        failing: list[str] = []
        pending: list[str] = []
        overall_state = "success"

        for check in checks:
            name = check.get("name", check.get("context", "unknown"))
            state = classify_check(check.get("conclusion"), check.get("status"))
            if state == "failed":
                failing.append(name)
                overall_state = "failed"
            elif state == "pending":
                pending.append(name)
                if overall_state != "failed":
                    overall_state = "pending"

        # Determine if this PR matches watch criteria
        matches = watch_all
        if not matches and "failed" in watch_states and failing:
            matches = True
        if not matches and "pending" in watch_states and pending:
            matches = True
        if not matches and "success" in watch_states and overall_state == "success":
            matches = True

        if matches:
            action_parts = []
            if failing:
                action_parts.append(f"{len(failing)} check(s) failing")
            if pending:
                action_parts.append(f"{len(pending)} check(s) pending")
            if not action_parts:
                action_parts.append("All checks passing")
            action = "Needs attention: " + ", ".join(action_parts) if failing or pending else "All checks passing"

            matching.append({
                "number": pr["number"],
                "title": pr["title"],
                "state": "OPEN",
                "check_status": overall_state.upper(),
                "failing_checks": failing,
                "pending_checks": pending,
                "action": action,
            })

    return {
        "repo": repo,
        "watch_states": watch_states,
        "total_open_prs": len(prs),
        "matching_prs": len(matching),
        "prs": matching,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Monitor PR status and report check results.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--watch-states", required=True,
                        help="Comma-separated states to watch: pending,failed,success,all")
    parser.add_argument("--label", help="Filter PRs by label")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "monitor-pull-requests", args.output_file)
        sys.exit(1)

    watch_states = [s.strip() for s in args.watch_states.split(",")]

    result = monitor_prs(
        repo=args.repo,
        watch_states=watch_states,
        label=args.label,
    )
    write_output(result, "monitor-pull-requests", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)
    elif result.get("total_open_prs", 0) == 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
