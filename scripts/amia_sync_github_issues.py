#!/usr/bin/env python3
"""
Integrator Sync GitHub Issues Script

Syncs modules with GitHub Issues:
- Creates issues for new modules
- Updates issue labels for status changes
- Closes issues for removed/completed modules

Usage:
    python3 amia_sync_github_issues.py
    python3 amia_sync_github_issues.py --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError as e:
    raise SystemExit("PyYAML required: pip install pyyaml (or use: uv run --with pyyaml)") from e

# State file locations
PLAN_STATE_FILE = Path(".claude/orchestrator-plan-phase.local.md")
EXEC_STATE_FILE = Path(".claude/orchestrator-exec-phase.local.md")


def parse_frontmatter(file_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter and return (data, body)."""
    if not file_path.exists():
        return {}, ""

    content = file_path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}, content

    end_index = content.find("---", 3)
    if end_index == -1:
        return {}, content

    yaml_content = content[3:end_index].strip()
    body = content[end_index + 3:].strip()

    try:
        data = yaml.safe_load(yaml_content) or {}
        return data, body
    except yaml.YAMLError:
        return {}, content


def write_state_file(file_path: Path, data: dict, body: str) -> bool:
    """Write a state file with YAML frontmatter."""
    try:
        yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)
        content = f"---\n{yaml_content}---\n\n{body}"
        file_path.write_text(content, encoding="utf-8")
        return True
    except Exception as e:
        print(f"ERROR: Failed to write state file: {e}")
        return False


def create_github_issue(module: dict, plan_id: str) -> str | None:
    """Create a GitHub Issue for a module."""
    name = module.get("name", module.get("id"))
    criteria = module.get("acceptance_criteria", "See specifications")
    priority = module.get("priority", "medium")

    body = f"""## Module: {name}

### Description
Implementation of the {name} module.

### Acceptance Criteria
- [ ] {criteria}

### Priority
{priority}

### Related
- Plan ID: {plan_id}
- Module ID: {module.get('id')}
"""

    labels = f"module,priority-{priority},status-todo"

    try:
        result = subprocess.run(
            ["gh", "issue", "create",
             "--title", f"[Module] {name}",
             "--body", body,
             "--label", labels],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if "/issues/" in output:
                return f"#{output.split('/issues/')[-1]}"
        return None
    except Exception:
        return None


def update_issue_labels(issue_num: str, status: str) -> bool:
    """Update issue labels based on module status."""
    issue = issue_num.replace("#", "").strip()
    if not issue.isdigit():
        print(f"ERROR: Invalid issue number: {issue_num!r}")
        return False

    # Map status to labels
    status_labels = {
        "pending": "status-todo",
        "planned": "status-todo",
        "assigned": "status-in-progress",
        "in-progress": "status-in-progress",
        "pending_verification": "status-ai-review",
        "complete": "status-done",
    }

    new_label = status_labels.get(status, "status-todo")

    try:
        # Remove old status labels
        for old_label in status_labels.values():
            subprocess.run(
                ["gh", "issue", "edit", issue, "--remove-label", old_label],
                capture_output=True,
                timeout=10
            )

        # Add new status label
        result = subprocess.run(
            ["gh", "issue", "edit", issue, "--add-label", new_label],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def close_issue(issue_num: str, reason: str) -> bool:
    """Close a GitHub issue."""
    issue = issue_num.replace("#", "").strip()
    if not issue.isdigit():
        print(f"ERROR: Invalid issue number: {issue_num!r}")
        return False

    try:
        result = subprocess.run(
            ["gh", "issue", "close", issue, "-c", reason],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync modules with GitHub Issues"
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")

    args = parser.parse_args()

    # Determine which state file to use
    if EXEC_STATE_FILE.exists():
        state_file = EXEC_STATE_FILE
        modules_key = "modules_status"
    elif PLAN_STATE_FILE.exists():
        state_file = PLAN_STATE_FILE
        modules_key = "modules"
    else:
        print("ERROR: Not in Plan or Orchestration Phase")
        return 1

    data, body = parse_frontmatter(state_file)
    if not data:
        print("ERROR: Could not parse state file")
        return 1

    plan_id = data.get("plan_id", "unknown")
    modules = data.get(modules_key, [])

    if not modules:
        print("No modules to sync")
        return 0

    print(f"Syncing {len(modules)} modules with GitHub Issues...")
    if args.dry_run:
        print("(DRY RUN - no changes will be made)")
    print()

    created = 0
    updated = 0
    closed = 0
    errors = 0

    for module in modules:
        mod_id = module.get("id")
        mod_name = module.get("name", mod_id)
        status = module.get("status", "pending")
        issue = module.get("github_issue")

        # Create issue if needed
        if not issue and status != "removed":
            if args.dry_run:
                print(f"  Would create issue for: {mod_name}")
                created += 1
            else:
                print(f"  Creating issue for: {mod_name}...", end=" ")
                new_issue = create_github_issue(module, plan_id)
                if new_issue:
                    module["github_issue"] = new_issue
                    print(f"✓ {new_issue}")
                    created += 1
                else:
                    print("✗ Failed")
                    errors += 1
            continue

        if not issue:
            continue

        # Update labels for status changes
        if status in ("assigned", "in-progress", "pending_verification", "complete"):
            if args.dry_run:
                print(f"  Would update labels for {issue}: {status}")
                updated += 1
            else:
                print(f"  Updating {issue} labels to {status}...", end=" ")
                if update_issue_labels(issue, status):
                    print("✓")
                    updated += 1
                else:
                    print("✗")
                    errors += 1

        # Close completed issues
        if status == "complete":
            if args.dry_run:
                print(f"  Would close {issue} as complete")
                closed += 1
            else:
                print(f"  Closing {issue}...", end=" ")
                if close_issue(issue, "Module implementation complete"):
                    print("✓")
                    closed += 1
                else:
                    print("✗")
                    errors += 1

    # Write updated state
    if not args.dry_run and created > 0:
        write_state_file(state_file, data, body)

    print()
    print("Summary:")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Closed: {closed}")
    if errors:
        print(f"  Errors: {errors}")

    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
