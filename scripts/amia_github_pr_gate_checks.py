#!/usr/bin/env python3
"""
amia_github_pr_gate_checks.py - Gate check functions for PR validation.

Contains individual gate check implementations used by amia_github_pr_gate.py.
Each check function validates a specific aspect of PR readiness.

This module is imported by amia_github_pr_gate.py and should not be run directly.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = [
    "GateResult",
    "PRInfo",
    "check_spec_gate",
    "check_tests_gate",
    "check_reviews_gate",
    "check_draft_gate",
    "check_mergeable_gate",
    "check_linked_issues_gate",
]


@dataclass
class GateResult:
    """Result of a single gate check."""

    name: str
    passed: bool
    message: str
    details: list[str] = field(default_factory=list)
    required: bool = True


@dataclass
class PRInfo:
    """Information about a pull request."""

    number: int
    title: str
    body: str
    state: str
    draft: bool
    labels: list[str]
    author: str
    reviewers: list[str]
    approvals: int
    changes_requested: int
    linked_issues: list[int]
    checks_passing: bool
    checks_pending: bool
    mergeable: bool
    head_ref: str
    base_ref: str


def check_spec_gate(pr: PRInfo, project_root: Path) -> GateResult:
    """Check if PR is linked to an approved spec.

    Feature PRs (not bug fixes) should reference an approved design spec.
    """
    result = GateResult(
        name="spec",
        passed=True,
        message="Spec requirement",
        required=True,
    )

    # Skip for bug fixes, docs, chores
    skip_prefixes = ("fix:", "bug:", "docs:", "chore:", "refactor:", "test:", "ci:")
    title_lower = pr.title.lower()
    if any(title_lower.startswith(p) for p in skip_prefixes):
        result.message = "Spec not required (not a feature PR)"
        return result

    # Check for spec reference in body
    spec_pattern = re.compile(
        r"spec:\s*([A-Z]{2,6}-SPEC-\d{8}-[a-f0-9]{8})", re.IGNORECASE
    )
    match = spec_pattern.search(pr.body)

    if not match:
        result.passed = False
        result.message = "No spec referenced"
        result.details.append(
            "Feature PRs should include: spec: PROJ-SPEC-YYYYMMDD-uuid8"
        )
        return result

    spec_uuid = match.group(1)
    result.details.append(f"Referenced spec: {spec_uuid}")

    # Try to find and validate spec status
    # Use amia_design_search.py to check
    search_script = Path(__file__).parent / "amia_design_search.py"
    if search_script.exists():
        cmd = [
            "python3",
            str(search_script),
            "--uuid",
            spec_uuid,
            "--format",
            "json",
            "--design-dir",
            str(project_root / "design"),
        ]
        search_result = subprocess.run(cmd, capture_output=True, text=True)

        if search_result.returncode == 0:
            try:
                docs = json.loads(search_result.stdout)
                if docs:
                    status = docs[0].get("status", "").lower()
                    if status not in ("approved", "implemented"):
                        result.passed = False
                        result.message = f"Spec not approved (status: {status})"
                        result.details.append(
                            "Spec must be in 'approved' or 'implemented' status"
                        )
                    else:
                        result.message = f"Linked to approved spec: {spec_uuid}"
            except json.JSONDecodeError:
                result.details.append("Could not verify spec status")

    return result


def check_tests_gate(pr: PRInfo) -> GateResult:
    """Check if all CI tests are passing."""
    result = GateResult(
        name="tests",
        passed=True,
        message="CI tests",
        required=True,
    )

    if pr.checks_pending:
        result.passed = False
        result.message = "Tests still running"
        result.details.append("Wait for all CI checks to complete")
        return result

    if not pr.checks_passing:
        result.passed = False
        result.message = "Tests failing"
        result.details.append("All CI checks must pass before merge")
        return result

    result.message = "All tests passing"
    return result


def check_reviews_gate(pr: PRInfo, min_approvals: int = 1) -> GateResult:
    """Check if PR has required approvals."""
    result = GateResult(
        name="reviews",
        passed=True,
        message="Review approvals",
        required=True,
    )

    if pr.changes_requested > 0:
        result.passed = False
        result.message = f"Changes requested ({pr.changes_requested})"
        result.details.append("Address all requested changes before merge")
        return result

    if pr.approvals < min_approvals:
        result.passed = False
        result.message = f"Needs {min_approvals - pr.approvals} more approval(s)"
        result.details.append(f"Current: {pr.approvals}/{min_approvals} approvals")
        return result

    result.message = f"{pr.approvals} approval(s)"
    return result


def check_draft_gate(pr: PRInfo) -> GateResult:
    """Check if PR is not a draft."""
    result = GateResult(
        name="draft",
        passed=not pr.draft,
        message="Draft status",
        required=True,
    )

    if pr.draft:
        result.message = "PR is still a draft"
        result.details.append("Mark PR as ready for review")
    else:
        result.message = "PR is ready for review"

    return result


def check_mergeable_gate(pr: PRInfo) -> GateResult:
    """Check if PR is mergeable (no conflicts)."""
    result = GateResult(
        name="mergeable",
        passed=pr.mergeable,
        message="Merge conflicts",
        required=True,
    )

    if not pr.mergeable:
        result.message = "Has merge conflicts"
        result.details.append("Resolve conflicts with base branch")
    else:
        result.message = "No conflicts"

    return result


def check_linked_issues_gate(pr: PRInfo) -> GateResult:
    """Check if PR is linked to issues."""
    result = GateResult(
        name="issues",
        passed=True,
        message="Linked issues",
        required=False,  # Recommended but not required
    )

    if not pr.linked_issues:
        result.passed = False
        result.message = "No linked issues"
        result.details.append("Consider linking to issues with 'Closes #N'")
    else:
        result.message = (
            f"Linked to {len(pr.linked_issues)} issue(s): {pr.linked_issues}"
        )

    return result
