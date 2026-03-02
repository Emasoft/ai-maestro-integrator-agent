#!/usr/bin/env python3
"""GitHub Project Status Reports for AMIA using GitHub Projects V2 API.

Queries project items, calculates metrics (velocity, completion rate, blockers),
and generates markdown/JSON reports. Uses gh CLI for authentication.

Usage: python amia_github_report.py --project 1 [--format json] [--list-projects]
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from amia_github_report_formatters import (
    generate_json_report,
    generate_markdown_report,
    post_report_to_issue,
    save_report_to_file,
)

__all__ = [
    "ProjectItem",
    "ProjectMetrics",
    "run_gh_command",
    "check_gh_auth",
    "get_repo_info",
    "parse_datetime",
    "get_project_items",
    "calculate_metrics",
    "list_projects",
    "main",
]


@dataclass
class ProjectItem:
    """Represents a GitHub Projects V2 item."""

    id: str
    content_type: str  # Issue, DraftIssue, PullRequest
    title: str
    number: Optional[int] = None
    status: Optional[str] = None
    labels: list[str] = field(default_factory=list)
    assignees: list[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    url: Optional[str] = None
    is_blocked: bool = False
    linked_prs: list[int] = field(default_factory=list)


@dataclass
class ProjectMetrics:
    """Calculated project metrics."""

    total_items: int = 0
    by_status: dict[str, int] = field(default_factory=dict)
    completed_count: int = 0
    in_progress_count: int = 0
    blocked_count: int = 0
    at_risk_count: int = 0
    completion_rate: float = 0.0
    velocity_items_per_week: float = 0.0
    avg_days_to_complete: float = 0.0
    oldest_in_progress_days: int = 0


def run_gh_command(
    args: list[str], capture_output: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run gh CLI command with error handling."""
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True,
            timeout=120,  # 2 minute timeout for large queries
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"ERROR: gh command timed out: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("ERROR: gh CLI not found. Install with: brew install gh", file=sys.stderr)
        sys.exit(1)


def check_gh_auth() -> bool:
    """Check if gh CLI is authenticated."""
    result = run_gh_command(["auth", "status"])
    return result.returncode == 0


def get_repo_info() -> tuple[str, str]:
    """Get current repository owner and name."""
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    if result.returncode != 0:
        print("ERROR: Not in a GitHub repository", file=sys.stderr)
        sys.exit(1)
    data = json.loads(result.stdout)
    return data["owner"]["login"], data["name"]


def parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        # Handle ISO format with Z suffix
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except ValueError:
        return None


