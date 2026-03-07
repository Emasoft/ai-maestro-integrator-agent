#!/usr/bin/env python3
"""
amia_kanban_check_completion.py

Check if all Kanban board items are complete (for stop hook integration).
Part of github-kanban-core skill for AMOA orchestrator.

Usage:
    python3 amia_kanban_check_completion.py OWNER REPO PROJECT_NUMBER [--verbose] [--json]

Arguments:
    OWNER           Repository owner (organization or user)
    REPO            Repository name
    PROJECT_NUMBER  GitHub Project V2 number

Options:
    --verbose       Show detailed status of all incomplete items
    --json          Output result as JSON

Exit Codes:
    0   All items Done (orchestrator can exit)
    1   Items still in progress (cannot exit)
    2   Blocked items exist (needs attention)

Example:
    python3 amia_kanban_check_completion.py Emasoft my-repo 1
    python3 amia_kanban_check_completion.py Emasoft my-repo 1 --verbose
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


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
    """Get the project node ID."""
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          id
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
        print(f"Error: Project {project_number} not found", file=sys.stderr)
        sys.exit(1)

    return project["id"]


def get_board_items(project_id: str) -> list[dict[str, Any]]:
    """Get all items from the board with their status."""
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
                  state
                  assignees(first: 3) {
                    nodes { login }
                  }
                }
              }
            }
          }
        }
      }
    }
    """
    result = run_gh_command([
        "api", "graphql",
        "-f", f"query={query}",
        "-f", f"projectId={project_id}",
    ])

    items = result.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])
    parsed_items = []

    for item in items:
        content = item.get("content", {})
        if not content:
            continue

        # Get status
        status = "Unknown"
        for fv in item.get("fieldValues", {}).get("nodes", []):
            if fv.get("field", {}).get("name") == "Status":
                status = fv.get("name", "Unknown")
                break

        parsed_items.append({
            "number": content.get("number"),
            "title": content.get("title"),
            "state": content.get("state"),
            "status": status,
            "assignees": [a.get("login") for a in content.get("assignees", {}).get("nodes", [])],
        })

    return parsed_items


def check_completion(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Check if all items are complete."""
    # Count by status
    counts = {
        "Backlog": 0,
        "Todo": 0,
        "In Progress": 0,
        "AI Review": 0,
        "Human Review": 0,
        "Merge/Release": 0,
        "Done": 0,
        "Blocked": 0,
        "Other": 0,
    }

    incomplete = []
    blocked = []

    for item in items:
        status = item["status"]
        if status in counts:
            counts[status] += 1
        else:
            counts["Other"] += 1

        # Track incomplete items (not Backlog, not Done)
        if status in ["Todo", "In Progress", "AI Review", "Human Review", "Merge/Release"]:
            incomplete.append(item)
        elif status == "Blocked":
            blocked.append(item)

    total = sum(counts.values())
    done = counts["Done"]
    backlog = counts["Backlog"]

    # Calculate active work (excludes backlog and done)
    active = total - done - backlog

    result = {
        "can_exit": False,
        "exit_code": 1,
        "reason": "",
        "counts": counts,
        "total": total,
        "done": done,
        "active": active,
        "incomplete_items": incomplete,
        "blocked_items": blocked,
    }

    # Determine exit eligibility
    if blocked:
        result["can_exit"] = False
        result["exit_code"] = 2
        result["reason"] = f"{len(blocked)} blocked item(s) require attention"
    elif incomplete:
        result["can_exit"] = False
        result["exit_code"] = 1
        result["reason"] = f"{len(incomplete)} item(s) still in progress"
    else:
        result["can_exit"] = True
        result["exit_code"] = 0
        result["reason"] = "All active items complete"

    return result


def print_result(result: dict[str, Any], verbose: bool = False) -> None:
    """Print completion check result."""
    print("\n" + "=" * 60)
    print("KANBAN COMPLETION CHECK")
    print("=" * 60)

    counts = result["counts"]
    print("\nStatus Summary:")
    print(f"  Backlog:       {counts['Backlog']}")
    print(f"  Todo:          {counts['Todo']}")
    print(f"  In Progress:   {counts['In Progress']}")
    print(f"  AI Review:     {counts['AI Review']}")
    print(f"  Human Review:  {counts['Human Review']}")
    print(f"  Merge/Release: {counts['Merge/Release']}")
    print(f"  Blocked:       {counts['Blocked']}")
    print(f"  Done:          {counts['Done']}")
    print(f"\n  Total: {result['total']} | Active: {result['active']} | Done: {result['done']}")

    if result["total"] > 0:
        percentage = (result["done"] / result["total"]) * 100
        print(f"  Completion: {percentage:.1f}%")

    print("\n" + "-" * 60)

    if result["can_exit"]:
        print("RESULT: CAN EXIT")
        print(f"Reason: {result['reason']}")
    else:
        print("RESULT: CANNOT EXIT")
        print(f"Reason: {result['reason']}")

        if verbose:
            if result["blocked_items"]:
                print("\nBlocked Items:")
                for item in result["blocked_items"]:
                    assignees = ", ".join(item["assignees"]) if item["assignees"] else "unassigned"
                    print(f"  #{item['number']}: {item['title'][:40]} ({assignees})")

            if result["incomplete_items"]:
                print("\nIncomplete Items:")
                for item in result["incomplete_items"]:
                    assignees = ", ".join(item["assignees"]) if item["assignees"] else "unassigned"
                    print(f"  #{item['number']}: {item['title'][:40]} [{item['status']}] ({assignees})")

    print("=" * 60 + "\n")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check if all Kanban board items are complete.")
    parser.add_argument("owner", help="Repository owner (organization or user)")
    parser.add_argument("repo", help="Repository name")
    parser.add_argument("project_number", type=int, help="GitHub Project V2 number")
    parser.add_argument("--verbose", action="store_true", help="Show detailed status of all incomplete items")
    parser.add_argument("--json", dest="output_json", action="store_true", help="Output result as JSON")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    args = parser.parse_args()

    # Get project items
    project_id = get_project_id(args.owner, args.repo, args.project_number)
    items = get_board_items(project_id)

    # Check completion
    result = check_completion(items)

    # Output
    if args.output_json or args.output_file:
        write_output(result, "amia_kanban_check_completion", args.output_file)
    else:
        print_result(result, args.verbose)

    # Exit with appropriate code
    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()
