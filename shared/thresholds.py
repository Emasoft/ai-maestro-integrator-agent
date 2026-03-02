"""
thresholds.py - Shared constants for Integrator Agent.

These thresholds configure behavior for quality gates,
testing, and integration workflows.
"""

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
