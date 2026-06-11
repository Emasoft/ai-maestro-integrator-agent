#!/usr/bin/env python3
"""Real tests for the release-pipeline MANAGER-approval gate (issue #13, M5).

Exercises shared/release_governance.py and the two release scripts against real
fixture TRDDs in a tmp directory — no mocks. The CLI checks invoke the scripts
as subprocesses against a fake repo and a nonexistent notes file, so they assert
the GOVERNANCE gate WITHOUT ever reaching the network: the gate blocks first, or
(when approval is supplied) the missing-notes-file check fails inside
create_release — both before any `gh` call.

Runs two ways (the publish pipeline uses pytest; the table runner is for humans):

  uv run --with pytest pytest tests/test_release_governance.py -q
  uv run python tests/test_release_governance.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
CREATE = PLUGIN_ROOT / "skills" / "amia-release-management" / "scripts" / "amia_create_release.py"
ROLLBACK = PLUGIN_ROOT / "skills" / "amia-release-management" / "scripts" / "amia_rollback.py"

sys.path.insert(0, str(PLUGIN_ROOT))
from shared.release_governance import verify_release_approval  # noqa: E402

NO_LOG_TRDD = """---
trdd-id: 00000000-0000-4000-8000-000000000001
title: A task with no approval log
column: dev
---
# TRDD

Body with no approval log section at all.
"""

REQUEST_ONLY_TRDD = """---
trdd-id: 00000000-0000-4000-8000-000000000002
title: A task awaiting approval
column: complete
---
# TRDD

## Approval log

- 2026-06-11T10:00:00+0200 — Requested `complete → publish`. Standing by for MANAGER.
"""

APPROVED_TRDD = """---
trdd-id: 00000000-0000-4000-8000-000000000003
title: A task approved for release
column: complete
---
# TRDD

## Approval log

- 2026-06-11T10:00:00+0200 — Requested `complete → publish` (target: marketplace).
  MANAGER reply: APPROVED at 10:03. Rationale: tests passed; EHTs terminal.

