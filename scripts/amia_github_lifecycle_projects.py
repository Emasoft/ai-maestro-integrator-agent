#!/usr/bin/env python3
"""
amia_github_lifecycle_projects.py - Project and PR operations for GitHub lifecycle automation.

This module provides functions for:
- Linking PRs to issues
- Managing GitHub Projects V2 cards
- Moving issues between project columns
- Listing project statuses

Part of the Integrator GitHub Lifecycle Automation suite.
"""

import json
import re
import sys
from typing import Optional

from amia_github_lifecycle_core import (
    run_gh_command,
    get_repo_info,
)

__all__ = [
    "link_pr_to_issue",
    "get_project_id",
    "get_project_field_id",
    "get_project_item_id",
    "move_issue_in_project",
    "list_project_statuses",
]


def link_pr_to_issue(issue_number: int, pr_number: int) -> bool:
    """Link a PR to an issue by adding 'Closes #N' to PR body.

    Returns True if successful.
    """
    # Get current PR body
    result = run_gh_command(["pr", "view", str(pr_number), "--json", "body"])
    if result.returncode != 0:
        print(f"ERROR: Could not get PR #{pr_number}: {result.stderr}", file=sys.stderr)
        return False

    data = json.loads(result.stdout)
    current_body = data.get("body", "")

    # Check if already linked
    close_pattern = rf"(Closes|Fixes|Resolves)\s*#?{issue_number}\b"
    if re.search(close_pattern, current_body, re.IGNORECASE):
        print(f"INFO: PR #{pr_number} already linked to Issue #{issue_number}")
        return True

    # Add closing reference
    new_body = current_body.rstrip() + f"\n\nCloses #{issue_number}"

    result = run_gh_command(["pr", "edit", str(pr_number), "--body", new_body])
    if result.returncode != 0:
        print(f"ERROR: Failed to update PR: {result.stderr}", file=sys.stderr)
        return False

    print(f"LINKED: PR #{pr_number} → Issue #{issue_number}")
    return True


def get_project_id(project_number: int) -> Optional[str]:
    """Get GitHub Projects V2 project ID from project number."""
    owner, repo = get_repo_info()

    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          id
        }
      }
    }
    """

    result = run_gh_command(
        ["api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"repo={repo}", "-F", f"number={project_number}"]
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    try:
        project_id: str = data["data"]["repository"]["projectV2"]["id"]
        return project_id
    except (KeyError, TypeError):
        return None


def get_project_field_id(
    project_id: str, field_name: str = "Status"
) -> tuple[Optional[str], dict[str, str]]:
    """Get field ID and options for a project field.

    Returns (field_id, {option_name: option_id}).
    """
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2SingleSelectField {
                id
                name
                options {
                  id
                  name
                }
              }
            }
          }
        }
      }
    }
    """

    result = run_gh_command(
        ["api", "graphql", "-f", f"query={query}", "-f", f"projectId={project_id}"]
    )

    if result.returncode != 0:
        return None, {}

    data = json.loads(result.stdout)
    try:
        fields = data["data"]["node"]["fields"]["nodes"]
        for f in fields:
            if f and f.get("name") == field_name:
                options = {opt["name"]: opt["id"] for opt in f.get("options", [])}
                return f["id"], options
    except (KeyError, TypeError):
        pass

    return None, {}


def get_project_item_id(project_id: str, issue_number: int) -> Optional[str]:
    """Get the project item ID for an issue in a project."""
    owner, repo = get_repo_info()

    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          projectItems(first: 10) {
            nodes {
              id
              project {
                id
              }
            }
          }
        }
      }
    }
    """

    result = run_gh_command(
        ["api", "graphql", "-f", f"query={query}", "-f", f"owner={owner}", "-f", f"repo={repo}", "-F", f"issueNumber={issue_number}"]
    )

    if result.returncode != 0:
        return None

    data = json.loads(result.stdout)
    try:
        items = data["data"]["repository"]["issue"]["projectItems"]["nodes"]
        for item in items:
            if item["project"]["id"] == project_id:
                item_id: str = item["id"]
                return item_id
    except (KeyError, TypeError):
        pass

    return None


def move_issue_in_project(
    issue_number: int,
    project_number: int,
    status: str,
) -> bool:
    """Move an issue to a different status in GitHub Projects V2.

    Returns True if successful.
    """
    # Get project ID
    project_id = get_project_id(project_number)
    if not project_id:
        print(f"ERROR: Project #{project_number} not found", file=sys.stderr)
        return False

    # Get Status field ID and options
    field_id, options = get_project_field_id(project_id, "Status")
    if not field_id:
        print("ERROR: Status field not found in project", file=sys.stderr)
        return False

    # Find matching status option
    status_id: Optional[str] = None
    for opt_name, opt_id in options.items():
        if opt_name.lower() == status.lower():
            status_id = opt_id
            break

    if not status_id:
        print(
            f"ERROR: Status '{status}' not found. Available: {list(options.keys())}",
            file=sys.stderr,
        )
        return False

    # Get project item ID for this issue
    item_id = get_project_item_id(project_id, issue_number)
    if not item_id:
        print(
            f"ERROR: Issue #{issue_number} not found in project #{project_number}",
            file=sys.stderr,
        )
        return False

    # Update the field value
    mutation = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $valueId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: { singleSelectOptionId: $valueId }
      }) {
        projectV2Item {
          id
        }
      }
    }
    """

    result = run_gh_command(
        ["api", "graphql", "-f", f"query={mutation}", "-f", f"projectId={project_id}", "-f", f"itemId={item_id}", "-f", f"fieldId={field_id}", "-f", f"valueId={status_id}"]
    )
    if result.returncode != 0:
        print(f"ERROR: Failed to move issue: {result.stderr}", file=sys.stderr)
        return False

    print(f"MOVED: Issue #{issue_number} → {status}")
    return True


def list_project_statuses(project_number: int) -> list[str]:
    """List available status options for a project."""
    project_id = get_project_id(project_number)
    if not project_id:
        return []

    _, options = get_project_field_id(project_id, "Status")
    return list(options.keys())
