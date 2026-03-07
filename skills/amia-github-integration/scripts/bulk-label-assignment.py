#!/usr/bin/env python3
"""
bulk-label-assignment.py - Bulk add or remove labels on GitHub issues.

Finds issues matching a search filter and applies or removes labels in bulk.

Usage:
    python scripts/bulk-label-assignment.py --repo owner/repo --filter "is:issue is:open" --add-label bug
    python scripts/bulk-label-assignment.py --repo owner/repo --filter "is:issue label:triage" --remove-label triage --add-label reviewed
    python scripts/bulk-label-assignment.py --repo owner/repo --filter "is:issue is:open" --add-label P1 --dry-run

Output:
    JSON object with bulk operation results to stdout.

Example output:
    {
        "repo": "owner/repo",
        "filter": "is:issue is:open",
        "matched": 12,
        "updated": 12,
        "add_labels": ["bug"],
        "remove_labels": [],
        "dry_run": false,
        "errors": []
    }

Exit codes (standardized):
    0 - Success, labels applied
    1 - Invalid parameters (no labels specified)
    2 - No matching issues found
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


def find_matching_issues(repo: str, search_filter: str) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Find issues matching the search filter."""
    success, output = run_gh_command([
        "issue", "list", "--repo", repo,
        "--search", search_filter,
        "--json", "number,title",
        "--limit", "200",
    ])
    if not success:
        return None, output
    try:
        return json.loads(output), None
    except json.JSONDecodeError:
        return None, f"Could not parse issues: {output[:200]}"


def apply_labels(
    repo: str,
    search_filter: str,
    add_labels: list[str],
    remove_labels: list[str],
    dry_run: bool = False,
) -> dict[str, Any]:
    """Find matching issues and apply/remove labels."""
    errors: list[str] = []

    issues, err = find_matching_issues(repo, search_filter)
    if err:
        if "not logged in" in err.lower():
            return {"error": True, "message": err, "code": "AUTH_REQUIRED"}
        return {"error": True, "message": err, "code": "API_ERROR"}

    issues = issues or []
    if not issues:
        return {
            "repo": repo,
            "filter": search_filter,
            "matched": 0,
            "updated": 0,
            "add_labels": add_labels,
            "remove_labels": remove_labels,
            "dry_run": dry_run,
            "errors": [],
        }

    updated = 0
    for issue in issues:
        number = issue["number"]
        if dry_run:
            updated += 1
            continue

        cmd = ["issue", "edit", str(number), "--repo", repo]
        for label in add_labels:
            cmd.extend(["--add-label", label])
        for label in remove_labels:
            cmd.extend(["--remove-label", label])

        success, err_msg = run_gh_command(cmd)
        if success:
            updated += 1
        else:
            errors.append(f"Issue #{number}: {err_msg}")

    return {
        "repo": repo,
        "filter": search_filter,
        "matched": len(issues),
        "updated": updated,
        "add_labels": add_labels,
        "remove_labels": remove_labels,
        "dry_run": dry_run,
        "errors": errors,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bulk add or remove labels on GitHub issues.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--filter", required=True, help="GitHub search filter (e.g. 'is:issue is:open')")
    parser.add_argument("--add-label", action="append", default=[], help="Label to add (repeatable)")
    parser.add_argument("--remove-label", action="append", default=[], help="Label to remove (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "bulk-label-assignment", args.output_file)
        sys.exit(1)

    if not args.add_label and not args.remove_label:
        write_output({"error": True, "message": "Specify at least one --add-label or --remove-label"}, "bulk-label-assignment", args.output_file)
        sys.exit(1)

    result = apply_labels(
        repo=args.repo,
        search_filter=args.filter,
        add_labels=args.add_label,
        remove_labels=args.remove_label,
        dry_run=args.dry_run,
    )
    write_output(result, "bulk-label-assignment", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)
    elif result["matched"] == 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
