#!/usr/bin/env python3
"""The TDD issue-closure gate must pass RED->GREEN histories and block GREEN->RED (TRDD-ONCGHA1Q).

`verify_tdd_sequence()` shipped for months with an inverted comparison: it blocked
correct TDD sequences and admitted incorrect ones, and no test covered it — the two-line
table below is exactly what would have caught it on the day it was written. Both
directions MUST be asserted: a test covering only one direction passes against the
inverted code too.

`gh pr view` returns commits NEWEST-FIRST, so a correct history (RED committed first,
GREEN after) arrives as ['GREEN: ...', 'RED: ...'].

  uv run --with pytest pytest tests/test_tdd_gate_sequence.py -q
  uv run python tests/test_tdd_gate_sequence.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)
from amia_pre_issue_close_hook import (
    verify_tdd_sequence,  # noqa: E402  # pyright: ignore[reportMissingImports]
)


def check_correct_red_then_green_is_valid() -> str:
    """A correct TDD history (RED committed first, GREEN after; newest-first input) is VALID."""
    is_valid, msg, red, green = verify_tdd_sequence(
        ["GREEN: implement feature", "RED: add failing test"]
    )
    if not is_valid:
        return f"FAIL: correct RED->GREEN was blocked: {msg!r}"
    if (red, green) != (1, 1):
        return f"FAIL: wrong counts red={red} green={green}"
    return "PASS"


def check_wrong_green_then_red_is_invalid() -> str:
    """A wrong history (GREEN committed first, RED after; newest-first input) is INVALID."""
    is_valid, msg, _red, _green = verify_tdd_sequence(
        ["RED: add failing test", "GREEN: implement feature"]
    )
    if is_valid:
        return "FAIL: GREEN-before-RED history passed the gate"
    if "GREEN" not in msg:
        return f"FAIL: error message does not name the violation: {msg!r}"
    return "PASS"


def check_missing_red_is_invalid() -> str:
    """A history with no RED commit is INVALID (tests must fail first)."""
    is_valid, msg, _r, _g = verify_tdd_sequence(["GREEN: implement feature"])
    if is_valid:
        return "FAIL: no-RED history passed"
    if "RED" not in msg:
        return f"FAIL: unexpected message {msg!r}"
    return "PASS"


def check_missing_green_is_invalid() -> str:
    """A history with no GREEN commit is INVALID (implementation must exist)."""
    is_valid, msg, _r, _g = verify_tdd_sequence(["RED: add failing test"])
    if is_valid:
        return "FAIL: no-GREEN history passed"
    if "GREEN" not in msg:
        return f"FAIL: unexpected message {msg!r}"
    return "PASS"


def check_interleaved_history_judged_on_first_pair() -> str:
    """A multi-commit history is judged on the FIRST RED vs FIRST GREEN chronologically."""
    # chronological: RED, GREEN, RED, GREEN -> newest-first input below. Valid.
    ok_valid, _m1, r1, g1 = verify_tdd_sequence(
        ["GREEN: impl 2", "RED: test 2", "GREEN: impl 1", "RED: test 1"]
    )
    # chronological: GREEN, RED, GREEN -> first GREEN precedes first RED. Invalid.
    ok_invalid, _m2, _r2, _g2 = verify_tdd_sequence(
        ["GREEN: impl 2", "RED: test 1", "GREEN: impl 1"]
    )
    if not ok_valid:
        return f"FAIL: interleaved correct history blocked (red={r1} green={g1})"
    if ok_invalid:
        return "FAIL: history whose first GREEN precedes its first RED passed"
    return "PASS"


CHECKS = [
    "check_correct_red_then_green_is_valid",
    "check_wrong_green_then_red_is_invalid",
    "check_missing_red_is_invalid",
    "check_missing_green_is_invalid",
    "check_interleaved_history_judged_on_first_pair",
]


def test_correct_red_then_green_is_valid() -> None:
    assert check_correct_red_then_green_is_valid().startswith("PASS")


def test_wrong_green_then_red_is_invalid() -> None:
    assert check_wrong_green_then_red_is_invalid().startswith("PASS")


def test_missing_red_is_invalid() -> None:
    assert check_missing_red_is_invalid().startswith("PASS")


def test_missing_green_is_invalid() -> None:
    assert check_missing_green_is_invalid().startswith("PASS")


def test_interleaved_history_judged_on_first_pair() -> None:
    assert check_interleaved_history_judged_on_first_pair().startswith("PASS")


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
