#!/usr/bin/env python3
"""GitHub Projects kanban synchronization with CI status.

Automatically updates issue/PR status based on:
- CI pass/fail results
- PR merge status
- Review status
- Manual status overrides

Integrates with AI Maestro for orchestrator notifications.
"""

import sys
import json
from pathlib import Path
from typing import Any, Optional, Literal
from dataclasses import dataclass

SKILLS_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "shared"))
from cross_platform import run_command, atomic_write_json  # type: ignore[import-not-found]  # noqa: E402
from aimaestro_notify import notify_task_blocked  # type: ignore[import-not-found]  # noqa: E402

# Status column mapping
STATUS_COLUMNS = {
    "Backlog": "backlog",
    "Todo": "todo",
    "In Progress": "in-progress",
    "AI Review": "ai-review",
    "Human Review": "human-review",
    "Merge/Release": "merge-release",
    "Done": "done",
    "Blocked": "blocked",
}


@dataclass
class IssueStatus:
    number: int
    title: str
    current_status: str
    ci_status: Optional[str]  # passing, failing, pending
    pr_status: Optional[str]  # open, merged, closed
    review_status: Optional[str]  # pending, approved, changes_requested
    last_updated: str


def get_issue_status(owner: str, repo: str, issue_number: int) -> IssueStatus:
    """Get comprehensive issue status from GitHub."""
    # Get issue details
    code, out, err = run_command(
        ["gh", "api", f"/repos/{owner}/{repo}/issues/{issue_number}"]
    )
    if code != 0:
        raise RuntimeError(f"Failed to get issue: {err}")

    issue = json.loads(out)

    # Get associated PR if any
    pr_status = None
    code, out, err = run_command(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "all",
            "--search",
            f"#{issue_number}",
            "--json",
            "number,state,reviewDecision,statusCheckRollup",
            "--repo",
            f"{owner}/{repo}",
        ]
    )

    ci_status = None
    review_status = None

    if code == 0:
        prs = json.loads(out)
        if prs:
            pr = prs[0]
            pr_status = pr.get("state", "").lower()
            review_status = pr.get("reviewDecision", "").lower().replace("_", " ")

            # Get CI status from check rollup
            checks = pr.get("statusCheckRollup", [])
            if checks:
                if all(c.get("conclusion") == "success" for c in checks):
                    ci_status = "passing"
                elif any(c.get("conclusion") == "failure" for c in checks):
                    ci_status = "failing"
                else:
                    ci_status = "pending"

    # Determine current status from labels
    labels = [lbl.get("name", "").lower() for lbl in issue.get("labels", [])]
    current_status = "backlog"
    for label in labels:
        if label in STATUS_COLUMNS.values():
            current_status = label
            break

    return IssueStatus(
        number=issue_number,
        title=issue.get("title", ""),
        current_status=current_status,
        ci_status=ci_status,
        pr_status=pr_status,
        review_status=review_status,
        last_updated=issue.get("updated_at", ""),
    )


def determine_new_status(status: IssueStatus) -> Optional[str]:
    """Determine if status should change based on CI/PR state."""

    # If CI failing, should be blocked
    if status.ci_status == "failing" and status.current_status != "blocked":
        return "blocked"

    # If PR merged, should be done
    if status.pr_status == "merged" and status.current_status != "done":
        return "done"

    # If PR open with passing CI, should be ai-review
    if status.pr_status == "open" and status.ci_status == "passing":
        if status.current_status not in ("ai-review", "human-review", "merge-release", "done"):
            return "ai-review"

    # If review approved, move to human-review (waiting for human sign-off)
    if status.review_status == "approved" and status.current_status not in ("human-review", "merge-release", "done"):
        return "human-review"

    # If changes requested, should be in-progress
    if status.review_status == "changes requested":
        if status.current_status in ("ai-review", "human-review"):
            return "in-progress"

    return None


def update_issue_status(
    owner: str, repo: str, issue_number: int, new_status: str, notify: bool = True
) -> bool:
    """Update issue status label on GitHub."""
    # Remove old status labels
    for status in STATUS_COLUMNS.values():
        run_command(
            [
                "gh",
                "issue",
                "edit",
                str(issue_number),
                "--remove-label",
                status,
                "--repo",
                f"{owner}/{repo}",
            ]
        )

    # Add new status label
    code, out, err = run_command(
        [
            "gh",
            "issue",
            "edit",
            str(issue_number),
            "--add-label",
            new_status,
            "--repo",
            f"{owner}/{repo}",
        ]
    )

    if code != 0:
        return False

    # Notify orchestrator if status changed to blocked
    if notify and new_status == "blocked":
        notify_task_blocked(
            task_id=f"GH-{issue_number}",
            reason="CI failing or review changes requested",
            issue_number=issue_number,
        )

    return True


