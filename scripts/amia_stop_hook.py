#!/usr/bin/env python3
"""
amia_stop_hook.py - Stop Hook for Integrator Agent.

Blocks the integrator agent from exiting with incomplete work. Checks:
1. Pending PRs awaiting review (via gh pr list)
2. GitHub Projects items in "In Progress" or "AI Review" status
3. Claude Tasks with pending/in_progress status (if transcript available)
4. Incomplete quality gates

IMPORTANT: This is a Stop hook. It receives hook data via stdin as JSON.
The script checks for incomplete work and blocks exit if found.

NO shell wrappers - runs via 'python3 script.py' directly.
NO external dependencies - Python 3.8+ stdlib only (except gh CLI).

Usage:
    # As Stop hook (stdin JSON):
    echo '{}' | python3 amia_stop_hook.py

    # Direct invocation (for testing):
    python3 amia_stop_hook.py --check

Exit codes:
    0 - Allow exit (no incomplete work)
    2 - Block exit (incomplete work detected)

Environment variables:
    CLAUDE_PROJECT_ROOT - Project root directory (defaults to current directory)
    ORCHESTRATOR_DEBUG - Enable debug logging (1=enabled, 0=disabled)
    AMIA_PROJECT_NUMBER - GitHub Projects number to check (optional)
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


def get_log_file() -> Path:
    """Get log file path from environment or default location.

    Returns:
        Path to the orchestrator hook log file
    """
    project_root = os.environ.get("CLAUDE_PROJECT_ROOT", os.getcwd())
    return Path(project_root) / ".claude" / "orchestrator-hook.log"


def ensure_log_dir(log_file: Path) -> None:
    """Ensure log directory exists.

    Args:
        log_file: Path to log file
    """
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass  # Silently fail if cannot create directory


def log(level: str, message: str, log_file: Path) -> None:
    """Write log message to log file.

    Args:
        level: Log level (INFO, DEBUG, BLOCKED, ALLOWED, WARN, FIRED)
        message: Log message
        log_file: Path to log file
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] [stop-hook] {message}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except OSError:
        pass  # Silently fail if cannot write to log


def debug(message: str, log_file: Path) -> None:
    """Write debug log message if debug mode enabled.

    Args:
        message: Debug message
        log_file: Path to log file
    """
    if os.environ.get("ORCHESTRATOR_DEBUG", "0") == "1":
        log("DEBUG", message, log_file)


def run_gh_command(args: list[str], timeout: int = 30) -> subprocess.CompletedProcess[str]:
    """Run a gh CLI command safely.

    Args:
        args: Command arguments (without 'gh' prefix)
        timeout: Command timeout in seconds

    Returns:
        CompletedProcess with stdout, stderr, returncode
    """
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            args=["gh"] + args,
            returncode=1,
            stdout="",
            stderr="Command timed out",
        )
    except FileNotFoundError:
        return subprocess.CompletedProcess(
            args=["gh"] + args,
            returncode=1,
            stdout="",
            stderr="gh CLI not found",
        )


def get_repo_info() -> tuple[str, str]:
    """Get owner and repo from current git context.

    Returns:
        Tuple of (owner, repo) or ("", "") if not in a repo
    """
    result = run_gh_command(["repo", "view", "--json", "owner,name"])
    if result.returncode != 0:
        return "", ""

    try:
        data = json.loads(result.stdout)
        owner = data.get("owner", {}).get("login", "")
        repo = data.get("name", "")
        return owner, repo
    except (json.JSONDecodeError, KeyError, TypeError):
        return "", ""


def get_pending_prs(log_file: Path) -> list[dict]:
    """Get list of open PRs awaiting review.

    Args:
        log_file: Path to log file

    Returns:
        List of PR dicts with number, title, state, reviewDecision
    """
    debug("Checking pending PRs...", log_file)

    result = run_gh_command([
        "pr", "list",
        "--state", "open",
        "--json", "number,title,reviewDecision,isDraft",
    ])

    if result.returncode != 0:
        debug(f"Failed to get PRs: {result.stderr}", log_file)
        return []

    try:
        prs = json.loads(result.stdout)
        # Filter to PRs needing attention (not draft, not approved)
        pending = []
        for pr in prs:
            if pr.get("isDraft"):
                continue
            review = pr.get("reviewDecision", "")
            # REVIEW_REQUIRED, CHANGES_REQUESTED, or no review yet
            if review not in ["APPROVED"]:
                pending.append(pr)
        debug(f"Found {len(pending)} pending PRs", log_file)
        return pending
    except (json.JSONDecodeError, TypeError):
        return []


