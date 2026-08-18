#!/usr/bin/env python3
"""amia_design_validate.py must accept the v2 TRDD corpus and reject malformed cards (TRDD-62UP8NJS).

The validator shipped on the v1 schema (type/status/GUUID) against a fully-v2 corpus,
rejecting 13/13 cards — and it was not wired into this runner, so the 100% failure was
invisible. This file is both halves of the fix's proof: the schema is v2, AND the
validator now runs on every suite pass. A checker nobody runs and a checker nobody
trusts are the same checker.

  uv run --with pytest pytest tests/test_design_validator_v2.py -q
  uv run python tests/test_design_validator_v2.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)
from amia_design_validate import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    find_design_docs,
    validate_document,
)

GOOD_CARD = """---
trdd-id: TESTCARD
title: A well-formed v2 card
column: todo
created: 2026-08-18T23:45:00+0200
updated: 2026-08-18T23:45:00+0200
current-owner: integrator
task-type: bugfix
---

# body
"""


def _validate_text(text: str) -> dict:
    with tempfile.NamedTemporaryFile(
        "w", suffix=".md", prefix="TRDD-", delete=False, encoding="utf-8"
    ) as f:
        f.write(text)
        p = Path(f.name)
    try:
        return validate_document(p)
    finally:
        p.unlink()


def check_real_corpus_validates_clean() -> str:
    """Every TRDD card in design/ validates clean under the v2 schema."""
    docs = find_design_docs(PLUGIN_ROOT / "design")
    if not docs:
        return "FAIL: found 0 cards — the discovery glob is broken (convenient zero)"
    bad = [r for r in (validate_document(d) for d in docs) if not r["valid"]]
    if bad:
        return f"FAIL: {len(bad)}/{len(docs)} cards rejected: {bad[:2]}"
    return "PASS"


def check_discovery_skips_non_cards() -> str:
    """PRRD.md and folder READMEs under design/ are not judged as cards."""
    docs = find_design_docs(PLUGIN_ROOT / "design")
    non_cards = [d for d in docs if not d.name.startswith("TRDD-")]
    if non_cards:
        return f"FAIL: non-card files swept in: {non_cards}"
    return "PASS"


def check_bogus_column_fails() -> str:
    """A card with `column: banana` FAILS, and passes once corrected (non-vacuity)."""
    bad = _validate_text(GOOD_CARD.replace("column: todo", "column: banana"))
    if bad["valid"] or not any("Invalid column" in i for i in bad["issues"]):
        return f"FAIL: bogus column accepted: {bad}"
    good = _validate_text(GOOD_CARD)
    if not good["valid"]:
        return f"FAIL: well-formed card rejected: {good}"
    return "PASS"


def check_missing_task_type_fails() -> str:
    """A card missing task-type still fails — the check is not merely disabled."""
    r = _validate_text(GOOD_CARD.replace("task-type: bugfix\n", ""))
    if r["valid"] or not any("task-type" in i for i in r["issues"]):
        return f"FAIL: missing task-type accepted: {r}"
    return "PASS"


def check_malformed_trdd_id_fails() -> str:
    """A lowercase/short trdd-id fails the 8-char uppercase base36 rule."""
    r = _validate_text(GOOD_CARD.replace("trdd-id: TESTCARD", "trdd-id: abc123"))
    if r["valid"] or not any("trdd-id" in i for i in r["issues"]):
        return f"FAIL: malformed id accepted: {r}"
    return "PASS"


CHECKS = [
    "check_real_corpus_validates_clean",
    "check_discovery_skips_non_cards",
    "check_bogus_column_fails",
    "check_missing_task_type_fails",
    "check_malformed_trdd_id_fails",
]


def test_real_corpus_validates_clean() -> None:
    assert check_real_corpus_validates_clean().startswith("PASS")


def test_discovery_skips_non_cards() -> None:
    assert check_discovery_skips_non_cards().startswith("PASS")


def test_bogus_column_fails() -> None:
    assert check_bogus_column_fails().startswith("PASS")


def test_missing_task_type_fails() -> None:
    assert check_missing_task_type_fails().startswith("PASS")


def test_malformed_trdd_id_fails() -> None:
    assert check_malformed_trdd_id_fails().startswith("PASS")


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
