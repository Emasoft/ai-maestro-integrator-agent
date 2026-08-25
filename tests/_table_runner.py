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

import importlib.util
from collections.abc import Callable, Sequence
from pathlib import Path
from types import ModuleType

SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"


def load_claude_plugin_install() -> ModuleType:
    """Import `claude-plugin-install.py` (a dashed filename — no plain `import` works).

    `main()` in that file is guarded by `if __name__ == "__main__":`, so a real
    `spec.loader.exec_module()` import runs only module-level code (imports, constant
    tables, function/class definitions) — no CLI side effects. Verified by reading the
    file's tail before relying on this loader; if that guard is ever removed this import
    would start executing the CLI, so prefer the real import over re-parsing the source
    with regex — it exercises the actual code, not a text approximation of it.

    Lives here, not in a test file, because it is needed by more than one suite and the
    CI duplication gate (MegaLinter jscpd) is python-only: a second copy of these ~18
    lines is exactly the kind of paste that pushed this repo over the 5% threshold once
    already (see this module's header). Each call returns a FRESH module object — the
    spec is never registered in `sys.modules` — so one suite monkeypatching the module's
    path constants cannot leak into another.
    """
    path = SCRIPTS_DIR / "claude-plugin-install.py"
    spec = importlib.util.spec_from_file_location("claude_plugin_install", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not build an import spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
