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
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)

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


# ── GOV-VAL-06 / R23.6 — no direct ai-maestro API calls anywhere in the tree ──
#
# R23.6 draws the line at "endpoint-syntax + actual calls/instructions, NOT the
# word 'API'". A guard on the bare string `/api/` therefore fires on the very
# prose that STATES the prohibition, and gets deleted the first week it cries
# wolf. This tree proves it: 39 raw `/api/` hits, ZERO of them ai-maestro calls
# — file paths (`src/api/auth.py`), globs (`**/api/**`), example Flask routes,
# and `curl https://monitoring.example.com/api/metrics` in teaching references.
# The predecessor check here was that naive form, narrow enough (docs/*.md, one
# endpoint) that it had not bitten yet: it failed on a doc correctly PROHIBITING
# the call, i.e. it punished accurate documentation. Verified, then replaced.
#
# So a violation is the CONJUNCTION: runnable AND an HTTP client AND an
# ai-maestro target. (Definition adopted from the CORE session, which paid four
# false positives to arrive at it.)

# ai-maestro's own port: server.mjs:101 `parseInt(process.env.PORT || '23000')`;
# the analytics reverse proxy is port+1. Read 2026-08-08 from blob af507a81b1c3.
# The authoritative namespace list is security-registry.json — the file GOV-VAL-05
# itself names — not a guess. Read 2026-08-08 from blob 53c09018590e.
AI_MAESTRO_NAMESPACES = (
    "agents", "auth", "governance", "oauth-rotator", "path", "sessions",
    "settings", "system", "teams", "trdd", "v1",
)

HTTP_INVOCATION = re.compile(
    r"""\b(?: curl | wget | http(?:ie)?
            | fetch\s*\( | axios\s*[.(]
            | (?:requests|httpx|aiohttp)\s*\.\s*(?:get|post|put|patch|delete|request)\s*\(
            | urllib | Invoke-WebRequest | XMLHttpRequest )\b""",
    re.VERBOSE | re.IGNORECASE,
)
# An explicit ai-maestro authority: its port, a host naming it, or a base-URL var.
AI_MAESTRO_HOST = re.compile(
    r"(?:localhost|127\.0\.0\.1|\[::1\]):2300[01]\b|\bai-?maestro[\w.-]*(?::\d+)?/|\$\{?AI_?MAESTRO",
    re.IGNORECASE,
)
# A host-relative endpoint in one of ai-maestro's OWN namespaces. Delimiter-anchored
# so `src/api/auth.py` (a file path) cannot match while `"/api/auth"` can.
AI_MAESTRO_RELATIVE = re.compile(
    r"""(?<![\w.-])/api/(?:%s)(?:[/"'`\s?]|$)""" % "|".join(AI_MAESTRO_NAMESPACES)
)
# GitHub is exempt by the persona's own R23 note ("GitHub gh / api.github.com is exempt").
GITHUB_EXEMPT = re.compile(r"api\.github\.com|\bgh\s+api\b|github\.com", re.IGNORECASE)

SCANNED_SUFFIXES = {".md", ".py", ".sh", ".bash", ".zsh", ".js", ".mjs", ".ts", ".json", ".yaml", ".yml"}
# Generated artifacts are not the plugin tree. Caught by the first falsification:
# .mypy_cache/*.json embeds analysed source as one enormous line and produced four
# false positives at `:1` — a scanner that reads its own build output reports noise
# no reader can act on, and a guard nobody can act on gets switched off.
SKIP_DIRS = {
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "venv",
    "node_modules", "__pycache__", ".trashcan", "reports", "reports_dev",
    "docs_dev", "scripts_dev", "tests_dev", "builds_dev", "downloads_dev",
}


def _runnable_lines(path: Path) -> list[tuple[int, str]]:
    """Lines that would actually EXECUTE: inside a md fence, or non-comment in a script."""
    out: list[tuple[int, str]] = []
    in_fence = False
    is_md = path.suffix == ".md"
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if is_md and line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if is_md and not in_fence:
            continue  # prose: R23.6 explicitly permits conceptual references
        if not is_md and line.lstrip().startswith(("#", "//", "*")):
            continue
        out.append((i, line))
    return out


