#!/usr/bin/env python3
"""The one standalone-runner table shared by every tests/test_*.py.

## Why this module exists

Each test file grew its own copy of the same ~25-line classify-and-render block.
Eight copies later, MegaLinter's jscpd crossed its 5% duplication threshold
(5.03%) and failed CI on the v1.4.0 release commit — caught by publish.py's new
post-release CI check, which is the only reason it did not sit red unnoticed.

The duplication was real, not a false positive: the flagged line ranges pointed
straight at each file's `main()`. So the fix is extraction, not raising the
threshold. Suppressing the detector would have kept the copies AND removed the
thing that noticed them.

`_`-prefixed so pytest does not collect it as a test module.

## The status vocabulary is deliberate

PASS / SKIP / FAIL / ERROR, where **SKIP is neither pass nor failure**. A check
that cannot run (no `gh`, no network) must say so rather than reporting green —
several suites here poll live APIs, and a skip silently counted as a pass is the
same fail-open inversion those suites exist to prevent.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence


def classify(outcome: str) -> str:
    """PASS / SKIP / ERROR / FAIL from a check's return string."""
    for prefix in ("PASS", "SKIP", "ERROR"):
        if outcome.startswith(prefix):
            return prefix
    return "FAIL"


def run_table(
    checks: Sequence[str],
    call: Callable[[str], str],
    doc_of: Callable[[str], str | None],
) -> int:
    """Run `checks` in order, print the result table, return 0 all-good else 1.

    `call` maps a check name to its outcome string; `doc_of` maps it to its
    docstring. Both are callables rather than dicts so a suite whose checks need
    per-check fixtures (a temp repo, say) can bind them without restructuring.
    """
    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in checks:
        try:
            outcome = call(name)
        except Exception as exc:  # a crashing check is a failing check
            outcome = f"ERROR: {exc}"
        status = classify(outcome)
        if status in ("FAIL", "ERROR"):
            failures += 1
        doc = (doc_of(name) or "").strip().splitlines()
        first = doc[0] if doc else name
        results.append((name, status, first if status == "PASS" else f"{first} — {outcome}"))

    name_w = max(len(r[0]) for r in results) + 1
    desc_w = max(len(r[2]) for r in results) + 1
    print(f"┏{'━' * name_w}┳{'━' * 8}┳{'━' * desc_w}┓")
    print(f"┃{'Test'.ljust(name_w)}┃{' Status '.ljust(8)}┃{'Description'.ljust(desc_w)}┃")
    print(f"┡{'━' * name_w}╇{'━' * 8}╇{'━' * desc_w}┩")
    for name, status, desc in results:
        print(f"│{name.ljust(name_w)}│ {status.ljust(7)}│{desc.ljust(desc_w)}│")
    print(f"└{'─' * name_w}┴{'─' * 8}┴{'─' * desc_w}┘")
    print(f"{len(results) - failures}/{len(results)} passed.")
    return 1 if failures else 0
