#!/usr/bin/env python3
"""
amia_pre_issue_close_hook.py - GitHub issue closure gate with TDD enforcement.

Prevents premature GitHub issue closure by verifying:
1. PR exists and is linked to issue
2. PR is MERGED (not just created)
3. All issue checkboxes are checked
4. Evidence file exists (optional warning)
5. TDD commit sequence (RED -> GREEN)

IMPORTANT: This is a PreToolUse(Bash) hook. It receives tool_input via stdin as JSON.
The script parses the command and ONLY triggers on `gh issue close` commands.

NO external dependencies - Python 3.8+ stdlib only.

Usage:
    # As PreToolUse hook (stdin JSON):
    echo '{"tool_input":{"command":"gh issue close 42"}}' | python3 amia_pre_issue_close_hook.py

    # Direct invocation (for testing):
    python3 amia_pre_issue_close_hook.py <issue_number>
    python3 amia_pre_issue_close_hook.py 42

Exit codes:
    0 - All checks passed (or non-matching command - allow)
    2 - Block issue closure (checks failed)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def log_message(level: str, message: str, log_file: Path) -> None:
    """Write log entry to orchestrator hook log.

    Args:
        level: Log level (DEBUG, INFO, WARN, ERROR, BLOCKED, PASSED)
        message: Message to log
        log_file: Path to log file
    """
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] [{level}] [pre-issue-close] {message}\n"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(entry)
    except OSError:
        # Silent fail if logging not possible
        pass


def run_gh_command(args: list[str], check: bool = True) -> tuple[int, str, str]:
    """Execute gh CLI command and return result.

    Args:
        args: Command arguments (e.g., ['pr', 'list', '--json', 'number'])
        check: Whether to raise exception on non-zero exit

    Returns:
        Tuple of (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            ["gh"] + args, capture_output=True, text=True, check=check, timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout or "", e.stderr or ""
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return 1, "", str(e)


def check_gh_available() -> tuple[bool, str]:
    """Verify gh CLI is installed and authenticated.

    Returns:
        Tuple of (is_available, error_message)
    """
    # Check gh installed
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True, timeout=5)
    except (
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ):
        return False, "gh CLI not installed. Install from https://cli.github.com/"

    # Check gh authenticated
    returncode, _, _ = run_gh_command(["auth", "status"], check=False)
    if returncode != 0:
        return False, "gh not authenticated. Run 'gh auth login' first."

    return True, ""


def get_linked_prs(issue_number: str) -> tuple[list[dict[str, Any]], str]:
    """Find PRs linked to the issue via keywords.

    Args:
        issue_number: GitHub issue number

    Returns:
        Tuple of (list of PR dicts, error_message)
    """
    search_query = (
        f"closes:#{issue_number} OR fixes:#{issue_number} OR resolves:#{issue_number}"
    )
    returncode, stdout, stderr = run_gh_command(
        ["pr", "list", "--search", search_query, "--json", "number,state,merged"],
        check=False,
    )

    if returncode != 0:
        return [], f"Failed to search PRs: {stderr}"

    try:
        prs = json.loads(stdout) if stdout.strip() else []
        return prs, ""
    except json.JSONDecodeError:
        return [], "Failed to parse PR list JSON"


def get_merged_pr(prs: list[dict[str, Any]]) -> int | None:
    """Find first merged PR from list.

    Args:
        prs: List of PR dictionaries from gh CLI

    Returns:
        PR number if found, None otherwise
    """
    for pr in prs:
        if pr.get("merged") is True:
            return pr.get("number")
    return None


def get_issue_body(issue_number: str) -> tuple[str, str]:
    """Retrieve issue body text.

    Args:
        issue_number: GitHub issue number

    Returns:
        Tuple of (body_text, error_message)
    """
    returncode, stdout, stderr = run_gh_command(
        ["issue", "view", issue_number, "--json", "body", "--jq", ".body"], check=False
    )

    if returncode != 0:
        return "", f"Failed to fetch issue body: {stderr}"

    return stdout.strip(), ""