def check_no_direct_ai_maestro_api_calls() -> str:
    """No runnable HTTP call targets the ai-maestro server's /api/* (GOV-VAL-06, R23.6)."""
    bad: list[str] = []
    for path in sorted(PLUGIN_ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        if SKIP_DIRS.intersection(path.parts) or path.resolve() == Path(__file__).resolve():
            # Self-exclusion: this file necessarily CONTAINS the endpoint syntax it
            # bans (the patterns above), so scanning it is the same self-match trap
            # as `ps aux | grep <pattern>` finding its own shell. The falsification
            # plants its violation in a DIFFERENT file so this stays a scoping
            # decision rather than a hole.
            continue
        for lineno, line in _runnable_lines(path):
            if GITHUB_EXEMPT.search(line) or not HTTP_INVOCATION.search(line):
                continue
            if AI_MAESTRO_HOST.search(line) or AI_MAESTRO_RELATIVE.search(line):
                bad.append(f"{path.relative_to(PLUGIN_ROOT)}:{lineno}")
    if bad:
        shown = ", ".join(bad[:6]) + (f" … (+{len(bad) - 6} more)" if len(bad) > 6 else "")
        return f"FAIL: direct ai-maestro /api/* call(s) ({len(bad)}): {shown} — use the frozen CLI layer"
    return "PASS"


def check_governance_stamp_matches_live_spec() -> str:
    """The persona's declared governance blobs still match upstream (GOV-VER-02 drift)."""
    # GOV-VER-02: "a declared version != the live one is a detectable failure". This is
    # the detector. It reports DILIGENCE, not upstream correctness: a differing blob
    # means something moved, never what — re-read and re-stamp, do not just bump the
    # number. Skips honestly offline; a network hiccup must not read as conformance.
    text = PERSONA.read_text(encoding="utf-8")
    want = {
        "design/specs/governance-spec.md": re.search(r"governance-spec\.md`?\s*\*\*v[\d.]+\*\*\s*\(blob `([0-9a-f]+)`\)", text),
        "docs/GOVERNANCE-RULES.md": re.search(r"GOVERNANCE-RULES\.md`? is \*\*v[\d.]+\*\* \(blob `([0-9a-f]+)`\)", text),
    }
    missing = [p for p, m in want.items() if not m]
    if missing:
        return f"FAIL: persona carries no GOV-VER-02 blob stamp for {missing}"
    declared = {p: m.group(1) for p, m in want.items() if m}

    if not shutil.which("gh"):
        return "SKIP: gh CLI missing — cannot read the live spec blobs"
    try:
        r = subprocess.run(
            ["gh", "api", "repos/Emasoft/ai-maestro/git/trees/governance-rules?recursive=1",
             "--jq", '.tree[]|select(.path=="design/specs/governance-spec.md" or '
                     '.path=="docs/GOVERNANCE-RULES.md")|"\\(.path) \\(.sha)"'],
            capture_output=True, text=True, check=False, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return "SKIP: could not reach github to read the live spec blobs"
    if r.returncode != 0:
        return "SKIP: gh could not read the ai-maestro tree (auth or network)"

    live = dict(line.split() for line in r.stdout.strip().splitlines() if " " in line)
    # A stamped path ABSENT from the live tree is drift, not a pass. gh already
    # answered (returncode 0), so this is the API's real view: upstream deleted or
    # renamed the file. Without this branch the comprehension below skips it on
    # `p in live` and the check returns PASS — the stamp would certify a document
    # that no longer exists. That is the one way this detector could report
    # conformance while knowing nothing, so it is spelled out rather than folded
    # into the drift list, whose message ("stamped X != live Y") would be a lie here.
    vanished = sorted(p for p in declared if p not in live)
    if vanished:
        return (f"FAIL: stamped path(s) missing from the live governance-rules tree: {vanished}. "
                "Upstream deleted or renamed them — re-read the spec and re-stamp against "
                "wherever the content moved. Do NOT drop the stamp to make this green.")
    drifted = [
        f"{p}: stamped {sha} != live {live[p][:len(sha)]}"
        for p, sha in declared.items()
        if not live[p].startswith(sha)
    ]
    if drifted:
        return (f"FAIL: governance stamp is STALE ({'; '.join(drifted)}). "
                "This means RE-READ the spec and re-stamp — not that upstream is wrong, "
                "and not a licence to bump the number without reading.")
    return "PASS"


def check_governance_stamp_detector_actually_fires() -> str:
    """The stamp detector's three verdicts all fire — vanished, drifted, and clean."""
    # WHY THIS EXISTS: the check above is green in the ONE state that never changes
    # (both paths present and matching). Its two FAIL verdicts are the whole point of
    # having it, and neither runs in normal operation — so a refactor could delete or
    # invert them and every suite would stay green until the rare day upstream actually
    # moves. A branch with no coverage is silence, not evidence. This drives the real
    # function through a substituted `subprocess.run` so all three verdicts execute
    # offline, on every run, with no network and nothing to skip.
    stamped = {
        "design/specs/governance-spec.md": "89c5db5690126efd7488cef7da0298698b45528b",
        "docs/GOVERNANCE-RULES.md": "ceb4ac163bc00270d8e936dd18aafadd2fbbaefd",
    }
    if not shutil.which("gh"):
        return "SKIP: gh CLI missing — the detector short-circuits before the tree read"

    class _Result:
        def __init__(self, stdout: str) -> None:
            self.returncode = 0
            self.stdout = stdout
            self.stderr = ""

    def _tree(paths: dict[str, str]) -> str:
        return "".join(f"{p} {sha}\n" for p, sha in paths.items())

    def _responder(paths: dict[str, str]):  # type: ignore[no-untyped-def]
        """A stand-in for subprocess.run that answers with exactly this tree."""
        def run(*args: object, **kwargs: object) -> _Result:
            del args, kwargs  # the detector's argv is not under test here
            return _Result(_tree(paths))
        return run

    # The persona's own stamp is the input, so a re-stamp must not silently break this
    # check: read the live blobs the detector would compare against out of the file
    # rather than hardcoding them a second time. Only the SHAPE of each response is
    # fixed here — which paths are present, and whether their blobs agree.
    text = PERSONA.read_text(encoding="utf-8")
    spec = re.search(r"governance-spec\.md`?\s*\*\*v[\d.]+\*\*\s*\(blob `([0-9a-f]+)`\)", text)
    rules = re.search(r"GOVERNANCE-RULES\.md`? is \*\*v[\d.]+\*\* \(blob `([0-9a-f]+)`\)", text)
    if not (spec and rules):
        return "FAIL: persona carries no GOV-VER-02 stamp to drive the detector with"
    live = {
        "design/specs/governance-spec.md": spec.group(1) + stamped[
            "design/specs/governance-spec.md"][len(spec.group(1)):],
        "docs/GOVERNANCE-RULES.md": rules.group(1) + stamped[
            "docs/GOVERNANCE-RULES.md"][len(rules.group(1)):],
    }
    cases = {
        # path absent from the tree -> the branch this check was written for
        "vanished": ({k: v for k, v in live.items() if "GOVERNANCE-RULES" not in k},
                     "FAIL: stamped path(s) missing"),
        # present but a different blob -> ordinary drift
        "drifted": ({**live, "docs/GOVERNANCE-RULES.md": "deadbeef" * 5},
                    "FAIL: governance stamp is STALE"),
        # both present and matching -> the only green state
        "clean": (live, "PASS"),
    }
    real_run = subprocess.run
    bad = []
    try:
        for name, (tree, want) in cases.items():
            subprocess.run = _responder(tree)  # type: ignore[assignment]
            got = check_governance_stamp_matches_live_spec()
            if not got.startswith(want):
                bad.append(f"{name}: wanted {want!r}, got {got[:60]!r}")
    finally:
        subprocess.run = real_run  # type: ignore[assignment]
    if bad:
        return f"FAIL: stamp detector verdicts wrong ({'; '.join(bad)})"
    return "PASS"


def check_main_agent_omits_model_pin() -> str:
    """The main agent does NOT pin `model:` (RP-MODEL-01, ai-maestro#136)."""
    for line in PERSONA.read_text(encoding="utf-8").splitlines():
        if line.startswith("model:"):
            return f"FAIL: main agent still pins {line.strip()!r} — RP-MODEL-01 says omit it"
        if line.strip() == "---" and line != PERSONA.read_text(encoding="utf-8").splitlines()[0]:
            break  # end of frontmatter
    return "PASS"


def check_skill_menu_covers_every_skill() -> str:
    """The main agent's skill menu lists EVERY shipped skill, and no phantom (RP-SKILL-MENU-01)."""
    # Drift is checked in BOTH directions on purpose. A missing entry hides a real
    # capability — a reader takes the menu's silence as "we don't have that". A
    # phantom entry is worse: it sends the agent to load a skill that isn't there.
    on_disk = {d.name for d in SKILLS.iterdir() if d.is_dir() and d.name.startswith("amia-")}
    text = PERSONA.read_text(encoding="utf-8")
    listed = set(re.findall(r"`(amia-[a-z0-9-]+)`\s*\|", text))
    missing = sorted(on_disk - listed)
    phantom = sorted(listed - on_disk)
    if missing or phantom:
        return f"FAIL: menu drift — missing {missing}; phantom {phantom}"
    return "PASS"


def check_async_approval_fields_taught() -> str:
    """TRDD-authoring guidance teaches the async-approval fields, not the deprecated tier."""
    # TRDD-O16UGID8: an agent whose choice trees predate the async model WAITS
    # where the model says author-as-planned-and-proceed.
    hits = [p for p in SKILLS.rglob("*.md")
            if "min-approval-requirement" in p.read_text(encoding="utf-8")
            and "mandate:" in p.read_text(encoding="utf-8")]
    if not hits:
        return "FAIL: no skill teaches min-approval-requirement + mandate (async model absent)"
    return "PASS"


def check_no_deprecated_approval_tier() -> str:
    """Nothing uses the deprecated `approval-tier: N` field (superseded by min-approval-requirement)."""
    bad = []
    for p in list(PLUGIN_ROOT.glob("design/**/*.md")) + list(SKILLS.rglob("*.md")):
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^approval-tier:\s*\d", line):
                bad.append(f"{p.relative_to(PLUGIN_ROOT)}:{i}")
    if bad:
        return f"FAIL: deprecated approval-tier still used: {bad}"
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
    "check_no_direct_ai_maestro_api_calls",
    "check_governance_stamp_matches_live_spec",
    "check_governance_stamp_detector_actually_fires",
    "check_main_agent_omits_model_pin",
    "check_skill_menu_covers_every_skill",
    "check_async_approval_fields_taught",
    "check_no_deprecated_approval_tier",
    "check_all_agents_global_memory",
    "check_no_per_plugin_memory_skill",
    "check_references_escalate_to_maestro_not_user",
    "check_persona_has_governance_section",
    "check_governance_scenarios_present",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──
# pytest collects these test_* functions by name; they take no fixtures, so the
# module needs no `import pytest` (and runs fine standalone without pytest present).

def test_main_agent_omits_model_pin() -> None:
    assert check_main_agent_omits_model_pin().startswith("PASS")


def test_skill_menu_covers_every_skill() -> None:
    assert check_skill_menu_covers_every_skill().startswith("PASS")


def test_async_approval_fields_taught() -> None:
    assert check_async_approval_fields_taught().startswith("PASS")


def test_no_deprecated_approval_tier() -> None:
    assert check_no_deprecated_approval_tier().startswith("PASS")


def test_role_boundaries_no_obsolete_approval() -> None:
    assert check_role_boundaries_no_obsolete_approval().startswith("PASS")


def test_role_boundaries_has_r29_r30() -> None:
    assert check_role_boundaries_has_r29_r30().startswith("PASS")


def test_role_boundaries_header_localized() -> None:
    assert check_role_boundaries_header_localized().startswith("PASS")


def test_team_registry_created_by() -> None:
    assert check_team_registry_created_by().startswith("PASS")


def test_no_direct_ai_maestro_api_calls() -> None:
    assert check_no_direct_ai_maestro_api_calls().startswith("PASS")


def test_governance_stamp_matches_live_spec() -> None:
    # The only network-dependent check here, so it is the only one that can skip.
    outcome = check_governance_stamp_matches_live_spec()
    if outcome.startswith("SKIP:"):
        try:
            import pytest  # pyright: ignore[reportMissingImports]

            pytest.skip(outcome[5:].strip())
        except ImportError:
            return
    assert outcome.startswith("PASS"), outcome


def test_all_agents_global_memory() -> None:
    assert check_all_agents_global_memory().startswith("PASS")


def test_governance_stamp_detector_actually_fires() -> None:
    assert check_governance_stamp_detector_actually_fires().startswith(("PASS", "SKIP"))


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
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
