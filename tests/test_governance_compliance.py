#!/usr/bin/env python3
"""Real governance-compliance tests for the INTEGRATOR plugin (MANAGER audit #15-#19).

Asserts the v4.0.2 governance invariants (R23 frozen-CLI, R24 global memory,
R29/R30 authority model, R37 MAESTRO escalation) DIRECTLY against the plugin's
own source docs + agent definitions — no mocks, no network. Each check greps the
real files, so the suite is green iff the shipped docs encode the current
governance model. It doubles as the verification oracle for the audit fixes:
a failing check names exactly which governance debt is still unpaid.

  uv run --with pytest pytest tests/test_governance_compliance.py -q
  uv run python tests/test_governance_compliance.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
ROLE_BOUNDARIES = PLUGIN_ROOT / "docs" / "ROLE_BOUNDARIES.md"
TEAM_REGISTRY = PLUGIN_ROOT / "docs" / "TEAM_REGISTRY_SPECIFICATION.md"
DOCS = PLUGIN_ROOT / "docs"
AGENTS = PLUGIN_ROOT / "agents"
SKILLS = PLUGIN_ROOT / "skills"
PERSONA = AGENTS / "ai-maestro-integrator-agent-main-agent.md"
SCENARIOS = PLUGIN_ROOT / "tests" / "scenarios" / "governance-scenarios.md"

# Pre-R29 per-agent-approval phrasing that R29/R30 superseded.
OBSOLETE_APPROVAL = re.compile(
    r"with AMAMA approval|Approves AMCOS|Approve/reject AMCOS|Request approval to (?:spawn|replace)"
)
# A bare "user" named as the escalation/approval AUTHORITY. The requirement-author
# "user-specified / user-requested / user-provided" is exempt (R37 scope note), so
# the negative lookahead (?!-) skips "user-...".
ESCALATE_TO_USER = re.compile(r"escalate(?:d)?\s+to\s+(?:the\s+)?user\b(?!-)", re.IGNORECASE)


def check_role_boundaries_no_obsolete_approval() -> str:
    """ROLE_BOUNDARIES.md carries no pre-R29 per-agent AMAMA-approval phrasing (R29/R30, #16)."""
    hits = OBSOLETE_APPROVAL.findall(ROLE_BOUNDARIES.read_text(encoding="utf-8"))
    if hits:
        return f"FAIL: obsolete approval-model phrases still present: {sorted(set(hits))}"
    return "PASS"


def check_role_boundaries_has_r29_r30() -> str:
    """ROLE_BOUNDARIES.md encodes the R29/R30 mandate model (teams + standing mandate) (#16)."""
    text = ROLE_BOUNDARIES.read_text(encoding="utf-8")
    if "R29" not in text or "R30" not in text or "mandate" not in text.lower():
        return "FAIL: R29/R30 mandate model not found in ROLE_BOUNDARIES.md"
    return "PASS"


def check_role_boundaries_header_localized() -> str:
    """ROLE_BOUNDARIES.md is not mislabeled '# AMCOS Role Boundaries' in the integrator plugin (#19)."""
    first = ROLE_BOUNDARIES.read_text(encoding="utf-8").splitlines()[0]
    if "AMCOS Role Boundaries" in first:
        return f"FAIL: header still mislabeled as the AMCOS plugin: {first!r}"
    return "PASS"


def check_team_registry_created_by() -> str:
    """TEAM_REGISTRY no longer attributes team creation to '(always AMCOS)' (R29.1, A2, #17)."""
    if "always AMCOS" in TEAM_REGISTRY.read_text(encoding="utf-8"):
        return "FAIL: TEAM_REGISTRY_SPECIFICATION still says created_by '(always AMCOS)'"
    return "PASS"


def check_no_api_teams_in_docs() -> str:
    """No doc instructs a direct /api/teams/{id}/tasks call (R23 frozen-CLI, #14)."""
    bad = [md.name for md in DOCS.glob("*.md") if "/api/teams/" in md.read_text(encoding="utf-8")]
    if bad:
        return f"FAIL: /api/teams/ endpoint still referenced in docs: {bad}"
    return "PASS"


def check_all_agents_global_memory() -> str:
    """Every agent (main + subagents) wires the GLOBAL janitor memory; none the retired per-plugin skill (R24, MAJOR-2)."""
    missing, stale = [], []
    for agent in sorted(AGENTS.glob("*.md")):
        text = agent.read_text(encoding="utf-8")
        if "janitor-memory-recall" not in text:
            missing.append(agent.name)
        if "integrator-memory" in text:
            stale.append(agent.name)
    if missing or stale:
        return f"FAIL: missing janitor-memory in {missing}; stale integrator-memory in {stale}"
    return "PASS"


def check_no_per_plugin_memory_skill() -> str:
    """The per-plugin integrator-memory-recall/write skills are retired (R24 align-to-fleet, MAJOR-2)."""
    leftovers = [d.name for d in SKILLS.glob("integrator-memory-*") if d.is_dir()]
    if leftovers:
        return f"FAIL: per-plugin memory skill dirs still present: {leftovers}"
    return "PASS"


def check_references_escalate_to_maestro_not_user() -> str:
    """Escalation prose in references/** names the chain/MAESTRO, not a bare 'user' authority (R37, #18)."""
    bad = []
    for md in SKILLS.rglob("*.md"):
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if ESCALATE_TO_USER.search(line):
                bad.append(f"{md.relative_to(PLUGIN_ROOT)}:{i}")
    if bad:
        shown = ", ".join(bad[:8]) + (f" … (+{len(bad) - 8} more)" if len(bad) > 8 else "")
        return f"FAIL: 'escalate to user' authority phrasing remains ({len(bad)}): {shown}"
    return "PASS"


def check_persona_has_governance_section() -> str:
    """The main-agent persona carries the R26-R40 governance section naming the MAESTRO apex (R36/R37, #15)."""
    text = PERSONA.read_text(encoding="utf-8")
    needed = ["Foundational Governance Rules", "MAESTRO", "R37", "R28", "R32"]
    missing = [tok for tok in needed if tok not in text]
    if missing:
        return f"FAIL: persona governance section missing tokens: {missing}"
    return "PASS"


def check_governance_scenarios_present() -> str:
    """tests/scenarios/governance-scenarios.md exists and covers the INTEGRATOR R26-R40 behaviors + release gate (#15)."""
    if not SCENARIOS.is_file():
        return "FAIL: SCEN suite not found at tests/scenarios/governance-scenarios.md"
    text = SCENARIOS.read_text(encoding="utf-8")
    needed = ["SCEN-G01", "SCEN-G11", "R28", "R32", "R36", "R37", "release"]
    missing = [tok for tok in needed if tok not in text]
    if missing:
        return f"FAIL: SCEN suite missing required coverage tokens: {missing}"
    return "PASS"


CHECKS = [
    "check_role_boundaries_no_obsolete_approval",
    "check_role_boundaries_has_r29_r30",
    "check_role_boundaries_header_localized",
    "check_team_registry_created_by",
    "check_no_api_teams_in_docs",
    "check_all_agents_global_memory",
    "check_no_per_plugin_memory_skill",
    "check_references_escalate_to_maestro_not_user",
    "check_persona_has_governance_section",
    "check_governance_scenarios_present",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──
# pytest collects these test_* functions by name; they take no fixtures, so the
# module needs no `import pytest` (and runs fine standalone without pytest present).

def test_role_boundaries_no_obsolete_approval() -> None:
    assert check_role_boundaries_no_obsolete_approval().startswith("PASS")


def test_role_boundaries_has_r29_r30() -> None:
    assert check_role_boundaries_has_r29_r30().startswith("PASS")


def test_role_boundaries_header_localized() -> None:
    assert check_role_boundaries_header_localized().startswith("PASS")


def test_team_registry_created_by() -> None:
    assert check_team_registry_created_by().startswith("PASS")


def test_no_api_teams_in_docs() -> None:
    assert check_no_api_teams_in_docs().startswith("PASS")


def test_all_agents_global_memory() -> None:
    assert check_all_agents_global_memory().startswith("PASS")


def test_no_per_plugin_memory_skill() -> None:
    assert check_no_per_plugin_memory_skill().startswith("PASS")


def test_references_escalate_to_maestro_not_user() -> None:
    assert check_references_escalate_to_maestro_not_user().startswith("PASS")


def test_persona_has_governance_section() -> None:
    assert check_persona_has_governance_section().startswith("PASS")


def test_governance_scenarios_present() -> None:
    assert check_governance_scenarios_present().startswith("PASS")


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in CHECKS:
        try:
            outcome = globals()[name]()
        except Exception as exc:  # a crashing check is a failing check
            outcome = f"ERROR: {exc}"
        doc = (globals()[name].__doc__ or "").strip().splitlines()[0]
        status = "PASS" if outcome.startswith("PASS") else ("ERROR" if outcome.startswith("ERROR") else "FAIL")
        if status != "PASS":
            failures += 1
        results.append((name, status, doc if status == "PASS" else f"{doc} — {outcome}"))

    name_w = max(len(r[0]) for r in results) + 1
    desc_w = max(len(r[2]) for r in results) + 1
    print(f"┏{'━' * name_w}┳{'━' * 8}┳{'━' * desc_w}┓")
    print(f"┃{'Test'.ljust(name_w)}┃{' Status '.ljust(8)}┃{'Description'.ljust(desc_w)}┃")
    print(f"┡{'━' * name_w}╇{'━' * 8}╇{'━' * desc_w}┩")
    for name, status, desc in results:
        print(f"│{name.ljust(name_w)}│ {status.ljust(7)}│{desc.ljust(desc_w)}│")
    print(f"└{'─' * name_w}┴{'─' * 8}┴{'─' * desc_w}┘")
    passed = len(results) - failures
    print(f"{passed}/{len(results)} passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
