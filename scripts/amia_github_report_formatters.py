#!/usr/bin/env python3
"""
amia_github_report_formatters.py - Report formatting functions for AMIA GitHub Reports.

This module provides report generation and output functions for GitHub Project status reports.
It handles:
- Markdown report generation with configurable sections
- JSON report generation with structured metrics
- Report posting to GitHub issues
- Report file saving

This is a companion module to amia_github_report.py.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from amia_github_report import ProjectItem, ProjectMetrics

__all__ = [
    "get_blockers",
    "get_at_risk_items",
    "generate_markdown_report",
    "generate_json_report",
    "post_report_to_issue",
    "save_report_to_file",
]


def get_blockers(items: list["ProjectItem"]) -> list["ProjectItem"]:
    """Get list of blocked items.

    Args:
        items: List of project items to filter.

    Returns:
        List of items that are marked as blocked.
    """
    return [item for item in items if item.is_blocked]


def get_at_risk_items(
    items: list["ProjectItem"],
    stale_days: int = 7,
) -> list["ProjectItem"]:
    """Get items at risk (in progress with no recent updates).

    Args:
        items: List of project items to filter.
        stale_days: Number of days without update to consider at-risk.

    Returns:
        List of at-risk items sorted by update time (oldest first).
    """
    now = datetime.now()
    at_risk = []

    for item in items:
        status_lower = (item.status or "").lower()
        if status_lower in ("in progress", "in-progress", "working"):
            if item.updated_at:
                days_since_update = (now - item.updated_at.replace(tzinfo=None)).days
                if days_since_update >= stale_days:
                    at_risk.append(item)

    return sorted(at_risk, key=lambda x: x.updated_at or datetime.min)


def generate_markdown_report(
    project_number: int,
    items: list["ProjectItem"],
    metrics: "ProjectMetrics",
    include_blockers: bool = True,
    include_at_risk: bool = True,
    include_velocity: bool = True,
) -> str:
    """Generate markdown report from project data.

    Args:
        project_number: GitHub Projects V2 project number.
        items: List of project items.
        metrics: Calculated project metrics.
        include_blockers: Whether to include blockers section.
        include_at_risk: Whether to include at-risk section.
        include_velocity: Whether to include velocity section.

    Returns:
        Markdown formatted report string.
    """
    now = datetime.now()
    report_lines = [
        f"# Project #{project_number} Status Report",
        "",
        f"**Generated**: {now.strftime('%Y-%m-%d %H:%M')}",
        f"**Total Items**: {metrics.total_items}",
        "",
    ]

    # Summary table
    report_lines.extend(
        [
            "## Summary",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total Items | {metrics.total_items} |",
            f"| Completed | {metrics.completed_count} ({metrics.completion_rate:.1f}%) |",
            f"| In Progress | {metrics.in_progress_count} |",
            f"| Blocked | {metrics.blocked_count} |",
            f"| At Risk | {metrics.at_risk_count} |",
            "",
        ]
    )

    # Status breakdown
    if metrics.by_status:
        report_lines.extend(
            [
                "## Status Breakdown",
                "",
                "| Status | Count |",
                "|--------|-------|",
            ]
        )
        for status, count in sorted(metrics.by_status.items()):
            report_lines.append(f"| {status} | {count} |")
        report_lines.append("")

    # Velocity
    if include_velocity:
        report_lines.extend(
            [
                "## Velocity",
                "",
                f"- **Items completed per week**: {metrics.velocity_items_per_week:.1f}",
                f"- **Average days to complete**: {metrics.avg_days_to_complete:.1f}",
                f"- **Oldest in-progress item**: {metrics.oldest_in_progress_days} days",
                "",
            ]
        )

    # Blockers
    if include_blockers:
        blockers = get_blockers(items)
        if blockers:
            report_lines.extend(
                [
                    "## Blockers",
                    "",
                ]
            )
            for item in blockers:
                item_ref = f"#{item.number}" if item.number else item.title
                assignees = (
                    ", ".join(item.assignees) if item.assignees else "unassigned"
                )
                report_lines.append(f"- **{item_ref}**: {item.title} ({assignees})")
            report_lines.append("")

    # At-risk items
    if include_at_risk:
        at_risk = get_at_risk_items(items)
        if at_risk:
            report_lines.extend(
                [
                    "## At Risk",
                    "",
                    "Items in progress with no updates in 7+ days:",
                    "",
                ]
            )
            for item in at_risk[:10]:  # Limit to 10
                item_ref = f"#{item.number}" if item.number else item.title
                days_ago = (
                    (now - item.updated_at.replace(tzinfo=None)).days
                    if item.updated_at
                    else "?"
                )
                report_lines.append(
                    f"- **{item_ref}**: {item.title} (last update: {days_ago} days ago)"
                )
            report_lines.append("")

    # Footer
    report_lines.extend(
        [
            "---",
            "*Generated by AMIA (Emasoft Integrator Agent)*",
        ]
    )

    return "\n".join(report_lines)


def generate_json_report(
    project_number: int,
    items: list["ProjectItem"],
    metrics: "ProjectMetrics",
) -> str:
    """Generate JSON report from project data.

    Args:
        project_number: GitHub Projects V2 project number.
        items: List of project items.
        metrics: Calculated project metrics.

    Returns:
        JSON formatted report string.
    """
    now = datetime.now()

    report = {
        "project_number": project_number,
        "generated_at": now.isoformat(),
        "metrics": {
            "total_items": metrics.total_items,
            "completed_count": metrics.completed_count,
            "in_progress_count": metrics.in_progress_count,
            "blocked_count": metrics.blocked_count,
            "at_risk_count": metrics.at_risk_count,
            "completion_rate": metrics.completion_rate,
            "velocity_items_per_week": metrics.velocity_items_per_week,
            "avg_days_to_complete": metrics.avg_days_to_complete,
            "oldest_in_progress_days": metrics.oldest_in_progress_days,
            "by_status": metrics.by_status,
        },
        "blockers": [
            {
                "number": item.number,
                "title": item.title,
                "url": item.url,
                "assignees": item.assignees,
            }
            for item in get_blockers(items)
        ],
        "at_risk": [
            {
                "number": item.number,
                "title": item.title,
                "url": item.url,
                "last_updated": item.updated_at.isoformat()
                if item.updated_at
                else None,
            }
            for item in get_at_risk_items(items)
        ],
        "items": [
            {
                "number": item.number,
                "title": item.title,
                "type": item.content_type,
                "status": item.status,
                "labels": item.labels,
                "assignees": item.assignees,
                "url": item.url,
                "is_blocked": item.is_blocked,
            }
            for item in items
        ],
    }

    return json.dumps(report, indent=2)


def post_report_to_issue(
    issue_number: int,
    report: str,
    run_gh_command: "Callable[[list[str]], subprocess.CompletedProcess[str]]",
) -> bool:
    """Post report as a comment on an issue.

    Args:
        issue_number: GitHub issue number to post to.
        report: Report content to post.
        run_gh_command: Function to execute gh CLI commands.

    Returns:
        True if successful, False otherwise.
    """
    result = run_gh_command(["issue", "comment", str(issue_number), "--body", report])
    if result.returncode != 0:
        print(f"ERROR: Failed to post report: {result.stderr}", file=sys.stderr)
        return False
    print(f"Report posted to issue #{issue_number}")
    return True


def save_report_to_file(
    report: str,
    output_path: Path,
    _format_type: str,
) -> bool:
    """Save report to file.

    Args:
        report: Report content to save.
        output_path: Path to save the report to.
        format_type: Format type (for logging purposes).

    Returns:
        True if successful, False otherwise.
    """
    try:
        output_path.write_text(report, encoding="utf-8")
        print(f"Report saved to {output_path}")
        return True
    except OSError as e:
        print(f"ERROR: Failed to save report: {e}", file=sys.stderr)
        return False