def get_project_items(
    project_number: int, status_filter: Optional[str] = None
) -> list[ProjectItem]:
    """Fetch all items from a GitHub Projects V2 project using GraphQL pagination."""
    owner, repo = get_repo_info()
    query = """
    query($owner: String!, $repo: String!, $number: Int!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          items(first: 100, after: $cursor) {
            pageInfo {
              hasNextPage
              endCursor
            }
            nodes {
              id
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
              content {
                __typename
                ... on Issue {
                  number
                  title
                  url
                  createdAt
                  updatedAt
                  closedAt
                  labels(first: 20) {
                    nodes { name }
                  }
                  assignees(first: 10) {
                    nodes { login }
                  }
                }
                ... on PullRequest {
                  number
                  title
                  url
                  createdAt
                  updatedAt
                  closedAt
                  labels(first: 20) {
                    nodes { name }
                  }
                  assignees(first: 10) {
                    nodes { login }
                  }
                }
                ... on DraftIssue {
                  title
                  createdAt
                  updatedAt
                }
              }
            }
          }
        }
      }
    }
    """

    items: list[ProjectItem] = []
    cursor: Optional[str] = None

    while True:
        variables = {
            "owner": owner,
            "repo": repo,
            "number": project_number,
            "cursor": cursor,
        }
        result = run_gh_command(
            [
                "api",
                "graphql",
                "-f",
                f"query={query}",
                "-f",
                f"variables={json.dumps(variables)}",
            ]
        )

        if result.returncode != 0:
            print(
                f"ERROR: Failed to fetch project items: {result.stderr}",
                file=sys.stderr,
            )
            break

        data = json.loads(result.stdout)

        try:
            project_data = data["data"]["repository"]["projectV2"]["items"]
        except (KeyError, TypeError):
            print("ERROR: Project not found or no access", file=sys.stderr)
            break

        for node in project_data["nodes"]:
            if not node or not node.get("content"):
                continue

            content = node["content"]
            content_type = content.get("__typename", "Unknown")

            # Extract status
            status_field = node.get("fieldValueByName")
            status = status_field.get("name") if status_field else None

            # Apply status filter if specified
            if status_filter and status and status.lower() != status_filter.lower():
                continue

            # Extract labels and assignees
            labels: list[str] = []
            assignees: list[str] = []

            if "labels" in content:
                labels = [lbl["name"] for lbl in content["labels"].get("nodes", [])]

            if "assignees" in content:
                assignees = [a["login"] for a in content["assignees"].get("nodes", [])]

            # Check if blocked (by label)
            is_blocked = any(
                lbl.lower() in ("blocked", "blocker", "waiting") for lbl in labels
            )

            item = ProjectItem(
                id=node["id"],
                content_type=content_type,
                title=content.get("title", "Untitled"),
                number=content.get("number"),
                status=status,
                labels=labels,
                assignees=assignees,
                created_at=parse_datetime(content.get("createdAt")),
                updated_at=parse_datetime(content.get("updatedAt")),
                closed_at=parse_datetime(content.get("closedAt")),
                url=content.get("url"),
                is_blocked=is_blocked,
            )
            items.append(item)

        # Check for more pages
        page_info = project_data["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

    return items


def calculate_metrics(
    items: list[ProjectItem], velocity_days: int = 14
) -> ProjectMetrics:
    """Calculate project metrics from items."""
    metrics = ProjectMetrics()
    metrics.total_items = len(items)

    if not items:
        return metrics

    # Count by status
    for item in items:
        status = item.status or "No Status"
        metrics.by_status[status] = metrics.by_status.get(status, 0) + 1

    # Count completed (closed or Done status)
    now = datetime.now()
    completed_in_period = 0
    completion_times: list[int] = []

    for item in items:
        status_lower = (item.status or "").lower()

        # Count by category
        if status_lower in ("done", "closed", "completed", "merged"):
            metrics.completed_count += 1
            if item.closed_at and item.created_at:
                days = (item.closed_at - item.created_at).days
                completion_times.append(days)

            # Check if completed within velocity period
            if item.closed_at:
                days_ago = (now - item.closed_at.replace(tzinfo=None)).days
                if days_ago <= velocity_days:
                    completed_in_period += 1

        elif status_lower in ("in progress", "in-progress", "working"):
            metrics.in_progress_count += 1

            # Track oldest in-progress
            if item.updated_at:
                days = (now - item.updated_at.replace(tzinfo=None)).days
                metrics.oldest_in_progress_days = max(
                    metrics.oldest_in_progress_days,
                    days,
                )

        if item.is_blocked:
            metrics.blocked_count += 1

        # Check at-risk: in progress > 7 days without update
        if status_lower in ("in progress", "in-progress"):
            if item.updated_at:
                days_since_update = (now - item.updated_at.replace(tzinfo=None)).days
                if days_since_update > 7:
                    metrics.at_risk_count += 1

    # Calculate rates
    if metrics.total_items > 0:
        metrics.completion_rate = metrics.completed_count / metrics.total_items * 100

    # Velocity (items per week over velocity_days)
    if velocity_days > 0:
        weeks = velocity_days / 7
        metrics.velocity_items_per_week = (
            completed_in_period / weeks if weeks > 0 else 0
        )

    # Average completion time
    if completion_times:
        metrics.avg_days_to_complete = sum(completion_times) / len(completion_times)

    return metrics


def list_projects() -> list[dict[str, object]]:
    """List all projects in the repository."""
    owner, repo = get_repo_info()

    query = """
    query($owner: String!, $repo: String!) {
      repository(owner: $owner, name: $repo) {
        projectsV2(first: 20) {
          nodes {
            number
            title
            closed
            shortDescription
          }
        }
      }
    }
    """

    variables = json.dumps({"owner": owner, "repo": repo})
    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"variables={variables}",
        ]
    )

    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    try:
        return data["data"]["repository"]["projectsV2"]["nodes"]  # type: ignore[no-any-return]
    except (KeyError, TypeError):
        return []


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Project Status Reports for AMIA"
    )

    parser.add_argument("--project", "-p", type=int, help="Project number")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", "-o", type=Path, help="Save report to file")
    parser.add_argument(
        "--post-to-issue", type=int, help="Post report as issue comment"
    )
    parser.add_argument("--status", "-s", help="Filter by status")
    parser.add_argument(
        "--velocity-days",
        type=int,
        default=14,
        help="Days for velocity calculation (default: 14)",
    )
    parser.add_argument(
        "--no-blockers", action="store_true", help="Exclude blockers section"
    )
    parser.add_argument(
        "--no-at-risk", action="store_true", help="Exclude at-risk section"
    )
    parser.add_argument(
        "--no-velocity", action="store_true", help="Exclude velocity section"
    )
    parser.add_argument(
        "--list-projects", action="store_true", help="List available projects"
    )

    args = parser.parse_args()

    # Check authentication
    if not check_gh_auth():
        print("ERROR: gh CLI not authenticated. Run: gh auth login", file=sys.stderr)
        return 1

    # List projects mode
    if args.list_projects:
        projects = list_projects()
        if not projects:
            print("No projects found")
            return 0

        print(f"\n{'#':<5} {'Title':<40} {'Status':<10}")
        print("-" * 60)
        for p in projects:
            status = "Closed" if p.get("closed") else "Open"
            title = str(p.get("title", "Untitled"))[:37]
            if len(title) == 37:
                title += "..."
            print(f"{p.get('number', '?'):<5} {title:<40} {status:<10}")
        return 0

    # Require project number for report
    if not args.project:
        print("ERROR: --project is required (or use --list-projects)", file=sys.stderr)
        return 1

    # Fetch project items
    print(f"Fetching project #{args.project} items...", file=sys.stderr)
    items = get_project_items(args.project, status_filter=args.status)

    if not items:
        print(f"No items found in project #{args.project}")
        return 0

    # Calculate metrics
    metrics = calculate_metrics(items, velocity_days=args.velocity_days)

    # Generate report
    if args.format == "json":
        report = generate_json_report(args.project, items, metrics)
    else:
        report = generate_markdown_report(
            args.project,
            items,
            metrics,
            include_blockers=not args.no_blockers,
            include_at_risk=not args.no_at_risk,
            include_velocity=not args.no_velocity,
        )

    # Output
    if args.output:
        save_report_to_file(report, args.output, args.format)
    elif args.post_to_issue:
        post_report_to_issue(args.post_to_issue, report, run_gh_command)
    else:
        print(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
