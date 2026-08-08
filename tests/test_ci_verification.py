#!/usr/bin/env python3
"""Real tests for the post-release CI verification stage (CPV v5.1.1's gap).

No mocks for the network: these poll the real GitHub check-runs API for real
commits in this repo. Substituting that read would test a different function than
the one that ships, and the stage exists precisely because a *green publish* is
not evidence of a *green build*.

## The hole being closed

`baseline-pr-and-checks` grants an admin bypass so `publish.py` can push straight
to the default branch — so the required status checks **never gate the release
push**. Without this stage the pipeline prints "Published successfully" purely
because `git push` and `gh release create` returned 0, having verified nothing
about whether the released commit builds. A red CI on a published tag would sit
unnoticed until somebody happened to look.

## Fail-closed is the property under test

An unreadable check-run list must never yield a green verdict. This was a real bug
caught while writing this: the first implementation returned `0` ("check manually")
when the API could not be read, which reports success on no evidence — the exact
inversion the branch-rules guard was written to avoid two commits earlier.

Two INDEPENDENT mechanisms enforce that, which the falsification made visible: the
`runs is None` branch keeps polling and exits 1 at the deadline, AND the green branch
requires `gating` to be non-empty, so even a bare `[]` cannot report green. Injecting
`[] on failure` — the dangerous shape — therefore leaves these checks passing. That is
defence in depth, not a decorative test: injecting a read that WRONGLY reports success
(the only shape that reaches a false green) does make `check_unreadable_fails_closed`
fail. `check_unreadable_read_returns_none` pins the `None`-vs-`[]` contract at the
function level so a future refactor cannot quietly remove one of the two mechanisms.

Runs two ways:

  uv run --with pytest pytest tests/test_ci_verification.py -q
  uv run python tests/test_ci_verification.py

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

import publish  # noqa: E402  # pyright: ignore[reportMissingImports]

# The v1.3.9 release commit: pushed, CI completed, known green.
GREEN_SHA = "8c16c2882bba8774d508a0b397a16954ed915688"
UNKNOWN_SHA = "0" * 40


def _gh_usable() -> bool:
    if not shutil.which("gh"):
        return False
    r = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
    return r.returncode == 0


SKIP_REASON = "gh CLI missing or unauthenticated — cannot read the LIVE check-runs API"


def _run_stage(sha: str, *, timeout: int = 6, poll: int = 2) -> tuple[int, str]:
    """Run the real stage against `sha`, with the deadline shortened for tests."""
    old_t, old_p = publish.CI_VERIFY_TIMEOUT_SEC, publish.CI_VERIFY_POLL_SEC
    old_git = publish._git_stdout
    publish.CI_VERIFY_TIMEOUT_SEC, publish.CI_VERIFY_POLL_SEC = timeout, poll
    # Only HEAD resolution is redirected — the check-runs read stays live, which
    # is the part whose behaviour is under test.
    publish._git_stdout = lambda root, cmd: sha if "rev-parse" in cmd else old_git(root, cmd)
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            rc = publish.stage_verify_ci(PLUGIN_ROOT, "0.0.0", dry_run=False)
    finally:
        publish.CI_VERIFY_TIMEOUT_SEC, publish.CI_VERIFY_POLL_SEC = old_t, old_p
        publish._git_stdout = old_git
    return rc, buf.getvalue()


# ── The checks ──


def check_push_only_jobs_are_not_gates() -> str:
    """Push-only jobs are excluded — they never run on a PR and must not be awaited."""
    if not {"notify", "release"} <= publish.CI_VERIFY_IGNORE:
        return f"FAIL: ignore-set is {publish.CI_VERIFY_IGNORE!r}"
    return "PASS"


def check_green_commit_verifies() -> str:
    """A real released commit with green CI verifies successfully."""
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    rc, out = _run_stage(GREEN_SHA)
    if rc != 0:
        return f"FAIL: green commit returned {rc}: {out.strip()[:180]}"
    if "CI green" not in out:
        return f"FAIL: no green confirmation: {out.strip()[:180]}"
    return "PASS"


def check_unreadable_fails_closed() -> str:
    """An unreadable check-run list exits NON-ZERO — never a green verdict on no evidence."""
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    rc, out = _run_stage(UNKNOWN_SHA)
    if rc == 0:
        return f"FAIL: unreadable list reported success: {out.strip()[:180]}"
    if "NOT verified" not in out:
        return f"FAIL: exited non-zero but did not say it was unverified: {out.strip()[:180]}"
    return "PASS"


def check_unreadable_read_returns_none() -> str:
    """An unreadable check-run list yields None — never [] read as 'nothing failed'."""
    # Pins the contract at the function level, independently of the stage's own
    # second guard (`gating` must be non-empty). Both must survive a refactor.
    if not _gh_usable():
        return f"SKIP: {SKIP_REASON}"
    got = publish._ci_check_runs("Emasoft/this-repo-does-not-exist-amia-ci-test", UNKNOWN_SHA)
    if got is None:
        return "PASS"
    return f"FAIL: unreadable list returned {got!r} instead of None"


def check_dry_run_does_not_poll() -> str:
    """Dry-run reports intent and returns 0 without touching the network."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = publish.stage_verify_ci(PLUGIN_ROOT, "0.0.0", dry_run=True)
    if rc != 0:
        return f"FAIL: dry-run returned {rc}"
    if "Would wait" not in buf.getvalue():
        return f"FAIL: dry-run said nothing: {buf.getvalue().strip()[:120]}"
    return "PASS"


CHECKS = [
    "check_push_only_jobs_are_not_gates",
    "check_dry_run_does_not_poll",
    "check_green_commit_verifies",
    "check_unreadable_fails_closed",
    "check_unreadable_read_returns_none",
]


# ── pytest wrappers ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_ci_verification(check_name: str) -> None:
        outcome = globals()[check_name]()
        if outcome.startswith("SKIP:"):
            pytest.skip(outcome[5:].strip())
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner ──


def main() -> int:
    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in CHECKS:
        fn = globals()[name]
        try:
            outcome = fn()
        except Exception as exc:
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
