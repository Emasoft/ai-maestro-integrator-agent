#!/usr/bin/env python3
"""
amia_kanban_move_card.py

Move a Kanban card to a different status column with validation.
Part of github-kanban-core skill for AMOA orchestrator.

Usage:
    python3 amia_kanban_move_card.py OWNER REPO PROJECT_NUMBER ISSUE_NUMBER NEW_STATUS [--reason "Reason"]

Arguments:
    OWNER           Repository owner (organization or user)
    REPO            Repository name
    PROJECT_NUMBER  GitHub Project V2 number
    ISSUE_NUMBER    Issue number to move
    NEW_STATUS      Target status: Backlog, Todo, "In Progress", "AI Review", "Human Review", "Merge/Release", Done, Blocked

Options:
    --reason        Reason for the status change (added as comment)
    --force         Skip transition validation

Example:
    python3 amia_kanban_move_card.py Emasoft my-repo 1 42 "In Progress" --reason "Starting work"
    python3 amia_kanban_move_card.py Emasoft my-repo 1 42 Blocked --reason "Missing credentials"
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

# Allow imports from the plugin root shared/ directory (depth=3: scripts -> skill -> skills -> root)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output  # noqa: E402

# Valid status transitions
VALID_TRANSITIONS: dict[str, list[str]] = {
    "Backlog": ["Todo"],
    "Todo": ["Backlog", "In Progress", "Blocked"],
    "In Progress": ["Todo", "AI Review", "Blocked"],
    "AI Review": ["In Progress", "Human Review", "Merge/Release", "Blocked"],
    "Human Review": ["In Progress", "Merge/Release", "Blocked"],
    "Merge/Release": ["Done", "Blocked"],
    "Done": [],  # Terminal status
    "Blocked": ["Todo", "In Progress"],
}


def run_gh_command(args: list[str], check: bool = True) -> dict[str, Any] | str:
    """Run gh CLI command and return parsed JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=check,
        )
        if result.returncode != 0 and check:
            print(f"Error: {result.stderr}", file=sys.stderr)
            sys.exit(1)
        try:
            parsed: dict[str, Any] = json.loads(result.stdout)
            return parsed
        except json.JSONDecodeError:
            return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e.stderr}", file=sys.stderr)
        sys.exit(1)


def get_project_info(owner: str, repo: str, project_number: int) -> dict[str, Any]:
    """Get project ID and status field information."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          id
          title
          field(name: "Status") {
            ... on ProjectV2SingleSelectField {
              id
              options { id name }
            }
          }
        }
      }
    }
    """
    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"owner={owner}",
            "-f",
            f"repo={repo}",
            "-F",
            f"number={project_number}",
        ]
    )

    if isinstance(result, str):
        print(f"Error: Unexpected string response: {result}", file=sys.stderr)
        sys.exit(1)
    project = result.get("data", {}).get("repository", {}).get("projectV2")
    if not project:
        print(f"Error: Project {project_number} not found", file=sys.stderr)
        sys.exit(1)

    if not isinstance(project, dict):
        print("Error: Unexpected project format from GraphQL response", file=sys.stderr)
        sys.exit(1)
    return project


def get_item_info(project_id: str, issue_number: int) -> dict[str, Any]:
    """Get project item info for an issue."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          items(first: 100) {
            nodes {
              id
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                }
              }
              content {
                ... on Issue {
                  number
                  title
                }
              }
            }
          }
        }
      }
    }
    """
    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"projectId={project_id}",
        ]
    )

    if isinstance(result, str):
        print(f"Error: Unexpected string response: {result}", file=sys.stderr)
        sys.exit(1)
    items = result.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])

    for item in items:
        content = item.get("content", {})
        if content and content.get("number") == issue_number:
            # Extract current status
            current_status = "Unknown"
            for fv in item.get("fieldValues", {}).get("nodes", []):
                if fv.get("field", {}).get("name") == "Status":
                    current_status = fv.get("name", "Unknown")
                    break

            return {
                "item_id": item.get("id"),
                "current_status": current_status,
                "title": content.get("title"),
            }

    print(f"Error: Issue #{issue_number} not found in project", file=sys.stderr)
    sys.exit(1)


