#!/usr/bin/env python3
"""
sync-projects-v2.py - Sync GitHub Projects V2 with repository issues.

Compares items in a GitHub Projects V2 board with repository issues
and syncs them in the specified direction.

Usage:
    uv run python scripts/sync-projects-v2.py --repo owner/repo --project 3 --direction bidirectional
    uv run python scripts/sync-projects-v2.py --repo owner/repo --project 3 --direction to-github --dry-run
    uv run python scripts/sync-projects-v2.py --repo owner/repo --project 3 --direction from-github

Output:
    JSON object with sync results to stdout.

Example output:
    {
        "repo": "owner/repo",
        "project_number": 3,
        "direction": "bidirectional",
        "dry_run": false,
        "project_items": 15,
        "repo_issues": 20,
        "added_to_project": 5,
        "already_synced": 15,
        "errors": []
    }

Exit codes (standardized):
    0 - Success, sync completed
    1 - Invalid parameters (bad direction, missing project)
    2 - Resource not found (repo or project not found)
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


def get_owner_from_repo(repo: str) -> str:
    """Extract owner from owner/repo format."""
    return repo.split("/")[0]


def get_project_items(owner: str, project_number: int) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Get items from a GitHub Projects V2 board."""
    success, output = run_gh_command([
        "project", "item-list", str(project_number),
        "--owner", owner,
        "--format", "json",
    ])
    if not success:
        return None, output
    try:
        data = json.loads(output)
        return data.get("items", []), None
    except json.JSONDecodeError:
        return None, f"Could not parse project items: {output[:200]}"


def get_repo_issues(repo: str) -> tuple[list[dict[str, Any]] | None, str | None]:
    """Get open issues from the repository."""
    success, output = run_gh_command([
        "issue", "list", "--repo", repo,
        "--state", "open",
        "--json", "number,title,url",
        "--limit", "200",
    ])
    if not success:
        return None, output
    try:
        return json.loads(output), None
    except json.JSONDecodeError:
        return None, f"Could not parse issues: {output[:200]}"


def add_issue_to_project(owner: str, project_number: int, issue_url: str) -> tuple[bool, str]:
    """Add an issue to a project board."""
    return run_gh_command([
        "project", "item-add", str(project_number),
        "--owner", owner,
        "--url", issue_url,
    ])


def sync_projects(
    repo: str,
    project_number: int,
    direction: str,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Sync issues between repo and project board."""
    owner = get_owner_from_repo(repo)
    errors: list[str] = []

    # Fetch project items
    project_items, err = get_project_items(owner, project_number)
    if err:
        if "not logged in" in err.lower():
            return {"error": True, "message": err, "code": "AUTH_REQUIRED"}
        if "Could not resolve" in err or "not found" in err.lower():
            return {"error": True, "message": err, "code": "NOT_FOUND"}
        return {"error": True, "message": err, "code": "API_ERROR"}

    # Fetch repo issues
    repo_issues, err = get_repo_issues(repo)
    if err:
        return {"error": True, "message": err, "code": "API_ERROR"}

    project_items = project_items or []
    repo_issues = repo_issues or []

    # Build set of issue URLs already in project
    project_urls: set[str] = set()
    for item in project_items:
        content = item.get("content", {})
        if content and "url" in content:
            project_urls.add(content["url"])

    added_to_project = 0

    if direction in ("to-github", "bidirectional"):
        # Add repo issues not yet in project
        for issue in repo_issues:
            issue_url = issue.get("url", "")
            if issue_url and issue_url not in project_urls:
                if not dry_run:
                    success, err_msg = add_issue_to_project(owner, project_number, issue_url)
                    if not success:
                        errors.append(f"Failed to add #{issue['number']}: {err_msg}")
                        continue
                added_to_project += 1

    return {
        "repo": repo,
        "project_number": project_number,
        "direction": direction,
        "dry_run": dry_run,
        "project_items": len(project_items),
        "repo_issues": len(repo_issues),
        "added_to_project": added_to_project,
        "already_synced": len(project_urls),
        "errors": errors,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sync GitHub Projects V2 with repository issues.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--project", required=True, type=int, help="Project number")
    parser.add_argument("--direction", required=True, choices=["to-github", "from-github", "bidirectional"],
                        help="Sync direction")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without applying")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "sync-projects-v2", args.output_file)
        sys.exit(1)

    result = sync_projects(
        repo=args.repo,
        project_number=args.project,
        direction=args.direction,
        dry_run=args.dry_run,
    )
    write_output(result, "sync-projects-v2", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code == "NOT_FOUND":
            sys.exit(2)
        elif code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
