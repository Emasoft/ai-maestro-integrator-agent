#!/usr/bin/env python3
"""
amia_milestone_progress.py - Report and manage GitHub milestone progress.

Queries milestone completion percentage, lists overdue milestones, performs
bulk milestone assignment, and safely closes a milestone (optionally moving
its still-open issues to a successor milestone first).

All GitHub access goes through the `gh` CLI with a fixed argument vector
(never a shell string), so no untrusted value is ever interpolated into a
shell command.

Usage:
    amia_milestone_progress.py progress  --repo owner/repo --milestone "v2.1.0"
    amia_milestone_progress.py overdue   --repo owner/repo
    amia_milestone_progress.py bulk-assign --repo owner/repo --milestone "v2.1.0" --issues 1 2 3 4 5
    amia_milestone_progress.py close     --repo owner/repo --milestone "v2.0.0" --move-open-to "v2.1.0"
    amia_milestone_progress.py close     --repo owner/repo --milestone "v2.0.0" --force

Output:
    JSON to stdout describing the result of the requested operation.

Exit codes (standardized):
    0 - Success
    1 - Invalid parameters
    2 - Resource not found (milestone not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def run_gh(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command with a fixed argv and return (ok, output)."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout.strip()
    return False, result.stderr.strip()


def get_milestone(repo: str, title: str) -> dict | None:
    """Return the milestone object matching `title`, or None if absent."""
    ok, out = run_gh(["api", f"repos/{repo}/milestones", "--paginate"])
    if not ok or not out:
        return None
    for milestone in json.loads(out):
        if milestone.get("title") == title:
            return milestone
    return None


def get_progress(repo: str, title: str) -> dict:
    """Compute completion percentage and issue counts for a milestone."""
    milestone = get_milestone(repo, title)
    if milestone is None:
        return {"error": "Milestone not found"}

    open_count = milestone.get("open_issues", 0)
    closed_count = milestone.get("closed_issues", 0)
    total = open_count + closed_count
    percent = (closed_count / total * 100) if total > 0 else 0.0

    return {
        "title": milestone["title"],
        "open_issues": open_count,
        "closed_issues": closed_count,
        "total_issues": total,
        "percent_complete": round(percent, 1),
        "due_on": milestone.get("due_on"),
        "state": milestone.get("state"),
    }


def get_overdue(repo: str) -> list[dict]:
    """Return all open milestones whose due date is in the past."""
    ok, out = run_gh(["api", f"repos/{repo}/milestones", "--paginate"])
    if not ok or not out:
        return []

    now = datetime.now(timezone.utc)
    overdue: list[dict] = []
    for ms in json.loads(out):
        if ms.get("state") != "open" or not ms.get("due_on"):
            continue
        due_on = datetime.fromisoformat(ms["due_on"].replace("Z", "+00:00"))
        if due_on < now:
            overdue.append(
                {
                    "title": ms["title"],
                    "due_on": ms["due_on"],
                    "days_overdue": (now - due_on).days,
                    "open_issues": ms.get("open_issues", 0),
                    "closed_issues": ms.get("closed_issues", 0),
                }
            )
    return overdue


def assign_issue(repo: str, issue_number: int, milestone_title: str) -> bool:
    """Assign one issue to a milestone by title."""
    ok, _ = run_gh(
        [
            "issue", "edit", str(issue_number),
            "--repo", repo,
            "--milestone", milestone_title,
        ]
    )
    return ok


def bulk_assign(repo: str, issue_numbers: list[int], milestone_title: str) -> dict:
    """Assign multiple issues to a milestone, reporting success/failure."""
    results: dict[str, list[int]] = {"success": [], "failed": []}
    for issue_num in issue_numbers:
        bucket = "success" if assign_issue(repo, issue_num, milestone_title) else "failed"
        results[bucket].append(issue_num)
    return results


def get_open_issue_numbers(repo: str, milestone_title: str) -> list[int]:
    """List the numbers of still-open issues in a milestone."""
    ok, out = run_gh(
        [
            "issue", "list",
            "--repo", repo,
            "--milestone", milestone_title,
            "--state", "open",
            "--json", "number",
            "--jq", ".[].number",
        ]
    )
    if not ok or not out:
        return []
    return [int(line) for line in out.splitlines() if line.strip()]


def close_milestone(
    repo: str,
    title: str,
    move_open_to: str | None = None,
    force: bool = False,
) -> dict:
    """Close a milestone, optionally moving its open issues to a successor."""
    progress = get_progress(repo, title)
    if "error" in progress:
        return progress

    milestone = get_milestone(repo, title)
    number = milestone["number"]

    if progress["open_issues"] > 0:
        if move_open_to:
            for issue_num in get_open_issue_numbers(repo, title):
                assign_issue(repo, issue_num, move_open_to)
        elif not force:
            return {
                "error": f"Cannot close: {progress['open_issues']} issues still open",
                "hint": "Use --move-open-to or --force",
            }

    ok, _ = run_gh(
        [
            "api", f"repos/{repo}/milestones/{number}",
            "--method", "PATCH",
            "-f", "state=closed",
        ]
    )
    return {
        "success": ok,
        "milestone": title,
        "issues_moved": progress["open_issues"] if move_open_to else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Report and manage milestone progress.")
    parser.add_argument("command", choices=["progress", "overdue", "bulk-assign", "close"])
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--milestone", help="Milestone title")
    parser.add_argument("--issues", nargs="*", type=int, default=[], help="Issue numbers")
    parser.add_argument("--move-open-to", help="Successor milestone for open issues")
    parser.add_argument("--force", action="store_true", help="Close even with open issues")
    args = parser.parse_args()

    if args.command == "progress":
        if not args.milestone:
            print(json.dumps({"error": "--milestone is required"}))
            return 1
        result = get_progress(args.repo, args.milestone)
    elif args.command == "overdue":
        result = {"overdue": get_overdue(args.repo)}
    elif args.command == "bulk-assign":
        if not args.milestone or not args.issues:
            print(json.dumps({"error": "--milestone and --issues are required"}))
            return 1
        result = bulk_assign(args.repo, args.issues, args.milestone)
    else:  # close
        if not args.milestone:
            print(json.dumps({"error": "--milestone is required"}))
            return 1
        result = close_milestone(args.repo, args.milestone, args.move_open_to, args.force)

    print(json.dumps(result, indent=2))
    return 2 if isinstance(result, dict) and result.get("error") == "Milestone not found" else 0


if __name__ == "__main__":
    sys.exit(main())
