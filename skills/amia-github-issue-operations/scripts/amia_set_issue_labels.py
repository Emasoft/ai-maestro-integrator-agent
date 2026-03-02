#!/usr/bin/env python3
"""
amia_set_issue_labels.py - Manage labels on a GitHub issue.

Add, remove, or set labels on an issue. Can auto-create missing labels
with sensible defaults for priority and type labels.

Usage:
    amia_set_issue_labels.py --repo owner/repo --issue 123 --add "bug,P1"
    amia_set_issue_labels.py --repo owner/repo --issue 123 --remove "backlog"
    amia_set_issue_labels.py --repo owner/repo --issue 123 --set "bug,P1,in-progress"
    amia_set_issue_labels.py --repo owner/repo --issue 123 --add "custom-label" --auto-create

Output:
    JSON object with updated labels list to stdout.

Example output:
    {
        "issue": 123,
        "labels": ["bug", "P1", "in-progress"],
        "added": ["in-progress"],
        "removed": [],
        "created": []
    }

Exit codes (standardized):
    0 - Success, labels updated
    1 - Invalid parameters (bad issue number, missing args)
    2 - Resource not found (issue or labels not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import subprocess
import sys
from typing import Any


# Default configurations for common labels
DEFAULT_LABEL_CONFIGS: dict[str, dict[str, str]] = {
    "P0": {"color": "b60205", "description": "Critical priority"},
    "P1": {"color": "d93f0b", "description": "High priority"},
    "P2": {"color": "fbca04", "description": "Medium priority"},
    "P3": {"color": "0e8a16", "description": "Low priority"},
    "P4": {"color": "cfd3d7", "description": "Trivial priority"},
    "bug": {"color": "d73a4a", "description": "Something isn't working"},
    "feature": {"color": "5319e7", "description": "New functionality"},
    "task": {"color": "0075ca", "description": "General task"},
    "docs": {"color": "0075ca", "description": "Documentation"},
    "blocked": {"color": "d73a4a", "description": "Blocked by dependency"},
    "in-progress": {"color": "fbca04", "description": "Work in progress"},
    "ai-review": {"color": "0e8a16", "description": "Ready for AI review"},
    "human-review": {"color": "1d76db", "description": "Ready for human review"},
    "merge-release": {"color": "5319e7", "description": "Ready for merge/release"},
}


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def get_existing_labels(repo: str) -> set[str]:
    """Get all labels that exist in the repository."""
    success, output = run_gh_command(["label", "list", "--repo", repo, "--json", "name", "--limit", "500"])
    if not success:
        return set()
    try:
        labels = json.loads(output)
        return {label["name"] for label in labels}
    except (json.JSONDecodeError, KeyError):
        return set()


def get_issue_labels(repo: str, issue_number: int) -> list[str]:
    """Get current labels on an issue."""
    success, output = run_gh_command(["issue", "view", str(issue_number), "--repo", repo, "--json", "labels"])
    if not success:
        return []
    try:
        data = json.loads(output)
        return [label["name"] for label in data.get("labels", [])]
    except (json.JSONDecodeError, KeyError):
        return []


def create_label(repo: str, name: str) -> bool:
    """Create a label with default or sensible color/description."""
    config = DEFAULT_LABEL_CONFIGS.get(name, {"color": "cfd3d7", "description": f"Label: {name}"})
    success, _ = run_gh_command([
        "label", "create", name,
        "--repo", repo,
        "--color", config["color"],
        "--description", config["description"]
    ])
    return success


def set_issue_labels(
    repo: str,
    issue_number: int,
    add_labels: list[str] | None = None,
    remove_labels: list[str] | None = None,
    set_labels: list[str] | None = None,
    auto_create: bool = False
) -> dict[str, Any]:
    """Manage labels on a GitHub issue."""
    existing_repo_labels = get_existing_labels(repo)
    current_labels = set(get_issue_labels(repo, issue_number))
    created_labels: list[str] = []

    # Determine target labels
    if set_labels is not None:
        target_labels = set(set_labels)
    else:
        target_labels = current_labels.copy()
        if add_labels:
            target_labels.update(add_labels)
        if remove_labels:
            target_labels -= set(remove_labels)

    # Check for missing labels in repo
    missing_labels = target_labels - existing_repo_labels
    if missing_labels:
        if auto_create:
            for label in missing_labels:
                if create_label(repo, label):
                    created_labels.append(label)
                else:
                    return {"error": True, "message": f"Failed to create label: {label}", "code": "LABEL_CREATE_FAILED"}
        else:
            return {"error": True, "message": f"Labels do not exist: {missing_labels}", "code": "LABELS_NOT_FOUND"}

    # Apply labels using gh issue edit
    labels_to_add = target_labels - current_labels
    labels_to_remove = current_labels - target_labels

    # Add labels
    if labels_to_add:
        success, output = run_gh_command([
            "issue", "edit", str(issue_number),
            "--repo", repo,
            "--add-label", ",".join(labels_to_add)
        ])
        if not success:
            return {"error": True, "message": output, "code": "ADD_LABELS_FAILED"}

    # Remove labels
    if labels_to_remove:
        success, output = run_gh_command([
            "issue", "edit", str(issue_number),
            "--repo", repo,
            "--remove-label", ",".join(labels_to_remove)
        ])
        if not success:
            return {"error": True, "message": output, "code": "REMOVE_LABELS_FAILED"}

    return {
        "issue": issue_number,
        "labels": sorted(list(target_labels)),
        "added": sorted(list(labels_to_add)),
        "removed": sorted(list(labels_to_remove)),
        "created": sorted(created_labels)
    }


def parse_labels(labels_str: str | None) -> list[str] | None:
    """Parse comma-separated labels string into list."""
    if not labels_str:
        return None
    return [label.strip() for label in labels_str.split(",") if label.strip()]


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage labels on a GitHub issue.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--issue", type=int, required=True, help="Issue number")
    parser.add_argument("--add", help="Comma-separated labels to add")
    parser.add_argument("--remove", help="Comma-separated labels to remove")
    parser.add_argument("--set", help="Comma-separated labels to set (replaces all)")
    parser.add_argument("--auto-create", action="store_true", help="Auto-create missing labels")

    args = parser.parse_args()

    result = set_issue_labels(
        repo=args.repo,
        issue_number=args.issue,
        add_labels=parse_labels(args.add),
        remove_labels=parse_labels(args.remove),
        set_labels=parse_labels(args.set),
        auto_create=args.auto_create
    )

    print(json.dumps(result, indent=2))

    # Exit with appropriate error code based on error type
    if result.get("error"):
        error_code = result.get("code", "")
        error_msg = result.get("message", "").lower()

        if error_code == "LABELS_NOT_FOUND" or "not found" in error_msg:
            sys.exit(2)  # Resource not found
        elif "auth" in error_msg or "login" in error_msg:
            sys.exit(4)  # Not authenticated
        else:
            sys.exit(3)  # API error


if __name__ == "__main__":
    main()
