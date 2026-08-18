#!/usr/bin/env python3
"""No `except Exception: pass` (bare or tuple-disguised) may exist in scripts/ (TRDD-J097QZ54).

House style is FAIL-FAST. A broad handler whose body is exactly `pass` silences every
failure including logic errors; the disguised form `except (X, Exception): pass` reads
targeted while Exception subsumes the tuple — a scan for the literal `except Exception`
slides past it, so this check walks the AST instead of grepping.

Narrow targeted catches (`OSError`, `ValueError`, ...) are fail-fast-compatible and pass.

  uv run --with pytest pytest tests/test_fail_fast_no_broad_swallows.py -q
  uv run python tests/test_fail_fast_no_broad_swallows.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)


def broad_swallows(source: str) -> list[tuple[int, str]]:
    """Return (lineno, handler-type) for every pass-only except that catches Exception."""
    hits: list[tuple[int, str]] = []
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, ast.ExceptHandler)
            and len(node.body) == 1
            and isinstance(node.body[0], ast.Pass)
        ):
            type_src = ast.unparse(node.type) if node.type else "BARE"
            names = (
                [type_src]
                if not type_src.startswith("(")
                else [t.strip() for t in type_src.strip("()").split(",")]
            )
            if type_src == "BARE" or any(
                n in ("Exception", "BaseException") for n in names
            ):
                hits.append((node.lineno, type_src))
    return hits


def check_no_broad_swallows_in_scripts() -> str:
    """scripts/*.py contains zero pass-only handlers that catch Exception/BaseException/bare."""
    offenders: list[str] = []
    for f in sorted((PLUGIN_ROOT / "scripts").glob("*.py")):
        for lineno, t in broad_swallows(f.read_text(encoding="utf-8")):
            offenders.append(f"{f.name}:{lineno} except {t}: pass")
    if offenders:
        return f"FAIL: broad swallows: {offenders}"
    return "PASS"


def check_non_vacuity_detects_injected_swallow() -> str:
    """The AST sweep flags a bare, a broad, AND a tuple-disguised swallow, and clears narrow ones."""
    bad = (
        "try:\n    x()\nexcept Exception:\n    pass\n"
        "try:\n    y()\nexcept (ValueError, Exception):\n    pass\n"
        "try:\n    w()\nexcept:\n    pass\n"
    )
    got = broad_swallows(bad)
    if len(got) != 3:
        return f"FAIL: expected 3 detections, got {got}"
    ok = "try:\n    z()\nexcept (OSError, ValueError):\n    pass\n"
    if broad_swallows(ok):
        return "FAIL: narrow targeted catch was flagged"
    return "PASS"


CHECKS = [
    "check_no_broad_swallows_in_scripts",
    "check_non_vacuity_detects_injected_swallow",
]


def test_no_broad_swallows_in_scripts() -> None:
    assert check_no_broad_swallows_in_scripts().startswith("PASS")


def test_non_vacuity_detects_injected_swallow() -> None:
    assert check_non_vacuity_detects_injected_swallow().startswith("PASS")


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
