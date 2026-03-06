#!/usr/bin/env python3
"""Generate a project status report from GitHub Issues and PRs.

Usage:
    python scripts/generate-project-report.py --repo owner/repo --format markdown
    python scripts/generate-project-report.py --repo owner/repo --format json --output report.md
    python scripts/generate-project-report.py --repo owner/repo --days 14

Exit Codes:
    0 - Success
    1 - Invalid parameters
    2 - Repository not found
    3 - GitHub API error
    4 - Not authenticated with gh CLI
    5 - File write error
    6 - Unexpected error
"""

import argparse
import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone


def run_gh_command(args: list[str]) -> dict:
    """Run a gh CLI command and return parsed JSON output.

    Args:
        args: Arguments to pass to the gh command.

    Returns:
        dict with keys: "success" (bool), "data" (parsed JSON or None), "error" (str or None).
    """
    cmd = ["gh"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        return {"success": False, "data": None, "error": "gh CLI not found. Install from https://cli.github.com/"}
    except subprocess.TimeoutExpired:
        return {"success": False, "data": None, "error": f"Command timed out: {' '.join(cmd)}"}

    if result.returncode != 0:
        stderr = result.stderr.strip()
        if "auth login" in stderr or "not logged" in stderr.lower():
            return {"success": False, "data": None, "error": f"AUTH:{stderr}"}
        if "Could not resolve" in stderr or "not found" in stderr.lower():
            return {"success": False, "data": None, "error": f"NOTFOUND:{stderr}"}
        return {"success": False, "data": None, "error": stderr}

    try:
        data = json.loads(result.stdout) if result.stdout.strip() else []
    except json.JSONDecodeError:
        return {"success": False, "data": None, "error": f"Failed to parse JSON: {result.stdout[:200]}"}

    return {"success": True, "data": data, "error": None}


def fetch_issues(repo: str) -> list[dict]:
    """Fetch all issues (open and closed) from the repository."""
    result = run_gh_command([
        "issue", "list",
        "--repo", repo,
        "--state", "all",
        "--json", "number,title,state,labels,createdAt,closedAt",
        "--limit", "200",
    ])
    if not result["success"]:
        error = result["error"] or "Unknown error"
        if error.startswith("AUTH:"):
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(4)
        if error.startswith("NOTFOUND:"):
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(3)
    return result["data"]


def fetch_prs(repo: str) -> list[dict]:
    """Fetch all PRs (open, merged, closed) from the repository."""
    result = run_gh_command([
        "pr", "list",
        "--repo", repo,
        "--state", "all",
        "--json", "number,title,state,labels,createdAt,mergedAt",
        "--limit", "200",
    ])
    if not result["success"]:
        error = result["error"] or "Unknown error"
        if error.startswith("AUTH:"):
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(4)
        if error.startswith("NOTFOUND:"):
            print(json.dumps({"error": error}), file=sys.stderr)
            sys.exit(2)
        print(json.dumps({"error": error}), file=sys.stderr)
        sys.exit(3)
    return result["data"]


def parse_datetime(dt_str: str) -> datetime:
    """Parse an ISO 8601 datetime string from gh CLI output."""
    # gh outputs formats like 2025-03-05T12:00:00Z
    dt_str = dt_str.replace("Z", "+00:00")
    return datetime.fromisoformat(dt_str)


def compute_stats(issues: list[dict], prs: list[dict], days: int) -> dict:
    """Compute project statistics from issues and PRs.

    Args:
        issues: List of issue dicts from gh CLI.
        prs: List of PR dicts from gh CLI.
        days: Number of days to consider for recent activity.

    Returns:
        Stats dictionary.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)

    # Issue counts
    open_issues = sum(1 for i in issues if i["state"] == "OPEN")
    closed_issues = sum(1 for i in issues if i["state"] == "CLOSED")

    # PR counts
    open_prs = sum(1 for p in prs if p["state"] == "OPEN")
    merged_prs = sum(1 for p in prs if p["state"] == "MERGED")
    closed_prs = sum(1 for p in prs if p["state"] == "CLOSED")

    # Issues by label
    label_counter = Counter()
    for issue in issues:
        for label in issue.get("labels", []):
            label_name = label.get("name", "") if isinstance(label, dict) else str(label)
            if label_name:
                label_counter[label_name] += 1

    # Recent activity
    issues_opened_recent = 0
    issues_closed_recent = 0
    prs_opened_recent = 0
    prs_merged_recent = 0

    for issue in issues:
        created = issue.get("createdAt")
        if created and parse_datetime(created) >= cutoff:
            issues_opened_recent += 1
        closed = issue.get("closedAt")
        if closed and parse_datetime(closed) >= cutoff:
            issues_closed_recent += 1

    for pr in prs:
        created = pr.get("createdAt")
        if created and parse_datetime(created) >= cutoff:
            prs_opened_recent += 1
        merged = pr.get("mergedAt")
        if merged and parse_datetime(merged) >= cutoff:
            prs_merged_recent += 1

    # Blockers: open issues with "blocker" or "priority:critical" label
    blocker_labels = {"blocker", "priority:critical"}
    blockers = []
    for issue in issues:
        if issue["state"] != "OPEN":
            continue
        issue_labels = {
            (label.get("name", "") if isinstance(label, dict) else str(label))
            for label in issue.get("labels", [])
        }
        if issue_labels & blocker_labels:
            blockers.append({"number": issue["number"], "title": issue["title"]})

    return {
        "issues": {"open": open_issues, "closed": closed_issues},
        "prs": {"open": open_prs, "merged": merged_prs, "closed": closed_prs},
        "by_label": dict(label_counter.most_common()),
        "recent_activity": {
            "issues_opened": issues_opened_recent,
            "issues_closed": issues_closed_recent,
            "prs_opened": prs_opened_recent,
            "prs_merged": prs_merged_recent,
        },
        "blockers": blockers,
    }


def generate_markdown(repo: str, stats: dict, days: int) -> str:
    """Generate a markdown report from computed stats.

    Args:
        repo: Repository in owner/repo format.
        stats: Stats dictionary from compute_stats().
        days: Number of days used for recent activity window.

    Returns:
        Markdown string.
    """
    lines = []
    lines.append(f"# Project Report: {repo}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}*")
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Open Issues | {stats['issues']['open']} |")
    lines.append(f"| Closed Issues | {stats['issues']['closed']} |")
    lines.append(f"| Open PRs | {stats['prs']['open']} |")
    lines.append(f"| Merged PRs | {stats['prs']['merged']} |")
    lines.append(f"| Closed PRs | {stats['prs']['closed']} |")
    lines.append("")

    # By Label
    if stats["by_label"]:
        lines.append("## Issues by Label")
        lines.append("")
        lines.append("| Label | Count |")
        lines.append("|-------|-------|")
        for label, count in sorted(stats["by_label"].items(), key=lambda x: -x[1]):
            lines.append(f"| {label} | {count} |")
        lines.append("")

    # Recent Activity
    recent = stats["recent_activity"]
    lines.append(f"## Recent Activity (last {days} days)")
    lines.append("")
    lines.append(f"| Activity | Count |")
    lines.append(f"|----------|-------|")
    lines.append(f"| Issues Opened | {recent['issues_opened']} |")
    lines.append(f"| Issues Closed | {recent['issues_closed']} |")
    lines.append(f"| PRs Opened | {recent['prs_opened']} |")
    lines.append(f"| PRs Merged | {recent['prs_merged']} |")
    lines.append("")

    # Blockers
    lines.append("## Blockers")
    lines.append("")
    if stats["blockers"]:
        for blocker in stats["blockers"]:
            lines.append(f"- **#{blocker['number']}**: {blocker['title']}")
    else:
        lines.append("No blockers found.")
    lines.append("")

    return "\n".join(lines)


def main():
    """CLI entry point for generating project reports."""
    parser = argparse.ArgumentParser(
        description="Generate a project status report from GitHub Issues and PRs.",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository in owner/repo format.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        dest="output_format",
        help="Output format: markdown (default) or json.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output file path to write the report to.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days for recent activity window (default: 7).",
    )

    args = parser.parse_args()

    # Validate --repo format
    if "/" not in args.repo or len(args.repo.split("/")) != 2:
        print(json.dumps({"error": "Invalid --repo format. Expected owner/repo."}), file=sys.stderr)
        sys.exit(1)

    if args.days < 1:
        print(json.dumps({"error": "--days must be a positive integer."}), file=sys.stderr)
        sys.exit(1)

    # Gather data from GitHub
    issues = fetch_issues(args.repo)
    prs = fetch_prs(args.repo)

    # Compute stats
    stats = compute_stats(issues, prs, args.days)

    # Build output
    markdown_str = generate_markdown(args.repo, stats, args.days) if args.output_format == "markdown" else None

    output = {
        "repo": args.repo,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
        "stats": stats,
    }
    if markdown_str is not None:
        output["markdown"] = markdown_str

    # Write to file if requested
    if args.output:
        try:
            content = markdown_str if markdown_str else json.dumps(output, indent=2)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            print(json.dumps({"error": f"Failed to write output file: {e}"}), file=sys.stderr)
            sys.exit(5)

    # Always output JSON to stdout
    print(json.dumps(output, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