def validate_transition(current: str, target: str) -> bool:
    """Validate if transition is allowed."""
    allowed = VALID_TRANSITIONS.get(current, [])
    return target in allowed


def update_status(
    project_id: str,
    item_id: str,
    field_id: str,
    option_id: str,
) -> bool:
    """Update the item status."""
    query = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId
        itemId: $itemId
        fieldId: $fieldId
        value: { singleSelectOptionId: $optionId }
      }) {
        projectV2Item { id }
      }
    }
    """
    result = run_gh_command(
        [
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-f",
            f"projectId={project_id}",
            "-f",
            f"itemId={item_id}",
            "-f",
            f"fieldId={field_id}",
            "-f",
            f"optionId={option_id}",
        ]
    )

    if isinstance(result, str):
        return False
    return "errors" not in result


def add_comment(
    repo: str, issue_number: int, from_status: str, to_status: str, reason: str | None
) -> None:
    """Add a comment documenting the status change."""
    reason_text = f"\n**Reason:** {reason}" if reason else ""
    body = f"""**Status Change**
From: {from_status}
To: {to_status}{reason_text}
"""
    run_gh_command(
        [
            "issue",
            "comment",
            str(issue_number),
            "--repo",
            repo,
            "--body",
            body,
        ]
    )


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Move a Kanban card to a different status column with validation."
    )
    parser.add_argument("owner", help="Repository owner (organization or user)")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("project_number", type=int, help="GitHub Project V2 number")
    parser.add_argument("issue_number", type=int, help="Issue number to move")
    parser.add_argument("new_status", help="Target status column name")
    parser.add_argument("--reason", help="Reason for the status change (added as comment)")
    parser.add_argument("--force", action="store_true", help="Skip transition validation")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    owner = args.owner
    repo = args.repo
    project_number = args.project_number
    issue_number = args.issue_number
    new_status = args.new_status
    reason = args.reason
    force = args.force

    if new_status not in VALID_TRANSITIONS:
        print(f"Error: Invalid status '{new_status}'", file=sys.stderr)
        print(
            f"Valid statuses: {list(VALID_TRANSITIONS.keys())}",
            file=sys.stderr,
        )
        sys.exit(1)

    # Get project info
    project = get_project_info(owner, repo, project_number)
    project_id = project["id"]
    field_info = project.get("field", {})
    field_id = field_info.get("id")
    options = {opt["name"]: opt["id"] for opt in field_info.get("options", [])}

    if new_status not in options:
        print(f"Error: Status '{new_status}' not found in project", file=sys.stderr)
        print(f"Available statuses: {list(options.keys())}", file=sys.stderr)
        sys.exit(1)

    # Get item info
    item = get_item_info(project_id, issue_number)
    item_id = item["item_id"]
    current_status = item["current_status"]

    print(f"Issue #{issue_number}: {item['title']}")
    print(f"Current status: {current_status}")
    print(f"Target status: {new_status}")

    # Validate transition
    if current_status == new_status:
        print("Already in target status. No change needed.")
        sys.exit(0)

    if not force and not validate_transition(current_status, new_status):
        print(
            f"\nError: Invalid transition from '{current_status}' to '{new_status}'",
            file=sys.stderr,
        )
        print(
            f"Allowed transitions from '{current_status}': {VALID_TRANSITIONS.get(current_status, [])}",
            file=sys.stderr,
        )
        print("\nUse --force to override validation", file=sys.stderr)
        sys.exit(1)

    # Update status
    option_id = options[new_status]
    success = update_status(project_id, item_id, field_id, option_id)

    if success:
        print(f"\nSuccessfully moved to '{new_status}'")

        # Add comment
        add_comment(f"{owner}/{repo}", issue_number, current_status, new_status, reason)
        print("Status change comment added to issue")
        result = {
            "status": "ok",
            "issue": issue_number,
            "from_status": current_status,
            "to_status": new_status,
        }
        write_output(result, "amia_kanban_move_card", args.output_file)
    else:
        result = {"status": "error", "issue": issue_number, "message": "Failed to update status"}
        write_output(result, "amia_kanban_move_card", args.output_file)
        print("Error: Failed to update status", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
