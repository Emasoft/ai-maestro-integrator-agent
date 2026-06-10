#!/usr/bin/env python3
"""Real tests for the integrator memory skills (issue #12).

Exercises the two bundled scripts against a real fixture memory dir in a
tmp directory — no mocks:

  - memory_recall.py with memgrep when installed (round-trip recall),
  - memory_recall.py --force-fallback (the degraded path, deterministic),
  - validate_memory_note.py on schema-valid and schema-broken notes.

Runs two ways (the publish pipeline uses pytest; the table runner is for
humans):

  uv run --with pytest pytest tests/test_memory_skills.py -q
  uv run python tests/test_memory_skills.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
RECALL = PLUGIN_ROOT / "skills" / "integrator-memory-recall" / "scripts" / "memory_recall.py"
VALIDATE = PLUGIN_ROOT / "skills" / "integrator-memory-write" / "scripts" / "validate_memory_note.py"

GOOD_NOTE = """---
name: project_ci-timeout-merge-step
description: "CI job times out on the integration test / pipeline hangs at the merge step"
metadata:
  node_type: memory
  type: project
---
The hang is an orphaned worktree lock under .git/worktrees/. Remove the stale
lock before retrying the merge step.

**Why:** the previous run was killed mid-merge and left the lock behind.
**How to apply:** check for stale locks before diagnosing CI timeouts.
"""

DECOY_NOTE = """---
name: reference_label-colors
description: "which colors do the review labels use"
metadata:
  node_type: memory
  type: reference
---
The review labels use the standard taxonomy palette.
"""

BAD_NOTE = """---
name: Wrong Name With Spaces
description: ""
metadata:
  node_type: page
  type: banana
---
"""


def build_fixture(memdir: Path) -> None:
    """Create a real two-note memory dir + index, validator-clean."""
    memdir.mkdir(parents=True)
    (memdir / "project_ci-timeout-merge-step.md").write_text(GOOD_NOTE, encoding="utf-8")
    (memdir / "reference_label-colors.md").write_text(DECOY_NOTE, encoding="utf-8")
    (memdir / "MEMORY.md").write_text(
        "# Memory index\n\n"
        "- [CI timeout at merge step](project_ci-timeout-merge-step.md) — orphaned worktree lock.\n"
        "- [Label colors](reference_label-colors.md) — taxonomy palette.\n",
        encoding="utf-8",
    )


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True)


# ── The checks (shared by pytest wrappers and the standalone runner) ──
# Named check_* (NOT test_*) on purpose: they take positional args, and
# pytest would otherwise collect them and report "fixture not found".


def check_recall_fallback(memdir: Path) -> str:
    """Fallback recall (no memgrep) finds the note from the SYMPTOM and skips the decoy."""
    proc = run([sys.executable, str(RECALL), "--symptom", "pipeline hangs at the merge step", "--memdir", str(memdir), "--force-fallback"])
    if proc.returncode != 0:
        return f"FAIL: exit {proc.returncode}: {proc.stderr.strip()}"
    if "project_ci-timeout-merge-step.md" not in proc.stdout:
        return f"FAIL: target note not found in output: {proc.stdout!r}"
    if "reference_label-colors.md" in proc.stdout:
        return "FAIL: decoy note matched — symptom search is not selective"
    return "PASS"


def check_recall_fallback_no_match(memdir: Path) -> str:
    """Fallback recall returns cleanly (exit 0, no paths) when nothing matches."""
    proc = run([sys.executable, str(RECALL), "--symptom", "kubernetes ingress flapping", "--memdir", str(memdir), "--force-fallback"])
    if proc.returncode != 0:
        return f"FAIL: exit {proc.returncode} on a no-match search"
    if ".md" in proc.stdout:
        return f"FAIL: expected no matches, got: {proc.stdout!r}"
    return "PASS"


def check_recall_missing_memdir() -> str:
    """Recall fails fast (exit 2) on a nonexistent memory dir."""
    proc = run([sys.executable, str(RECALL), "--symptom", "anything", "--memdir", "/nonexistent/memdir-xyz", "--force-fallback"])
    if proc.returncode != 2:
        return f"FAIL: expected exit 2, got {proc.returncode}"
    return "PASS"


def check_recall_memgrep(memdir: Path) -> str:
    """With memgrep installed, recall ranks the note from the SYMPTOM (round-trip); without it, the auto-fallback branch is verified."""
    if not shutil.which("memgrep"):
        # The script's contract without the binary IS the fallback — prove the
        # auto-detect branch picks it (no --force-fallback flag here).
        proc = run([sys.executable, str(RECALL), "--symptom", "pipeline hangs at the merge step", "--memdir", str(memdir)])
        if proc.returncode != 0 or "project_ci-timeout-merge-step.md" not in proc.stdout:
            return f"FAIL: auto-fallback branch broken: exit {proc.returncode}, out={proc.stdout!r}"
        return "PASS (memgrep absent — auto-fallback branch verified)"
    proc = run([sys.executable, str(RECALL), "--symptom", "pipeline hangs at the merge step", "--memdir", str(memdir)])
    if proc.returncode != 0:
        return f"FAIL: exit {proc.returncode}: {proc.stderr.strip()}"
    if "project_ci-timeout-merge-step" not in proc.stdout:
        return f"FAIL: memgrep recall did not surface the note: {proc.stdout!r}"
    return "PASS"


def check_validator_accepts_good(memdir: Path) -> str:
    """Validator passes a schema-valid note with an index line."""
    proc = run([sys.executable, str(VALIDATE), str(memdir / "project_ci-timeout-merge-step.md")])
    if proc.returncode != 0:
        return f"FAIL: exit {proc.returncode}: {proc.stderr.strip()}"
    return "PASS"


def check_validator_rejects_bad(tmp: Path) -> str:
    """Validator rejects a note with bad slug, empty description, wrong node_type/type, empty body."""
    bad = tmp / "badnote.md"
    bad.write_text(BAD_NOTE, encoding="utf-8")
    proc = run([sys.executable, str(VALIDATE), str(bad)])
    if proc.returncode != 1:
        return f"FAIL: expected exit 1, got {proc.returncode}"
    err = proc.stderr
    for needle in ("slug", "description", "node_type", "metadata.type", "empty body"):
        if needle not in err:
            return f"FAIL: missing finding {needle!r} in: {err!r}"
    return "PASS"


def check_validator_flags_missing_index_line(tmp: Path) -> str:
    """Validator fails when MEMORY.md exists but lacks the note's index line."""
    memdir2 = tmp / "mem2"
    memdir2.mkdir()
    (memdir2 / "project_orphan-note.md").write_text(
        GOOD_NOTE.replace("project_ci-timeout-merge-step", "project_orphan-note"), encoding="utf-8"
    )
    (memdir2 / "MEMORY.md").write_text("# Memory index\n", encoding="utf-8")
    proc = run([sys.executable, str(VALIDATE), str(memdir2 / "project_orphan-note.md")])
    if proc.returncode != 1 or "index line" not in proc.stderr:
        return f"FAIL: expected index-line finding, exit={proc.returncode}, err={proc.stderr!r}"
    return "PASS"