def get_project_items_in_progress(project_number: Optional[int], log_file: Path) -> list[dict]:
    """Get GitHub Projects items in "In Progress" or "AI Review" status.

    Args:
        project_number: GitHub Projects number to check
        log_file: Path to log file

    Returns:
        List of items with title, status, number
    """
    if not project_number:
        debug("No project number configured, skipping project check", log_file)
        return []

    debug(f"Checking project #{project_number} for in-progress items...", log_file)

    owner, repo = get_repo_info()
    if not owner or not repo:
        debug("Could not determine repo info", log_file)
        return []

    # GraphQL query to get project items with status
    query = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        projectV2(number: $number) {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  number
                  title
                }
                ... on PullRequest {
                  number
                  title
                }
              }
              fieldValues(first: 10) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      ... on ProjectV2SingleSelectField {
                        name
                      }
                    }
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
        "-f", f"owner={owner}",
        "-f", f"repo={repo}",
        "-F", f"number={project_number}",
    ], timeout=60)

    if result.returncode != 0:
        debug(f"Failed to query project: {result.stderr}", log_file)
        return []

    try:
        data = json.loads(result.stdout)
        items = data["data"]["repository"]["projectV2"]["items"]["nodes"]

        in_progress = []
        active_statuses = {"In Progress", "AI Review", "Human Review", "Merge/Release", "Working", "Active"}

        for item in items:
            content = item.get("content")
            if not content:
                continue

            # Find Status field value
            status = None
            for fv in item.get("fieldValues", {}).get("nodes", []):
                if fv and fv.get("field", {}).get("name") == "Status":
                    status = fv.get("name")
                    break

            if status and status in active_statuses:
                in_progress.append({
                    "number": content.get("number"),
                    "title": content.get("title"),
                    "status": status,
                })

        debug(f"Found {len(in_progress)} items in progress", log_file)
        return in_progress
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        debug(f"Failed to parse project response: {e}", log_file)
        return []


def check_claude_tasks(log_file: Path) -> list[dict]:
    """Check for pending Claude Tasks in project directory.

    Looks for .claude/tasks/ directory and checks task status files.

    Args:
        log_file: Path to log file

    Returns:
        List of incomplete tasks with id, status, description
    """
    debug("Checking Claude Tasks...", log_file)

    project_root = Path(os.environ.get("CLAUDE_PROJECT_ROOT", os.getcwd()))
    tasks_dir = project_root / ".claude" / "tasks"

    if not tasks_dir.exists():
        debug("No .claude/tasks directory found", log_file)
        return []

    incomplete = []
    active_statuses = {"pending", "in_progress", "blocked", "running"}

    try:
        for task_file in tasks_dir.glob("*.json"):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    task = json.load(f)

                status = task.get("status", "").lower()
                if status in active_statuses:
                    incomplete.append({
                        "id": task.get("id", task_file.stem),
                        "status": status,
                        "description": task.get("description", task.get("title", "Unknown")),
                    })
            except (json.JSONDecodeError, OSError):
                continue

        debug(f"Found {len(incomplete)} incomplete Claude Tasks", log_file)
        return incomplete
    except OSError:
        return []


def check_quality_gates(log_file: Path) -> list[str]:
    """Check for incomplete quality gates.

    Looks for quality gate status files in project directory.

    Args:
        log_file: Path to log file

    Returns:
        List of incomplete gate descriptions
    """
    debug("Checking quality gates...", log_file)

    project_root = Path(os.environ.get("CLAUDE_PROJECT_ROOT", os.getcwd()))
    gates_file = project_root / ".claude" / "quality-gates.json"

    if not gates_file.exists():
        debug("No quality-gates.json found", log_file)
        return []

    try:
        with open(gates_file, "r", encoding="utf-8") as f:
            gates = json.load(f)

        incomplete = []
        for gate in gates.get("gates", []):
            if not gate.get("passed", False):
                incomplete.append(gate.get("name", "Unknown gate"))

        debug(f"Found {len(incomplete)} incomplete quality gates", log_file)
        return incomplete
    except (json.JSONDecodeError, OSError):
        return []


