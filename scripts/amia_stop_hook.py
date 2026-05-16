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

Claude Code 2.1.143 caps consecutive Stop-hook blocks at 8 (override via
`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Once the cap is hit, Claude Code ends
the turn anyway. This hook tracks the consecutive block count per session
and, at 5 blocks, includes a friendly heads-up in the response so the user
knows the auto-release is imminent.

Hooks now run without terminal access (2.1.139) — writes to stdout/stderr
go to a captured stream, never directly to the user's terminal, so they
cannot corrupt the prompt.

NO shell wrappers - runs via 'python3 script.py' directly.
NO external dependencies - Python 3.8+ stdlib only (except gh CLI).

Usage:
    # As Stop hook (stdin JSON):
    echo '{"session_id":"abc123"}' | python3 amia_stop_hook.py

    # Direct invocation (for testing):
    python3 amia_stop_hook.py --check

Exit codes:
    0 - Allow exit (no incomplete work)
    2 - Block exit (incomplete work detected)

Environment variables (precedence order):
    CLAUDE_PROJECT_DIR     - Project root directory (Claude Code standard, preferred)
    CLAUDE_PROJECT_ROOT    - Project root directory (legacy fallback)
    CLAUDE_CODE_SESSION_ID - Current session ID (2.1.132+, fallback if stdin lacks it)
    CLAUDE_EFFORT          - Active effort level (2.1.133+) - low|medium|high|max|xhigh
    CLAUDE_CODE_STOP_HOOK_BLOCK_CAP - Max consecutive blocks before auto-release (default 8, set by Claude Code, 2.1.143)
    ORCHESTRATOR_DEBUG     - Enable debug logging (1=enabled, 0=disabled)
    AMIA_PROJECT_NUMBER    - GitHub Projects number to check (optional)
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Default consecutive-block cap that Claude Code 2.1.143+ enforces.
# We use the same default so our soft warning kicks in at 5/8 (62.5%).
_CLAUDE_CODE_DEFAULT_STOP_HOOK_BLOCK_CAP = 8
_SOFT_WARN_AT_FRACTION = 5 / 8  # warn the user at 5 consecutive blocks (when cap is 8)


def get_project_root() -> Path:
    """Resolve the project root directory.

    Precedence (matches Claude Code 2.1.139+ conventions):
      1. $CLAUDE_PROJECT_DIR (Claude Code standard env var; set by the harness
         for both hooks and MCP stdio servers as of 2.1.139)
      2. $CLAUDE_PROJECT_ROOT (legacy fallback; still set in older sessions)
      3. cwd
    """
    return Path(
        os.environ.get("CLAUDE_PROJECT_DIR")
        or os.environ.get("CLAUDE_PROJECT_ROOT")
        or os.getcwd()
    )


def get_log_file() -> Path:
    """Get log file path from environment or default location.

    Returns:
        Path to the orchestrator hook log file
    """
    return get_project_root() / ".claude" / "orchestrator-hook.log"


def get_block_tracking_dir() -> Path:
    """Directory holding per-session consecutive-block counter files.

    One file per session_id, contents = decimal integer (block count).
    Cleaned on every ALLOWED return so files don't accumulate.
    """
    return get_project_root() / ".claude" / ".stop-hook-blocks"


def get_block_cap() -> int:
    """Read the Claude Code 2.1.143+ Stop-hook consecutive-block cap.

    The cap is set by the user via $CLAUDE_CODE_STOP_HOOK_BLOCK_CAP and read
    by Claude Code itself; we read the same value so our soft-warn threshold
    tracks any user override. Defaults to 8 (matches Claude Code default).
    """
    raw = os.environ.get("CLAUDE_CODE_STOP_HOOK_BLOCK_CAP", "").strip()
    if not raw:
        return _CLAUDE_CODE_DEFAULT_STOP_HOOK_BLOCK_CAP
    try:
        value = int(raw)
    except ValueError:
        return _CLAUDE_CODE_DEFAULT_STOP_HOOK_BLOCK_CAP
    # Clamp to a sane range: at least 1, at most 100 (paranoia bound).
    return max(1, min(100, value))


def get_consecutive_block_count(session_id: str, log_file: Path) -> int:
    """Read the current consecutive-block count for a session.

    Returns 0 if the session has never been blocked (or the tracking file
    is missing/corrupt).
    """
    if not session_id:
        return 0
    tracking_dir = get_block_tracking_dir()
    counter = tracking_dir / f"{_sanitize_session_id(session_id)}.count"
    try:
        text = counter.read_text(encoding="utf-8").strip()
        return max(0, int(text))
    except (OSError, ValueError) as exc:
        debug(f"counter read failed for {session_id}: {exc}", log_file)
        return 0


def increment_block_count(session_id: str, log_file: Path) -> int:
    """Increment and persist the consecutive-block count for a session.

    Returns the new count (>=1). Silent no-op (returns 0) if session_id is
    empty or the tracking directory can't be created.
    """
    if not session_id:
        return 0
    tracking_dir = get_block_tracking_dir()
    try:
        tracking_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        debug(f"tracking dir mkdir failed: {exc}", log_file)
        return 0
    counter = tracking_dir / f"{_sanitize_session_id(session_id)}.count"
    current = get_consecutive_block_count(session_id, log_file)
    new_value = current + 1
    try:
        # Atomic write — tmp + rename — so a crash mid-write leaves the prior
        # value intact instead of zeroing the counter.
        tmp = counter.with_suffix(counter.suffix + f".tmp.{os.getpid()}")
        tmp.write_text(str(new_value), encoding="utf-8")
        tmp.replace(counter)
    except OSError as exc:
        debug(f"counter write failed for {session_id}: {exc}", log_file)
        return 0
    debug(f"block counter for {session_id}: {current} -> {new_value}", log_file)
    return new_value


def reset_block_count(session_id: str, log_file: Path) -> None:
    """Delete the consecutive-block counter file for a session.

    Called when we ALLOW the turn to end — the next block will start fresh.
    """
    if not session_id:
        return
    tracking_dir = get_block_tracking_dir()
    counter = tracking_dir / f"{_sanitize_session_id(session_id)}.count"
    try:
        counter.unlink()
        debug(f"block counter for {session_id} cleared", log_file)
    except FileNotFoundError:
        # Normal — no prior block in this session, nothing to clear.
        pass
    except OSError as exc:
        debug(f"counter unlink failed for {session_id}: {exc}", log_file)


def _sanitize_session_id(session_id: str) -> str:
    """Sanitize session_id for use as a filename component.

    Strips path separators and other filesystem-unsafe characters so a
    crafted session_id can't escape the tracking directory.
    """
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)
    return safe[:128] or "unknown"


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

    Stop hooks receive data via stdin in JSON format. The payload commonly
    includes (depending on Claude Code version):
      - session_id        (str)   — stable per-session identifier
      - effort            (dict)  — {"level": "low"|"medium"|"high"|"max"|"xhigh"} (2.1.133+)
      - hook_event_name   (str)   — "Stop"
      - transcript_path   (str)   — path to current session transcript

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


def extract_session_id(stdin_payload: dict) -> str:
    """Resolve session_id from stdin payload then env var fallback.

    Claude Code's stdin payload carries `session_id` directly. As a fallback,
    `$CLAUDE_CODE_SESSION_ID` (added in 2.1.132 for Bash subprocesses) is
    also exposed to hook subprocesses.
    """
    stdin_value = stdin_payload.get("session_id")
    if isinstance(stdin_value, str) and stdin_value:
        return stdin_value
    return os.environ.get("CLAUDE_CODE_SESSION_ID", "")


def extract_effort_level(stdin_payload: dict) -> str:
    """Resolve effort level from stdin payload then env var fallback.

    Added by Claude Code 2.1.133. Hooks receive the active effort level via
    the `effort.level` JSON input field and the `$CLAUDE_EFFORT` env var.
    Returns "" when unknown so callers can branch.
    """
    effort = stdin_payload.get("effort")
    if isinstance(effort, dict):
        level = effort.get("level")
        if isinstance(level, str) and level:
            return level
    return os.environ.get("CLAUDE_EFFORT", "")


def output_block_decision(
    reason: str,
    details: dict,
    block_count: int,
    block_cap: int,
) -> None:
    """Output JSON response to block exit.

    Args:
        reason: Human-readable reason for blocking
        details: Additional details about incomplete work
        block_count: This block's position in the consecutive-block sequence
                     (1 = first block of this session, 2 = second, ...)
        block_cap: Effective $CLAUDE_CODE_STOP_HOOK_BLOCK_CAP (default 8)
    """
    # Claude Code 2.1.143 auto-releases the turn after `block_cap` consecutive
    # blocks. Include a friendly heads-up in the response once we're past 5/8
    # so the user knows the auto-release is imminent and can either complete
    # the work or set $CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=1 to skip the gate.
    soft_warn_threshold = max(1, int(block_cap * _SOFT_WARN_AT_FRACTION))
    annotated_reason = reason
    if block_count >= soft_warn_threshold:
        remaining = max(0, block_cap - block_count)
        annotated_reason = (
            f"{reason} "
            f"(Stop-hook block {block_count}/{block_cap} — "
            f"Claude Code will auto-release the turn after {remaining} more "
            f"block{'s' if remaining != 1 else ''}; set "
            f"$CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=1 to skip this gate immediately)"
        )

    response = {
        "decision": "block",
        "reason": annotated_reason,
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Incomplete work detected",
            "incompleteWork": details,
            "blockCount": block_count,
            "blockCap": block_cap,
        },
    }
    print(json.dumps(response, indent=2))


def main() -> int:
    """Main entry point for stop hook.

    Checks for incomplete work and blocks exit if found. Tracks consecutive
    block count per session (Claude Code 2.1.143 caps at 8 — we annotate the
    response once past 5/8 so the user knows the auto-release is imminent).

    Returns:
        Exit code: 0 to allow exit, 2 to block exit
    """
    log_file = get_log_file()
    ensure_log_dir(log_file)

    # Parse stdin payload. session_id + effort.level are useful even when
    # most fields are empty for direct-invocation testing.
    payload = parse_stdin_json()
    session_id = extract_session_id(payload)
    effort_level = extract_effort_level(payload)

    # Support direct invocation for testing
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        log("INFO", "Running in test mode", log_file)

    session_tag = f"session={session_id or 'unknown'}"
    effort_tag = f"effort={effort_level or 'unknown'}"
    log("FIRED", f"Stop hook triggered ({session_tag}, {effort_tag}) - checking for incomplete work", log_file)

    # Collect all incomplete work
    issues: list[str] = []
    details: dict[str, Any] = {}

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
        # Increment consecutive-block counter for this session (no-op when
        # session_id is empty, e.g. --check mode).
        block_count = increment_block_count(session_id, log_file)
        block_cap = get_block_cap()
        reason = "Cannot exit: " + ", ".join(issues)
        log(
            "BLOCKED",
            f"{reason} ({session_tag}, consecutive={block_count}/{block_cap})",
            log_file,
        )

        # Hooks now run without terminal access (Claude Code 2.1.139) — stderr
        # is captured, never directly written to the user's prompt. Safe to
        # emit a verbose, scannable block message.
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

        soft_warn_threshold = max(1, int(block_cap * _SOFT_WARN_AT_FRACTION))
        if block_count >= soft_warn_threshold and block_count > 0:
            remaining = max(0, block_cap - block_count)
            print(f"""
[ Stop-hook block {block_count}/{block_cap}. Claude Code will auto-release the turn
  after {remaining} more block(s); set $CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=1 to skip. ]
""", file=sys.stderr)

        print("""
================================================================================
Complete the above work before exiting.
================================================================================
""", file=sys.stderr)

        # Output JSON response
        output_block_decision(reason, details, block_count, block_cap)
        return 2  # Exit code 2 = BLOCKING

    # Allow exit — reset the consecutive-block counter so the next blocking
    # event for this session starts fresh.
    reset_block_count(session_id, log_file)
    log(
        "ALLOWED",
        f"No incomplete work detected - allowing exit ({session_tag}, {effort_tag})",
        log_file,
    )
    return 0


def _cli_entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _cli_entry()