CHECKS = [
    "check_recall_fallback",
    "check_recall_fallback_no_match",
    "check_recall_missing_memdir",
    "check_recall_memgrep",
    "check_validator_accepts_good",
    "check_validator_rejects_bad",
    "check_validator_flags_missing_index_line",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    # pytest is not a declared project dep — the publish pipeline supplies it
    # via `uv run --with pytest`; standalone runs land in the except branch.
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.fixture(scope="session")
    def memenv(tmp_path_factory: "pytest.TempPathFactory") -> tuple[Path, Path]:
        tmp = tmp_path_factory.mktemp("amia-memtest")
        memdir = tmp / "memory"
        build_fixture(memdir)
        return tmp, memdir

    def test_recall_fallback(memenv: tuple[Path, Path]) -> None:
        result = check_recall_fallback(memenv[1])
        assert result.startswith("PASS"), result

    def test_recall_fallback_no_match(memenv: tuple[Path, Path]) -> None:
        result = check_recall_fallback_no_match(memenv[1])
        assert result.startswith("PASS"), result

    def test_recall_missing_memdir() -> None:
        result = check_recall_missing_memdir()
        assert result.startswith("PASS"), result

    def test_recall_memgrep(memenv: tuple[Path, Path]) -> None:
        result = check_recall_memgrep(memenv[1])
        assert result.startswith("PASS"), result

    def test_validator_accepts_good(memenv: tuple[Path, Path]) -> None:
        result = check_validator_accepts_good(memenv[1])
        assert result.startswith("PASS"), result

    def test_validator_rejects_bad(memenv: tuple[Path, Path]) -> None:
        result = check_validator_rejects_bad(memenv[0])
        assert result.startswith("PASS"), result

    def test_validator_flags_missing_index_line(memenv: tuple[Path, Path]) -> None:
        result = check_validator_flags_missing_index_line(memenv[0])
        assert result.startswith("PASS"), result

except ImportError:
    # Standalone mode (`python tests/test_memory_skills.py`) has no pytest —
    # main() below covers every check with its own fixture + result table.
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="amia-memtest-"))
    memdir = tmp / "memory"
    build_fixture(memdir)

    runners = {
        "check_recall_fallback": lambda: check_recall_fallback(memdir),
        "check_recall_fallback_no_match": lambda: check_recall_fallback_no_match(memdir),
        "check_recall_missing_memdir": check_recall_missing_memdir,
        "check_recall_memgrep": lambda: check_recall_memgrep(memdir),
        "check_validator_accepts_good": lambda: check_validator_accepts_good(memdir),
        "check_validator_rejects_bad": lambda: check_validator_rejects_bad(tmp),
        "check_validator_flags_missing_index_line": lambda: check_validator_flags_missing_index_line(tmp),
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
