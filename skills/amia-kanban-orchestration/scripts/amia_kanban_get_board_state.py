#!/usr/bin/env python3
"""
amia_kanban_get_board_state.py

Get complete Kanban board state with all items grouped by status column.
Part of github-kanban-core skill for AMOA orchestrator.

Usage:
    python3 amia_kanban_get_board_state.py OWNER REPO PROJECT_NUMBER [--json] [--summary]

Arguments:
    OWNER           Repository owner (organization or user)
    REPO            Repository name
    PROJECT_NUMBER  GitHub Project V2 number

Options:
    --json          Output raw JSON instead of formatted table
    --summary       Output only status counts summary

Example:
    python3 amia_kanban_get_board_state.py Emasoft my-repo 1
    python3 amia_kanban_get_board_state.py Emasoft my-repo 1 --summary
"""

import json
import subprocess
import sys
from typing import Any


def run_gh_command(args: list[str]) -> dict[str, Any]:
    """Run gh CLI command and return parsed JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        sys.exit(1)


def get_project_id(owner: str, repo: str, project_number: int) -> str:
    """Get the project node ID from owner, repo, and project number."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          id
          title
        }
      }
    }
    """
    result = run_gh_command([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"owner={owner}",
        "-f", f"repo={repo}",
        "-F", f"number={project_number}",
    ])

    project = result.get("data", {}).get("repository", {}).get("projectV2")
    if not project:
        print(f"Error: Project {project_number} not found in {owner}/{repo}", file=sys.stderr)
        sys.exit(1)

    return project["id"]


def get_board_state(project_id: str) -> dict[str, Any]:
    """Get all items from the project board."""
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          title
          items(first: 100) {
            totalCount
            nodes {
              id
              type
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field { ... on ProjectV2SingleSelectField { name } }
                  }
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field { ... on ProjectV2Field { name } }
                  }
                }
              }
              content {
                ... on Issue {
                  number
                  title
                  state
                  url
                  assignees(first: 5) {
                    nodes { login }
                  }
                  labels(first: 10) {
                    nodes { name }
                  }
                }
                ... on PullRequest {
                  number
                  title
                  state
                  url
                  merged
                }
              }
            }
          }
        }
      }
    }
    """
    return run_gh_command([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"projectId={project_id}",
    ])


def parse_board_state(raw_state: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Parse raw board state into items grouped by status."""
    project = raw_state.get("data", {}).get("node", {})
    items = project.get("items", {}).get("nodes", [])

    # Group items by status
    grouped: dict[str, list[dict[str, Any]]] = {
        "Backlog": [],
        "Todo": [],
        "In Progress": [],
        "AI Review": [],
        "Human Review": [],
        "Merge/Release": [],
        "Done": [],
        "Blocked": [],
        "Unknown": [],
    }

    for item in items:
        # Extract status
        status = "Unknown"
        field_values = item.get("fieldValues", {}).get("nodes", [])
        for fv in field_values:
            if fv.get("field", {}).get("name") == "Status":
                status = fv.get("name", "Unknown")
                break

        # Extract content info
        content = item.get("content", {})
        if not content:
            continue

        parsed_item = {
            "id": item.get("id"),
            "number": content.get("number"),
            "title": content.get("title"),
            "state": content.get("state"),
            "url": content.get("url"),
            "assignees": [a.get("login") for a in content.get("assignees", {}).get("nodes", [])],
            "labels": [label.get("name") for label in content.get("labels", {}).get("nodes", [])],
            "merged": content.get("merged"),
        }

        if status in grouped:
            grouped[status].append(parsed_item)
        else:
            grouped["Unknown"].append(parsed_item)

    return grouped


def print_summary(grouped: dict[str, list[dict[str, Any]]]) -> None:
    """Print status summary."""
    print("\n=== Board Status Summary ===\n")
    total = 0
    for status, items in grouped.items():
        count = len(items)
        total += count
        if count > 0:
            print(f"  {status}: {count}")
    print(f"\n  Total: {total}")

    # Calculate completion
    done = len(grouped.get("Done", []))
    if total > 0:
        percentage = (done / total) * 100
        print(f"  Completion: {percentage:.1f}%")


def print_table(grouped: dict[str, list[dict[str, Any]]]) -> None:
    """Print formatted table of board state."""
    print("\n" + "=" * 80)
    print("KANBAN BOARD STATE")
    print("=" * 80)

    column_order = ["Backlog", "Todo", "In Progress", "AI Review", "Human Review", "Merge/Release", "Blocked", "Done"]

    for status in column_order:
        items = grouped.get(status, [])
        if not items and status not in ["Blocked"]:
            continue

        print(f"\n--- {status} ({len(items)}) ---")

        if not items:
            print("  (empty)")
            continue

        for item in items:
            assignees = ", ".join(item["assignees"]) if item["assignees"] else "unassigned"
            labels = ", ".join(item["labels"][:3]) if item["labels"] else ""
            print(f"  #{item['number']}: {item['title'][:50]}")
            print(f"         Assignees: {assignees}")
            if labels:
                print(f"         Labels: {labels}")

    # Print unknown if any
    unknown = grouped.get("Unknown", [])
    if unknown:
        print(f"\n--- Unknown Status ({len(unknown)}) ---")
        for item in unknown:
            print(f"  #{item['number']}: {item['title'][:50]}")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    owner = sys.argv[1]
    repo = sys.argv[2]
    try:
        project_number = int(sys.argv[3])
    except ValueError:
        print("Error: PROJECT_NUMBER must be an integer", file=sys.stderr)
        sys.exit(1)

    output_json = "--json" in sys.argv
    output_summary = "--summary" in sys.argv

    # Get project ID
    project_id = get_project_id(owner, repo, project_number)

    # Get board state
    raw_state = get_board_state(project_id)

    # Parse into grouped structure
    grouped = parse_board_state(raw_state)

    # Output
    if output_json:
        print(json.dumps(grouped, indent=2))
    elif output_summary:
        print_summary(grouped)
    else:
        print_table(grouped)
        print_summary(grouped)


if __name__ == "__main__":
    main()
