#!/usr/bin/env python3
"""
Orchestrator PR polling script for monitoring open PRs.

Gets all open PRs, checks their status, identifies actions needed,
and returns a prioritized action list.

Usage:
    python amia_orchestrator_pr_poll.py --repo owner/repo
    python amia_orchestrator_pr_poll.py --repo owner/repo --filter needs_action
    python amia_orchestrator_pr_poll.py --repo owner/repo --pr 123
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
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


def get_author_type(user: dict[str, Any]) -> str:
    """Determine if PR author is human or bot."""
    login = str(user.get("login", "")).lower()
    user_type = str(user.get("type", ""))
    if user_type == "Bot":
        if "dependabot" in login or "renovate" in login:
            return "update-bot"
        if "actions" in login:
            return "mention-bot"
        return "agent-bot"
    bot_patterns = ["[bot]", "-bot", "_bot", "-ai", "_ai", "-agent"]
    if any(pattern in login for pattern in bot_patterns):
        return "agent-bot"
    return "human"


def determine_status(pr_data: dict[str, Any], checks_result: str) -> str:
    """Determine the status of a PR."""
    if pr_data.get("isDraft"):
        return "draft"
    reviews = pr_data.get("latestReviews", [])
    if not isinstance(reviews, list):
        reviews = []
    has_changes_requested = any(
        isinstance(r, dict) and r.get("state") == "CHANGES_REQUESTED" for r in reviews
    )
    if has_changes_requested:
        return "needs_changes"
    has_approval = any(
        isinstance(r, dict) and r.get("state") == "APPROVED" for r in reviews
    )
    mergeable = pr_data.get("mergeable", "UNKNOWN")
    if mergeable == "CONFLICTING":
        return "blocked"
    if "fail" in checks_result.lower():
        return "ci_failing"
    if "pending" in checks_result.lower():
        return "ci_pending"
    if has_approval and mergeable == "MERGEABLE":
        return "ready"
    return "needs_review"


def determine_action(status: str, author_type: str) -> str:
    """Determine what action is needed based on status."""
    action_map = {
        "draft": "wait",
        "needs_review": "delegate_review",
        "needs_changes": "delegate_fix",
        "ci_failing": "delegate_fix",
        "ci_pending": "wait",
        "blocked": "resolve_conflict",
        "ready": "verify_completion",
    }
    return action_map.get(status, "unknown")


def get_priority(status: str, author_type: str) -> int:
    """Assign priority (1=highest)."""
    priority_map = {
        "ci_failing": 1,
        "needs_changes": 2,
        "blocked": 2,
        "needs_review": 3,
        "ready": 4,
        "ci_pending": 5,
        "draft": 6,
    }
    return priority_map.get(status, 5)


def poll_prs(
    repo: str, pr_filter: str | None = None, pr_number: int | None = None
) -> dict[str, Any]:
    """Poll PRs and return status information."""
    poll_time = datetime.now(timezone.utc).isoformat()
    if pr_number:
        prs_data = run_gh_command(
            [
                "pr",
                "view",
                str(pr_number),
                "--repo",
                repo,
                "--json",
                "number,title,state,isDraft,author,createdAt,updatedAt,mergeable,latestReviews",
            ]
        )
        if isinstance(prs_data, dict) and "error" not in prs_data:
            prs_data = [prs_data]
        else:
            return {"error": f"Failed to get PR #{pr_number}", "details": prs_data}
    else:
        prs_data = run_gh_command(
            [
                "pr",
                "list",
                "--repo",
                repo,
                "--state",
                "open",
                "--json",
                "number,title,state,isDraft,author,createdAt,updatedAt,mergeable,latestReviews",
            ]
        )
    if isinstance(prs_data, dict) and "error" in prs_data:
        return {"error": "Failed to list PRs", "details": prs_data}
    # Type guard: ensure prs_data is a list of dicts
    if not isinstance(prs_data, list):
        return {"error": "Unexpected response format", "details": str(prs_data)}
    results: list[dict[str, Any]] = []
    for pr in prs_data:
        if not isinstance(pr, dict):
            continue
        pr_num = pr.get("number")
        if pr_num is None:
            continue
        checks_result = run_gh_command(["pr", "checks", str(pr_num), "--repo", repo])
        checks_str = checks_result if isinstance(checks_result, str) else ""
        ci_status = "passing"
        if "fail" in checks_str.lower():
            ci_status = "failing"
        elif "pending" in checks_str.lower():
            ci_status = "pending"
        status = determine_status(pr, checks_str)
        author = pr.get("author", {})
        if not isinstance(author, dict):
            author = {}
        author_type = get_author_type(author)
        action = determine_action(status, author_type)
        priority = get_priority(status, author_type)
        state_val = pr.get("state", "")
        pr_result: dict[str, Any] = {
            "number": pr_num,
            "title": pr.get("title", ""),
            "state": state_val.lower() if isinstance(state_val, str) else "",
            "author": author.get("login", "unknown"),
            "author_type": author_type,
            "created_at": pr.get("createdAt", ""),
            "updated_at": pr.get("updatedAt", ""),
            "status": status,
            "ci_status": ci_status,
            "mergeable": pr.get("mergeable", "UNKNOWN") == "MERGEABLE",
            "priority": priority,
            "action_needed": action,
        }
        results.append(pr_result)
    if pr_filter == "needs_action":
        results = [r for r in results if r["action_needed"] not in ["wait", "unknown"]]
    results.sort(key=lambda x: x["priority"])
    summary: dict[str, Any] = {
        "total_open": len(prs_data),
        "needs_action": sum(
            1 for r in results if r["action_needed"] not in ["wait", "unknown"]
        ),
        "blocked": sum(1 for r in results if r["status"] == "blocked"),
        "ready_to_merge": sum(1 for r in results if r["status"] == "ready"),
    }
    return {"poll_time": poll_time, "repo": repo, "prs": results, "summary": summary}


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Poll PR status for orchestrator")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--filter", choices=["needs_action"], help="Filter results")
    parser.add_argument("--pr", type=int, help="Check specific PR number only")
    args = parser.parse_args()
    result = poll_prs(args.repo, args.filter, args.pr)
    print(json.dumps(result, indent=2))
    if "error" in result:
        sys.exit(1)


if __name__ == "__main__":
    main()
