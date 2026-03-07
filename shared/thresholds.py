"""
thresholds.py - Shared constants for Integrator Agent.

These thresholds configure behavior for quality gates,
testing, integration workflows, and output discipline.
"""

import json
import sys
from pathlib import Path
from typing import Any

# Code review thresholds
MAX_PR_SIZE_LINES = 500
MAX_FILES_PER_PR = 20
REVIEW_TIMEOUT_SECONDS = 300

# Quality gate configuration
MIN_TEST_COVERAGE_PERCENT = 80
MAX_LINTER_WARNINGS = 0
MAX_TYPE_ERRORS = 0

# Branch protection
PROTECTED_BRANCHES = frozenset(["main", "master", "release/*"])

# Issue closure requirements
REQUIRE_MERGED_PR = True
REQUIRE_ALL_CHECKBOXES = True
REQUIRE_TEST_EVIDENCE = True
REQUIRE_TDD_COMPLIANCE = True

# GitHub integration
GH_API_TIMEOUT_SECONDS = 30
GH_MAX_RETRIES = 3

# CI/CD thresholds
CI_CHECK_TIMEOUT_SECONDS = 600
MAX_CI_RETRIES = 2


class TechnicalTimeouts:
    """Timeout values in seconds for various operation types."""

    API: int = GH_API_TIMEOUT_SECONDS
    GIT: int = 60
    COMMAND: int = REVIEW_TIMEOUT_SECONDS
    CI: int = CI_CHECK_TIMEOUT_SECONDS


class GitHubThresholds:
    """GitHub-specific thresholds and limits."""

    MAX_PR_SIZE_LINES: int = MAX_PR_SIZE_LINES
    MAX_FILES_PER_PR: int = MAX_FILES_PER_PR
    MAX_RETRIES: int = GH_MAX_RETRIES
    API_TIMEOUT: int = GH_API_TIMEOUT_SECONDS


class WorktreeThresholds:
    """Thresholds and configuration for worktree management."""

    # Port ranges by purpose/service type: (start_port, end_port)
    PORT_RANGES: dict[str, tuple[int, int]] = {
        "review": (8100, 8199),
        "feature": (8200, 8299),
        "bugfix": (8300, 8399),
        "test": (8400, 8499),
        "hotfix": (8500, 8549),
        "refactor": (8550, 8599),
    }

    @property
    def PORT_RANGES_LIST(self) -> list[dict[str, int | str]]:
        """Return port ranges as a list of dicts for registry format."""
        return [
            {"purpose": purpose, "start": start, "end": end}
            for purpose, (start, end) in self.PORT_RANGES.items()
        ]


class OutputThresholds:
    """Output discipline thresholds to minimize token consumption."""

    MAX_STDOUT_LINES: int = 5
    MAX_STDOUT_CHARS: int = 500
    MAX_JSON_ITEMS_INLINE: int = 10


def _build_summary(result: dict[str, Any], script_name: str) -> str:
    """Build a concise 1-line summary from a result dict."""
    if result.get("error"):
        msg = result.get("message", result.get("code", "unknown error"))
        # Truncate long error messages
        if len(str(msg)) > 120:
            msg = str(msg)[:117] + "..."
        return f"[ERROR] {script_name} — {msg}"

    # Build summary from common result fields
    parts = []
    for key in ("total", "total_commits", "matched", "created", "updated",
                "total_scanned", "valid", "invalid", "matching_prs",
                "added_to_project", "all_passed", "bump_type", "new_version",
                "version", "tag"):
        if key in result:
            parts.append(f"{key}={result[key]}")
    summary = ", ".join(parts) if parts else "completed"
    return f"[OK] {script_name} — {summary}"


def write_output(
    result: dict[str, Any],
    script_name: str,
    output_file: str | None = None,
) -> None:
    """Write full JSON to file if --output-file given, print summary to stdout.

    When output_file is provided:
      - Writes full JSON (indent=2) to that file
      - Prints 2-line summary to stdout:
        Line 1: [OK/ERROR] script_name — brief summary
        Line 2: Report: <path>

    When output_file is None (backward compatibility):
      - Prints full JSON to stdout (legacy behavior)
    """
    if output_file is None:
        # Backward compatibility: full JSON to stdout
        print(json.dumps(result, indent=2))
        return

    # Write full JSON to the specified file
    out_path = Path(output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    # Print concise summary to stdout
    summary = _build_summary(result, script_name)
    print(summary, file=sys.stderr)
    print(f"Report: {out_path}", file=sys.stderr)