def count_checkboxes(body: str) -> tuple[int, int]:
    """Count total and unchecked checkboxes in issue body.

    Args:
        body: Issue body markdown text

    Returns:
        Tuple of (unchecked_count, total_count)
    """
    unchecked = len(re.findall(r"- \[ \]", body))
    total = len(re.findall(r"- \[(x| )\]", body))
    return unchecked, total


def get_pr_commits(pr_number: int) -> tuple[list[str], str]:
    """Retrieve commit messages from merged PR.

    Args:
        pr_number: PR number

    Returns:
        Tuple of (list of commit headlines, error_message)
    """
    returncode, stdout, stderr = run_gh_command(
        [
            "pr",
            "view",
            str(pr_number),
            "--json",
            "commits",
            "--jq",
            ".commits[].messageHeadline",
        ],
        check=False,
    )

    if returncode != 0:
        return [], f"Failed to fetch PR commits: {stderr}"

    commits = [line.strip() for line in stdout.strip().split("\n") if line.strip()]
    return commits, ""


def verify_tdd_sequence(commits: list[str]) -> tuple[bool, str, int, int]:
    """Verify TDD commit sequence (RED before GREEN).

    Args:
        commits: List of commit message headlines (newest first from gh CLI)

    Returns:
        Tuple of (is_valid, error_message, red_count, green_count)
    """
    red_commits = [i for i, msg in enumerate(commits) if msg.startswith("RED:")]
    green_commits = [i for i, msg in enumerate(commits) if msg.startswith("GREEN:")]

    red_count = len(red_commits)
    green_count = len(green_commits)

    if red_count == 0:
        return False, "No RED (failing test) commit found", 0, 0

    if green_count == 0:
        return False, "No GREEN (implementation) commit found", red_count, 0

    # gh pr view shows commits newest-first, so GREEN index should be LESS than RED index
    first_red = red_commits[0]
    first_green = green_commits[0]

    if first_green > first_red:
        return (
            False,
            "GREEN commit appears BEFORE RED commit in history",
            red_count,
            green_count,
        )

    return True, "", red_count, green_count


def parse_stdin_json() -> tuple[str | None, str | None]:
    """Parse command from PreToolUse stdin JSON.

    PreToolUse hooks receive tool_input via stdin in JSON format:
    {"tool_input": {"command": "gh issue close 42"}}

    Returns:
        Tuple of (command, issue_number) or (None, None) if not applicable
    """
    if sys.stdin.isatty():
        return None, None

    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            return None, None

        data = json.loads(stdin_data)
        tool_input = data.get("tool_input", {})
        command = tool_input.get("command", "")

        # Check if this is a gh issue close command
        issue_close_match = re.search(r"\bgh\s+issue\s+close\s+(\d+)", command)
        if issue_close_match:
            return command, issue_close_match.group(1)

        # Also match: gh issue close #42
        issue_close_hash = re.search(r"\bgh\s+issue\s+close\s+#(\d+)", command)
        if issue_close_hash:
            return command, issue_close_hash.group(1)

        return command, None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None, None


