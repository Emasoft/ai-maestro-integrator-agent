"""
release_governance.py - MANAGER-approval gate for release-pipeline actions.

Entering the release pipeline (``complete -> publish`` / ``complete -> deploy``)
is a NON-EXEMPT Tier-2 governance action. See
``~/.claude/rules/trdd-approval-tiers.md`` (Part B, Tier 2) and
``~/.claude/rules/manager-approval-defaults.md`` (Section Y). A release script
MUST NOT perform a public, production-touching action (``gh release create``,
tag push, ``gh release delete``) until it can prove a MANAGER approval was
recorded.

Proof of approval lives in the approving TRDD's ``## Approval log`` section as a
git-tracked, greppable line, for example:

    - 2026-06-02T11:33:00+0200 — APPROVED by MANAGER (tier 2). Tests passed; EHTs terminal.
    - 2026-06-02T11:33:00+0200 — Requested `complete → publish`. MANAGER reply: APPROVED.

This module only READS that evidence; it never writes it (recording an approval
is the MANAGER's act, not the release script's). Fail-fast: no evidence means
the caller refuses to execute.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple, Union

# A recorded approval entry must contain an explicit APPROVED token.
_APPROVED = re.compile(r"\bAPPROVED\b")
# Keywords that mark a release-pipeline transition in an approval entry.
_RELEASE_KEYWORDS = ("publish", "deploy", "release", "ship")
# The "## Approval log" section header (any heading level, case-insensitive).
_APPROVAL_LOG_HEADER = re.compile(r"^\s*#{1,6}\s*approval\s+log\b", re.IGNORECASE)
# Any markdown heading — used to detect the end of the Approval log section.
_ANY_HEADER = re.compile(r"^\s*#{1,6}\s+\S")
# Start of a markdown bullet entry (its continuation lines are indented).
_BULLET = re.compile(r"^\s*[-*]\s")

# An approving TRDD is a human-authored markdown doc; cap the scan defensively.
_MAX_TRDD_BYTES = 1_000_000


def _bullet_entries(lines: list[str]) -> list[str]:
    """Group section lines into bullet entries (a '- ' line + its continuation).

    This keeps the canonical two-line approval format intact, where the
    transition keyword and the MANAGER's APPROVED reply live on separate
    physical lines of the SAME entry::

        - 2026-06-02T11:30:00+0200 — Requested `complete → deploy` (production).
          MANAGER reply: APPROVED at 11:33. Rationale: tests passed.
    """
    entries: list[str] = []
    current: list[str] = []
    for line in lines:
        if _BULLET.match(line):
            if current:
                entries.append("\n".join(current))
            current = [line]
        elif current:
            current.append(line)
    if current:
        entries.append("\n".join(current))
    # A free-form (bullet-less) log is scanned as a single entry rather than missed.
    if not entries and any(ln.strip() for ln in lines):
        entries.append("\n".join(lines))
    return entries


class ApprovalResult(NamedTuple):
    """Outcome of scanning a TRDD for a recorded release approval."""

    approved: bool
    detail: str
    evidence_line: str


def verify_release_approval(trdd_path: Union[str, Path]) -> ApprovalResult:
    """Return whether ``trdd_path`` records a MANAGER approval for a release.

    A release is approved iff the TRDD has an ``## Approval log`` section
    containing at least one line with an APPROVED token AND a release-pipeline
    keyword (publish/deploy/release/ship). Read-only; never mutates the TRDD.
    """
    path = Path(trdd_path)
    if not path.is_file():
        return ApprovalResult(False, f"approval TRDD not found: {path}", "")
    if path.stat().st_size > _MAX_TRDD_BYTES:
        return ApprovalResult(False, f"approval TRDD too large to scan: {path}", "")

    text = path.read_text(encoding="utf-8", errors="replace")
    section_lines: list[str] = []
    in_log = False
    for raw in text.splitlines():
        if _APPROVAL_LOG_HEADER.match(raw):
            in_log = True
            continue
        if in_log and _ANY_HEADER.match(raw):
            # Reached the next section heading; the Approval log ends here.
            break
        if in_log:
            section_lines.append(raw)

    # A release is approved iff one Approval-log ENTRY contains both an APPROVED
    # token and a release-pipeline keyword. Grouping by entry (not by physical
    # line) supports the canonical two-line "Requested … / MANAGER reply:
    # APPROVED" format while keeping unrelated entries separate.
    for entry in _bullet_entries(section_lines):
        if _APPROVED.search(entry) and any(k in entry.lower() for k in _RELEASE_KEYWORDS):
            evidence = next(
                (ln.strip() for ln in entry.splitlines() if _APPROVED.search(ln)),
                entry.strip().splitlines()[0],
            )
            return ApprovalResult(True, f"recorded release approval in {path.name}", evidence)

    return ApprovalResult(
        False,
        f"no APPROVED release entry in the '## Approval log' of {path.name}",
        "",
    )


def governance_block_message(repo: str, version: str) -> str:
    """Human-readable refusal explaining how to satisfy the Tier-2 gate."""
    return (
        f"GOVERNANCE BLOCK: creating or altering the {repo} {version} release is a "
        "NON-EXEMPT Tier-2 action (entering the release pipeline). It cannot run "
        "without a recorded MANAGER approval.\n"
        "Resolve by ONE of:\n"
        "  1. Obtain a MANAGER approval, ensure it is recorded in the approving "
        "TRDD's '## Approval log' (a line containing APPROVED and publish/deploy), "
        "then re-run with --approval-trdd design/tasks/TRDD-<id>-...md\n"
        "  2. If you are the project owner acting as MANAGER (solo / autonomous "
        'project), re-run with --solo-user-approval "<one-line rationale>".\n'
        "See ~/.claude/rules/trdd-approval-tiers.md (Part B, Tier 2) and "
        "manager-approval-defaults.md (Section Y)."
    )