def sync_all_issues(
    owner: str, repo: str, project_number: int
) -> dict[str, int | list[str] | list[dict[str, Any]]]:
    """Sync all issues in a GitHub Project."""
    synced_count = 0
    updated_count = 0
    errors: list[str] = []
    changes: list[dict[str, Any]] = []

    # Get all issues in project
    code, out, err = run_command(
        [
            "gh",
            "api",
            "--paginate",
            f"/repos/{owner}/{repo}/issues",
            "--jq",
            ".[].number",
        ]
    )

    if code != 0:
        errors.append(f"Failed to list issues: {err}")
        return {
            "synced": synced_count,
            "updated": updated_count,
            "errors": errors,
            "changes": changes,
        }

    issue_numbers = [int(n) for n in out.strip().split("\n") if n]

    for number in issue_numbers:
        try:
            issue_status = get_issue_status(owner, repo, number)
            new_status = determine_new_status(issue_status)

            synced_count += 1

            if new_status:
                if update_issue_status(owner, repo, number, new_status):
                    updated_count += 1
                    changes.append(
                        {
                            "issue": number,
                            "from": issue_status.current_status,
                            "to": new_status,
                            "reason": f"CI: {issue_status.ci_status}, PR: {issue_status.pr_status}",
                        }
                    )
                else:
                    errors.append(f"Failed to update #{number}")
        except Exception as exc:
            errors.append(f"Error processing #{number}: {exc}")

    return {
        "synced": synced_count,
        "updated": updated_count,
        "errors": errors,
        "changes": changes,
    }


def on_ci_status_change(
    owner: str, repo: str, branch: str, status: Literal["success", "failure", "pending"]
) -> None:
    """Handle CI status change event."""
    # Find issue/PR for this branch
    code, out, err = run_command(
        [
            "gh",
            "pr",
            "list",
            "--head",
            branch,
            "--json",
            "number",
            "--repo",
            f"{owner}/{repo}",
        ]
    )

    if code == 0:
        prs = json.loads(out)
        for pr in prs:
            pr_number = pr.get("number")
            if status == "failure":
                update_issue_status(owner, repo, pr_number, "blocked")
            elif status == "success":
                # Check if was blocked due to CI
                issue_status = get_issue_status(owner, repo, pr_number)
                if issue_status.current_status == "blocked":
                    update_issue_status(owner, repo, pr_number, "ai-review")


# CLI
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="GitHub kanban sync")
    parser.add_argument("--owner", required=True, help="Repository owner")
    parser.add_argument("--repo", required=True, help="Repository name")
    parser.add_argument("--project", type=int, help="Project number for full sync")
    parser.add_argument("--issue", type=int, help="Sync single issue")
    parser.add_argument(
        "--ci-event",
        nargs=3,
        metavar=("BRANCH", "STATUS", "RUN_ID"),
        help="Handle CI event",
    )
    parser.add_argument("--output", type=Path, help="Output results to file")

    args = parser.parse_args()

    if args.ci_event:
        branch, status, run_id = args.ci_event
        on_ci_status_change(args.owner, args.repo, branch, status)
        print(f"Handled CI event: {status} on {branch}")

    elif args.issue:
        status = get_issue_status(args.owner, args.repo, args.issue)
        new_status = determine_new_status(status)
        print(f"Issue #{args.issue}: {status.current_status}")
        if new_status:
            print(f"  → Should update to: {new_status}")
            if input("Update? [y/N] ").lower() == "y":
                update_issue_status(args.owner, args.repo, args.issue, new_status)

    elif args.project:
        results = sync_all_issues(args.owner, args.repo, args.project)
        print(f"Synced: {results['synced']}, Updated: {results['updated']}")
        errors_list = results["errors"]
        if errors_list:
            print(f"Errors: {len(errors_list)}")  # type: ignore[arg-type]
        if args.output:
            atomic_write_json(results, args.output)