def main() -> int:
    """Main entry point for pre-issue-close hook.

    Handles two invocation modes:
    1. PreToolUse hook: parses stdin JSON, checks if command is gh issue close
    2. CLI mode: takes issue_number as argument

    Returns:
        Exit code: 0 for success/allow, 2 for block
    """
    # Setup logging first
    project_root = Path(os.environ.get("CLAUDE_PROJECT_ROOT", os.getcwd()))
    log_file = project_root / ".claude" / "orchestrator-hook.log"

    # Try PreToolUse stdin JSON mode first
    command, stdin_issue = parse_stdin_json()

    if command is not None:
        # We received stdin - we're running as a hook
        log_message(
            "FIRED", f"PreToolUse(Bash) - command: {command[:100]}...", log_file
        )

        if stdin_issue is None:
            # Not a gh issue close command - allow
            return 0

        issue_number = stdin_issue
        debug_enabled = os.environ.get("ORCHESTRATOR_DEBUG") == "1"
    else:
        # Fall back to CLI argument mode
        parser = argparse.ArgumentParser(
            description="Verify GitHub issue is ready for closure",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    python3 amia_pre_issue_close_hook.py 42
    python3 amia_pre_issue_close_hook.py 123
            """,
        )
        parser.add_argument("issue_number", help="GitHub issue number to check")
        parser.add_argument("--debug", action="store_true", help="Enable debug logging")

        args = parser.parse_args()
        issue_number = args.issue_number
        debug_enabled = args.debug or os.environ.get("ORCHESTRATOR_DEBUG") == "1"

    # debug_enabled is already set in both branches above
    # log_file is already set at the top of main()

    def debug(msg: str) -> None:
        if debug_enabled:
            log_message("DEBUG", msg, log_file)

    debug(f"Checking issue #{issue_number} for closure readiness")

    # CHECK: gh CLI available
    is_available, error = check_gh_available()
    if not is_available:
        log_message("ERROR", error, log_file)
        print(f"ERROR: {error}", file=sys.stderr)
        return 1

    # CHECK 1: PR exists and linked
    print("Checking for linked PRs...")
    prs, error = get_linked_prs(issue_number)
    if error or not prs:
        log_message(
            "BLOCKED", f"No linked PR found for issue #{issue_number}", log_file
        )
        print(
            f"""
{"=" * 80}
BLOCKED: Cannot close issue #{issue_number} - No linked PR found
{"=" * 80}

Requirements for closing an issue:
1. Create a PR with "Closes #{issue_number}" in the body
2. Get the PR merged (not just created)
3. Ensure all issue checkboxes are checked
4. Create evidence file: evidence/{issue_number}.json

To create a linked PR:
  gh pr create --title "Fix issue #{issue_number}" \\
    --body "Closes #{issue_number}"

{"=" * 80}
        """,
            file=sys.stderr,
        )
        return 2  # Exit code 2 = block for PreToolUse hooks

    pr_numbers = [pr["number"] for pr in prs]
    print(f"  Found linked PRs: {' '.join(map(str, pr_numbers))}")

    # CHECK 2: PR is merged
    merged_pr = get_merged_pr(prs)
    if merged_pr is None:
        open_prs = [pr["number"] for pr in prs if pr.get("state") == "OPEN"]
        log_message(
            "BLOCKED",
            f"No merged PR for issue #{issue_number}. Open PRs: {open_prs}",
            log_file,
        )
        print(
            f"""
{"=" * 80}
BLOCKED: Cannot close issue #{issue_number} - PR not merged
{"=" * 80}

Linked PRs exist but none are merged yet.
Open PRs: {" ".join(map(str, open_prs))}

First, merge the PR:
  gh pr merge <PR_NUMBER> --squash

Then try closing the issue again.

{"=" * 80}
        """,
            file=sys.stderr,
        )
        return 2  # Exit code 2 = block for PreToolUse hooks

    print(f"  PR #{merged_pr} is merged")

    # CHECK 3: Issue checkboxes complete
    print("Checking issue checkboxes...")
    body, error = get_issue_body(issue_number)
    if not error and body:
        unchecked, total = count_checkboxes(body)
        if unchecked > 0:
            log_message(
                "BLOCKED",
                f"Issue #{issue_number} has {unchecked} unchecked checkboxes",
                log_file,
            )
            print(
                f"""
{"=" * 80}
BLOCKED: Cannot close issue #{issue_number} - Unchecked items remain
{"=" * 80}

The issue has {unchecked} of {total} checkboxes unchecked.

Before closing, either:
1. Complete all checklist items
2. Remove items that don't apply
3. Update the issue body to check completed items

To update the issue:
  gh issue edit {issue_number} --body "..."

{"=" * 80}
            """,
                file=sys.stderr,
            )
            return 2  # Exit code 2 = block for PreToolUse hooks

        print(f"  All {total} checkboxes complete")
    else:
        print("  No checkboxes found in issue body")

    # CHECK 4: Evidence file exists (optional)
    print("Checking for evidence file...")
    evidence_dir = project_root / "evidence"
    evidence_file = evidence_dir / f"{issue_number}.json"

    if not evidence_file.exists():
        log_message("WARN", f"No evidence file for issue #{issue_number}", log_file)
        print(
            f"""
{"=" * 80}
WARNING: No evidence file found for issue #{issue_number}
{"=" * 80}

Expected: {evidence_file}

Evidence files document verification results. Consider creating one:
{{
  "verification_id": "ver-{issue_number}",
  "task_id": "issue-{issue_number}",
  "status": "passed",
  "evidence": [
    {{"evidence_type": "exit_code", "value": {{"exit_code": 0, "command": "cargo test"}}}},
    {{"evidence_type": "approval", "value": {{"approver": "@reviewer", "type": "pr_approval"}}}}
  ]
}}

Proceeding anyway (evidence is recommended but not required)...

{"=" * 80}
        """,
            file=sys.stderr,
        )
    else:
        print(f"  Evidence file found: {evidence_file}")
        try:
            evidence_data = json.loads(evidence_file.read_text(encoding="utf-8"))
            status = evidence_data.get("status", "unknown")
            print(f"  Evidence status: {status}")

            if status != "passed":
                log_message(
                    "BLOCKED", f"Evidence status is not 'passed': {status}", log_file
                )
                print(
                    f"""
{"=" * 80}
BLOCKED: Evidence file shows status '{status}', not 'passed'
{"=" * 80}

The evidence file indicates the task did not pass verification.
Review and fix issues before closing the issue.

{"=" * 80}
                """,
                    file=sys.stderr,
                )
                return 2  # Exit code 2 = block for PreToolUse hooks
        except (json.JSONDecodeError, OSError) as e:
            log_message("WARN", f"Evidence file is not valid JSON: {e}", log_file)
            print("  WARNING: Evidence file is not valid JSON", file=sys.stderr)

    # CHECK 5: TDD commit sequence
    print("Checking TDD commit sequence in merged PR...")
    commits, error = get_pr_commits(merged_pr)

    if error or not commits:
        log_message(
            "WARN", f"Could not retrieve commits from PR #{merged_pr}", log_file
        )
        print("  WARNING: Could not verify TDD commit sequence", file=sys.stderr)
    else:
        is_valid, error_msg, red_count, green_count = verify_tdd_sequence(commits)

        if not is_valid:
            log_message(
                "BLOCKED", f"TDD violation in PR #{merged_pr}: {error_msg}", log_file
            )
            commits_preview = "\n".join(commits[:10])
            print(
                f"""
{"=" * 80}
BLOCKED: Cannot close issue #{issue_number} - TDD violation detected
{"=" * 80}

{error_msg}

TDD requires commits in this sequence:
  RED: test for feature     (failing test first)
  GREEN: implement feature  (minimum code to pass)
  REFACTOR: improve feature (optional cleanup)

Your PR commits (newest first):
{commits_preview}

{"=" * 80}
            """,
                file=sys.stderr,
            )
            return 2  # Exit code 2 = block for PreToolUse hooks

        print(f"  TDD commits found: {red_count} RED, {green_count} GREEN")
        print("  TDD sequence verified: RED → GREEN")

    # ALL CHECKS PASSED
    log_message(
        "PASSED", f"All closure checks passed for issue #{issue_number}", log_file
    )

    evidence_status = "Present" if evidence_file.exists() else "Not required"
    tdd_status = (
        f"Verified ({red_count} RED, {green_count} GREEN)"
        if commits and is_valid
        else "Not checked"
    )

    print(f"""
{"=" * 80}
All closure checks PASSED for issue #{issue_number}
{"=" * 80}

Summary:
  PR #{merged_pr} is merged
  All checkboxes complete
  Evidence: {evidence_status}
  TDD sequence: {tdd_status}

Safe to close the issue:
  gh issue close {issue_number}

{"=" * 80}
    """)

    return 0


if __name__ == "__main__":
    sys.exit(main())