def parse_stdin_json() -> dict:
    """Parse hook input from stdin JSON.

    Stop hooks receive data via stdin in JSON format.

    Returns:
        Parsed JSON dict or empty dict if parsing fails
    """
    if sys.stdin.isatty():
        return {}

    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            return {}
        data = json.loads(stdin_data)
        # Ensure we actually got a dict, not a list/scalar (CC-P1-A0-015)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def output_block_decision(reason: str, details: dict) -> None:
    """Output JSON response to block exit.

    Args:
        reason: Human-readable reason for blocking
        details: Additional details about incomplete work
    """
    response = {
        "decision": "block",
        "reason": reason,
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Incomplete work detected",
            "incompleteWork": details,
        },
    }
    print(json.dumps(response, indent=2))


def main() -> int:
    """Main entry point for stop hook.

    Checks for incomplete work and blocks exit if found.

    Returns:
        Exit code: 0 to allow exit, 2 to block exit
    """
    log_file = get_log_file()
    ensure_log_dir(log_file)

    # Parse stdin (may be empty for Stop hooks)
    _ = parse_stdin_json()

    # Support direct invocation for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        log("INFO", "Running in test mode", log_file)

    log("FIRED", "Stop hook triggered - checking for incomplete work", log_file)

    # Collect all incomplete work
    issues: list[str] = []
    details: dict[str, list[dict[str, Any]] | list[str]] = {}

    # Check 1: Pending PRs awaiting review
    pending_prs = get_pending_prs(log_file)
    if pending_prs:
        issues.append(f"{len(pending_prs)} PR(s) awaiting review")
        details["pending_prs"] = [
            {"number": pr["number"], "title": pr["title"]}
            for pr in pending_prs
        ]

    # Check 2: GitHub Projects items in progress
    project_number_str = os.environ.get("AMIA_PROJECT_NUMBER", "")
    project_number = int(project_number_str) if project_number_str.isdigit() else None
    project_items = get_project_items_in_progress(project_number, log_file)
    if project_items:
        issues.append(f"{len(project_items)} item(s) in progress")
        details["project_items"] = project_items

    # Check 3: Claude Tasks
    claude_tasks = check_claude_tasks(log_file)
    if claude_tasks:
        issues.append(f"{len(claude_tasks)} Claude Task(s) pending")
        details["claude_tasks"] = claude_tasks

    # Check 4: Quality gates
    quality_gates = check_quality_gates(log_file)
    if quality_gates:
        issues.append(f"{len(quality_gates)} quality gate(s) incomplete")
        details["quality_gates"] = quality_gates

    # Decision
    if issues:
        reason = "Cannot exit: " + ", ".join(issues)
        log("BLOCKED", reason, log_file)

        # Print human-readable message to stderr
        print(f"""
================================================================================
BLOCKED: Integration work is incomplete.
================================================================================

{reason}

Details:
""", file=sys.stderr)

        for category, items in details.items():
            print(f"\n{category}:", file=sys.stderr)
            if isinstance(items, list):
                for item in items[:5]:  # Show first 5
                    if isinstance(item, dict):
                        print(f"  - #{item.get('number', 'N/A')}: {item.get('title', item.get('description', 'Unknown'))}", file=sys.stderr)
                    else:
                        print(f"  - {item}", file=sys.stderr)
                if len(items) > 5:
                    print(f"  ... and {len(items) - 5} more", file=sys.stderr)

        print("""
================================================================================
Complete the above work before exiting.
================================================================================
""", file=sys.stderr)

        # Output JSON response
        output_block_decision(reason, details)
        return 2  # Exit code 2 = BLOCKING

    # Allow exit
    log("ALLOWED", "No incomplete work detected - allowing exit", log_file)
    return 0


def _cli_entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _cli_entry()