## Next section
Unrelated content after the log must not be scanned.
"""


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


def _write(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


# ── The checks (shared by pytest wrappers and the standalone runner) ──
# Named check_* (NOT test_*): they take positional args, so pytest would
# otherwise collect them and report "fixture not found".


def check_gate_blocks_without_log(tmp: Path) -> str:
    """A TRDD with no '## Approval log' section is not a release approval."""
    r = verify_release_approval(_write(tmp, "nolog.md", NO_LOG_TRDD))
    if r.approved:
        return f"FAIL: a TRDD without an approval log was accepted: {r.detail}"
    return "PASS"


def check_gate_rejects_request_only(tmp: Path) -> str:
    """A 'Requested ... publish' line WITHOUT a MANAGER APPROVED reply is rejected."""
    r = verify_release_approval(_write(tmp, "reqonly.md", REQUEST_ONLY_TRDD))
    if r.approved:
        return "FAIL: an unapproved request was treated as an approval"
    return "PASS"


def check_gate_accepts_manager_approval(tmp: Path) -> str:
    """An '## Approval log' with APPROVED + a release keyword is accepted, with evidence."""
    r = verify_release_approval(_write(tmp, "approved.md", APPROVED_TRDD))
    if not r.approved:
        return f"FAIL: a valid MANAGER approval was rejected: {r.detail}"
    if "APPROVED" not in r.evidence_line:
        return f"FAIL: evidence line missing the APPROVED token: {r.evidence_line!r}"
    return "PASS"


def check_gate_missing_trdd() -> str:
    """A nonexistent approval-TRDD path is not an approval (fail-closed)."""
    r = verify_release_approval("/nonexistent/trdd-xyz.md")
    if r.approved:
        return "FAIL: a missing TRDD was treated as approved"
    return "PASS"


def check_cli_create_blocks_exit7(tmp: Path) -> str:
    """amia_create_release.py with NO approval args exits 7 before any gh call."""
    proc = run([sys.executable, str(CREATE), "--repo", "fake/repo", "--version", "9.9.9",
                "--notes", str(tmp / "absent.md")])
    if proc.returncode != 7:
        return f"FAIL: expected exit 7 (governance block), got {proc.returncode}"
    if "GOVERNANCE BLOCK" not in proc.stdout:
        return f"FAIL: missing GOVERNANCE BLOCK message: {proc.stdout[:120]!r}"
    return "PASS"


def check_cli_create_solo_passes_gate(tmp: Path) -> str:
    """--solo-user-approval passes the gate (then fails NOT_FOUND on missing notes, exit 2 not 7)."""
    proc = run([sys.executable, str(CREATE), "--repo", "fake/repo", "--version", "9.9.9",
                "--notes", str(tmp / "absent.md"), "--solo-user-approval", "owner approves"])
    if proc.returncode == 7:
        return "FAIL: solo approval did not pass the gate (still blocked)"
    if proc.returncode != 2:
        return f"FAIL: expected exit 2 (NOT_FOUND after gate), got {proc.returncode}: {proc.stdout[:120]!r}"
    return "PASS"


def check_cli_create_invalid_trdd_exit7(tmp: Path) -> str:
    """--approval-trdd pointing at an unapproved TRDD exits 7."""
    bad = _write(tmp, "reqonly2.md", REQUEST_ONLY_TRDD)
    proc = run([sys.executable, str(CREATE), "--repo", "fake/repo", "--version", "9.9.9",
                "--notes", str(tmp / "absent.md"), "--approval-trdd", str(bad)])
    if proc.returncode != 7:
        return f"FAIL: expected exit 7 for an unapproved TRDD, got {proc.returncode}"
    return "PASS"


def check_cli_rollback_execute_blocks_exit7() -> str:
    """amia_rollback.py --execute without approval exits 7; plan-only exits 0."""
    blocked = run([sys.executable, str(ROLLBACK), "--repo", "fake/repo", "--from", "v9.9.9",
                   "--to", "v9.9.8", "--reason", "test", "--execute"])
    if blocked.returncode != 7:
        return f"FAIL: --execute without approval should exit 7, got {blocked.returncode}"
    plan = run([sys.executable, str(ROLLBACK), "--repo", "fake/repo", "--from", "v9.9.9",
                "--to", "v9.9.8", "--reason", "test"])
    if plan.returncode != 0:
        return f"FAIL: plan-only rollback should exit 0, got {plan.returncode}"
    return "PASS"


CHECKS = [
    "check_gate_blocks_without_log",
    "check_gate_rejects_request_only",
    "check_gate_accepts_manager_approval",
    "check_gate_missing_trdd",
    "check_cli_create_blocks_exit7",
    "check_cli_create_solo_passes_gate",
    "check_cli_create_invalid_trdd_exit7",
    "check_cli_rollback_execute_blocks_exit7",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    # pytest is not a declared project dep — the publish pipeline supplies it
    # via `uv run --with pytest`; standalone runs land in the except branch.
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.fixture(scope="session")
    def gateenv(tmp_path_factory: "pytest.TempPathFactory") -> Path:
        return tmp_path_factory.mktemp("amia-gatetest")

    def test_gate_blocks_without_log(gateenv: Path) -> None:
        assert check_gate_blocks_without_log(gateenv).startswith("PASS")

    def test_gate_rejects_request_only(gateenv: Path) -> None:
        assert check_gate_rejects_request_only(gateenv).startswith("PASS")

    def test_gate_accepts_manager_approval(gateenv: Path) -> None:
        assert check_gate_accepts_manager_approval(gateenv).startswith("PASS")

    def test_gate_missing_trdd() -> None:
        assert check_gate_missing_trdd().startswith("PASS")

    def test_cli_create_blocks_exit7(gateenv: Path) -> None:
        assert check_cli_create_blocks_exit7(gateenv).startswith("PASS")

    def test_cli_create_solo_passes_gate(gateenv: Path) -> None:
        assert check_cli_create_solo_passes_gate(gateenv).startswith("PASS")

    def test_cli_create_invalid_trdd_exit7(gateenv: Path) -> None:
        assert check_cli_create_invalid_trdd_exit7(gateenv).startswith("PASS")

    def test_cli_rollback_execute_blocks_exit7() -> None:
        assert check_cli_rollback_execute_blocks_exit7().startswith("PASS")

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="amia-gatetest-"))

    runners = {
        "check_gate_blocks_without_log": lambda: check_gate_blocks_without_log(tmp),
        "check_gate_rejects_request_only": lambda: check_gate_rejects_request_only(tmp),
        "check_gate_accepts_manager_approval": lambda: check_gate_accepts_manager_approval(tmp),
        "check_gate_missing_trdd": check_gate_missing_trdd,
        "check_cli_create_blocks_exit7": lambda: check_cli_create_blocks_exit7(tmp),
        "check_cli_create_solo_passes_gate": lambda: check_cli_create_solo_passes_gate(tmp),
        "check_cli_create_invalid_trdd_exit7": lambda: check_cli_create_invalid_trdd_exit7(tmp),
        "check_cli_rollback_execute_blocks_exit7": check_cli_rollback_execute_blocks_exit7,
    }

    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in CHECKS:
        try:
            outcome = runners[name]()
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

    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
