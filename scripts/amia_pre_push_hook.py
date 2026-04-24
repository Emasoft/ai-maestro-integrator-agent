#!/usr/bin/env python3
"""
amia_pre_push_hook.py - Branch Protection for Git Push Operations.

Prevents direct pushes to main/master branch and enforces feature branch workflow.
Validates branch naming conventions and provides guidance for proper git workflow.

IMPORTANT: This is a PreToolUse(Bash) hook. It receives tool_input via stdin as JSON.
The script parses the command and ONLY triggers on git push commands.

NO shell wrappers - runs via 'python3 script.py' directly.
NO external dependencies - Python 3.8+ stdlib only.

Usage:
    # As PreToolUse hook (stdin JSON):
    echo '{"tool_input":{"command":"git push"}}' | python3 amia_pre_push_hook.py

    # Direct invocation (for testing):
    python3 amia_pre_push_hook.py --command "git push origin main"

Exit codes:
    0 - Allow (non-push command OR valid feature branch)
    2 - Block push (main/master branch protection)

Environment variables:
    CLAUDE_PROJECT_ROOT - Project root directory (defaults to current directory)
    ORCHESTRATOR_DEBUG - Enable debug logging (1=enabled, 0=disabled)
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


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
        log_entry = f"[{timestamp}] [{level}] [pre-push-hook] {message}\n"
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


def get_current_branch() -> str:
    """Detect current git branch using git command.

    Returns:
        Branch name or "unknown" if not in a git repository
    """
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], capture_output=True, check=True, timeout=5)

        # Check if in a git repository
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            timeout=5,
        )

        # Get current branch name
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            check=True,
            timeout=5,
            text=True,
        )
        return result.stdout.strip()

    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return "unknown"


def check_protected_branch(branch: str, log_file: Path) -> bool:
    """Check if current branch is protected (main/master).

    Args:
        branch: Current branch name
        log_file: Path to log file

    Returns:
        True if branch is protected and push should be blocked
    """
    protected_branches = ["main", "master"]

    if branch in protected_branches:
        log("BLOCKED", f"Direct push to '{branch}' branch blocked", log_file)

        # Output blocking message to stderr
        blocking_message = f"""
================================================================================
BLOCKED: Direct push to '{branch}' branch is not allowed.
================================================================================

Git workflow requires:
1. Create feature branch:  git checkout -b feature/your-feature
2. Make commits on branch
3. Push to feature branch: git push -u origin feature/your-feature
4. Create PR:              gh pr create --title "Feature X" --body "..."
5. Merge via PR:           gh pr merge --squash

This protects the main branch and ensures code review.

To fix:
  git checkout -b feature/$(date +%Y%m%d)-fix
  git push -u origin feature/$(date +%Y%m%d)-fix

================================================================================
"""
        print(blocking_message, file=sys.stderr)
        return True

    return False


def check_branch_naming(branch: str, log_file: Path) -> None:
    """Check branch naming convention and warn if non-standard.

    Args:
        branch: Current branch name
        log_file: Path to log file
    """
    valid_prefixes = ["feature/", "issue-", "fix/", "hotfix/", "release/", "chore/"]
    branch_valid = False

    for prefix in valid_prefixes:
        if branch.startswith(prefix):
            branch_valid = True
            break

    if not branch_valid and branch != "unknown":
        log("WARN", f"Non-standard branch name: {branch}", log_file)

        # Warning only, don't block
        warning_message = f"""
WARNING: Branch '{branch}' doesn't follow naming convention.
Recommended prefixes: feature/, issue-, fix/, hotfix/, release/, chore/
Example: feature/add-authentication

Proceeding anyway...
"""
        print(warning_message, file=sys.stderr)


def parse_stdin_json() -> str | None:
    """Parse command from PreToolUse stdin JSON.

    PreToolUse hooks receive tool_input via stdin in JSON format:
    {"tool_input": {"command": "git push origin main"}}

    Returns:
        The bash command string or None if parsing fails
    """
    if sys.stdin.isatty():
        return None

    try:
        stdin_data = sys.stdin.read()
        if not stdin_data.strip():
            return None

        data: dict[str, object] = json.loads(stdin_data)
        tool_input = data.get("tool_input", {})
        if not isinstance(tool_input, dict):
            return None
        command = tool_input.get("command", "")
        if isinstance(command, str):
            return command
        return None
    except (json.JSONDecodeError, AttributeError, TypeError):
        return None


def is_git_push_command(command: str) -> bool:
    """Check if command is a git push operation.

    Args:
        command: Bash command string

    Returns:
        True if command contains git push
    """
    if not command:
        return False

    # Patterns that indicate git push
    push_patterns = [
        r"\bgit\s+push\b",
        r"\bgit\s+.*\s+push\b",
    ]

    for pattern in push_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True

    return False


def main() -> int:
    """Main entry point for pre-push hook.

    Parses stdin JSON to get the bash command. Only triggers branch protection
    checks if the command is a git push. All other commands pass through.

    Returns:
        Exit code: 0 to allow, 2 to block push
    """
    log_file = get_log_file()
    ensure_log_dir(log_file)

    # Parse command from stdin JSON (PreToolUse hook format)
    command = parse_stdin_json()

    # Support direct invocation for testing
    if command is None and len(sys.argv) > 1:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--command", "-c", help="Command to check")
        args, _ = parser.parse_known_args()
        command = args.command if args.command else ""

    # If we couldn't get a command, allow (fail-open for non-hook invocations)
    if command is None:
        debug("No command received - allowing", log_file)
        return 0

    # Log hook fired
    log("FIRED", f"PreToolUse(Bash) - command: {command[:100]}{'...' if len(command) > 100 else ''}", log_file)

    # Check if this is a git push command
    if not is_git_push_command(command):
        # Not a git push - allow command without branch checks
        debug(f"Not a git push command, allowing: {command[:50]}{'...' if len(command) > 50 else ''}", log_file)
        return 0

    debug("Git push detected - checking branch protection", log_file)

    # Detect current branch
    current_branch = get_current_branch()
    debug(f"Current branch: {current_branch}", log_file)

    # Check if push to protected branch
    if check_protected_branch(current_branch, log_file):
        return 2  # Exit code 2 = BLOCKING

    # Check branch naming convention (warning only)
    check_branch_naming(current_branch, log_file)

    # Allow push
    debug(f"Push allowed on branch: {current_branch}", log_file)
    log("ALLOWED", f"Push allowed on branch: {current_branch}", log_file)

    return 0


def _cli_entry() -> None:
    sys.exit(main())


if __name__ == "__main__":
    _cli_entry()
