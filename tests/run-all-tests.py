#!/usr/bin/env python3
"""Aggregate test runner — discovers and runs every tests/test_*.py.

Each `test_*.py` is a self-contained standalone runner: it prints its own
Unicode result table and exits 0 on all-pass / non-zero on any failure. This
runner discovers them, runs each as a subprocess in standalone mode, surfaces
each table, and aggregates into one overall verdict. Exit 0 iff every test
file passed — suitable as a publish-gate.

  uv run python tests/run-all-tests.py

The publish pipeline separately runs `pytest tests/` (the pytest wrappers in
each file). This runner is the pytest-independent path for humans and CI that
prefer the table output and want a single aggregate exit code.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent


def main() -> int:
    test_files = sorted(p for p in TESTS_DIR.glob("test_*.py"))
    if not test_files:
        print("no tests/test_*.py found", file=sys.stderr)
        return 1

    results: list[tuple[str, bool]] = []
    for tf in test_files:
        proc = subprocess.run([sys.executable, str(tf)], capture_output=True, text=True)
        sys.stdout.write(proc.stdout)
        if proc.stderr.strip():
            sys.stderr.write(proc.stderr)
        results.append((tf.name, proc.returncode == 0))

    name_w = max(len(n) for n, _ in results) + 1
    print(f"\n┏{'━' * name_w}┳{'━' * 8}┓")
    print(f"┃{'Test file'.ljust(name_w)}┃{' Result '.ljust(8)}┃")
    print(f"┡{'━' * name_w}╇{'━' * 8}┩")
    for name, ok in results:
        print(f"│{name.ljust(name_w)}│ {('PASS' if ok else 'FAIL').ljust(7)}│")
    print(f"└{'─' * name_w}┴{'─' * 8}┘")
    failed = [n for n, ok in results if not ok]
    print(f"{len(results) - len(failed)}/{len(results)} test files passed.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
