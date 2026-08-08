#!/usr/bin/env python3
"""Real tests for the `--install-branch-rules` §F guard (claude-plugins-validation#203).

No mocks, deliberately. The guard's entire value is that it reads the **live**
ruleset list before allowing a destructive command to run; substituting that read
would test a different function than the one that ships. So these call the real
`gh api` against the real repo.

## What is being guarded

`cpv-setup-branch-rules` does NOT bring the ratified baseline to spec. Verified in
its source at v5.3.0: `RULESET_NAME = "cpv-branch-rules"` is hardcoded (`:110`),
the file contains zero occurrences of `baseline-`, its "legacy" classifier
(`:326`) matches any ruleset containing `pull_request`/`required_status_checks` —
which `baseline-pr-and-checks` always does — and `:694` then prints a
`gh api --method DELETE` for each match.

So on a baselined repo it ADDS a non-ratified ruleset (§F NON-EXEMPT) and advises
DELETING the ratified one. This guard refuses that.

## Ordering matters here

`check_repo_really_is_baselined` establishes the PREMISE and must pass before the
refusal checks mean anything. A guard that refuses for the wrong reason — an
unreadable list, a typo'd slug, a missing `gh` — is indistinguishable from a guard
working correctly, and would otherwise sail through as a false green.

Runs two ways:

  uv run --with pytest pytest tests/test_branch_rules_guard.py -q
  uv run python tests/test_branch_rules_guard.py

Standalone exit: 0 all pass (or honestly skipped), 1 any failure.
"""

from __future__ import annotations

import io
import shutil
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

from publish import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    RATIFIED_BASELINE_RULESETS,
    _ratified_baseline_present,
    install_branch_rules,
)

SLUG = "Emasoft/ai-maestro-integrator-agent"


def _gh_usable() -> bool:
    """Is `gh` present AND authenticated? A skip is honest; a mock would not be."""
    if not shutil.which("gh"):
        return False
    r = subprocess.run(
        ["gh", "auth", "status"], capture_output=True, text=True, check=False
    )
    return r.returncode == 0


SKIP_REASON = "gh CLI missing or unauthenticated — cannot read the LIVE ruleset list"


# ── The checks (shared by pytest wrappers and the standalone runner) ──


def check_ratified_names_are_the_spec_pair() -> str:
    """The guard watches exactly the two ruleset names §F ratifies."""
    if set(RATIFIED_BASELINE_RULESETS) != {
        "baseline-history-protect",
        "baseline-pr-and-checks",
    }:
        return f"FAIL: guard watches {RATIFIED_BASELINE_RULESETS!r}"
    return "PASS"


def check_repo_really_is_baselined() -> str:
    """PREMISE: this repo genuinely carries the ratified baseline right now."""
    # Everything below is meaningless if this is false — a guard that refuses
    # because it cannot see anything looks identical to one that works.
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    got = _ratified_baseline_present(SLUG)
    if got is None:
        return "FAIL: could not read the live ruleset list (guard would fail closed)"
    if got is not True:
        return "FAIL: repo does NOT carry the ratified baseline — premise broken"
    return "PASS"


def check_guard_refuses_on_baselined_repo() -> str:
    """install_branch_rules REFUSES (exit 1) rather than running the destructive command."""
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = install_branch_rules(PLUGIN_ROOT)
    out = buf.getvalue()
    if rc == 0:
        return "FAIL: guard allowed the run on a baselined repo"
    if "REFUSED" not in out:
        return f"FAIL: refused but said nothing actionable: {out.strip()[:200]}"
    if "cpv-branch-rules" not in out:
        return "FAIL: refusal does not name the ruleset that would be added"
    return "PASS"


def check_unreadable_list_fails_closed() -> str:
    """An unreadable ruleset list yields None — never an empty set read as 'no baseline'."""
    # A bare [] on failure is the dangerous shape: it reads as "nothing here",
    # the caller steps aside, and the destructive command runs against exactly
    # the repo nobody could inspect.
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    got = _ratified_baseline_present("Emasoft/this-repo-does-not-exist-amia-guard-test")
    if got is None:
        return "PASS"
    return f"FAIL: unreadable list returned {got!r} instead of None"


CHECKS = [
    "check_ratified_names_are_the_spec_pair",
    "check_repo_really_is_baselined",
    "check_guard_refuses_on_baselined_repo",
    "check_unreadable_list_fails_closed",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_branch_rules_guard(check_name: str) -> None:
        outcome = globals()[check_name]()
        if outcome.startswith("SKIP:"):
            pytest.skip(outcome[5:].strip())
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in CHECKS:
        fn = globals()[name]
        try:
            outcome = fn()
        except Exception as exc:  # a crashing check is a failing check
            outcome = f"ERROR: {exc}"
        doc = (fn.__doc__ or "").strip().splitlines()[0]
        if outcome.startswith("PASS"):
            status = "PASS"
        elif outcome.startswith("SKIP"):
            status = "SKIP"
        elif outcome.startswith("ERROR"):
            status = "ERROR"
        else:
            status = "FAIL"
        if status in ("FAIL", "ERROR"):
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
    print(f"{len(results) - failures}/{len(results)} passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
