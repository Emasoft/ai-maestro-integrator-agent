#!/usr/bin/env python3
"""Real tests for the branch-protection PreToolUse hook (issue #13, M12).

Exercises scripts/amia_pre_push_hook.py against REAL temporary git repos — no
mocks. The hook decides from the actual current branch (via `git`), so each
test builds a throwaway repo, checks out the branch under test, and runs the
hook with that repo as cwd, feeding the PreToolUse stdin JSON contract:

    {"tool_input": {"command": "git push origin main"}, "session_id": "..."}

Contract under test: exit 2 = block (push while on main/master), exit 0 = allow
(non-push command, push from a feature branch, or no command / fail-open).

Runs two ways:

  uv run --with pytest pytest tests/test_hooks.py -q
  uv run python tests/test_hooks.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
HOOK = PLUGIN_ROOT / "scripts" / "amia_pre_push_hook.py"

PUSH_MAIN = json.dumps({"tool_input": {"command": "git push origin main"}, "session_id": "test-session-0001"})


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _make_repo(tmp: Path, branch: str) -> Path:
    """Create a real git repo checked out on `branch` with one commit."""
    repo = tmp / f"repo-{branch.replace('/', '-')}"
    repo.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "test@example.com"], repo)
    _git(["config", "user.name", "Test"], repo)
    _git(["checkout", "-q", "-b", branch], repo)
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    _git(["add", "f.txt"], repo)
    _git(["commit", "-q", "-m", "init"], repo)
    return repo


def _run_hook(stdin: str | None, cwd: Path) -> int:
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=stdin if stdin is not None else "",
        capture_output=True,
        text=True,
        cwd=str(cwd),
    )
    return proc.returncode


# ── The checks (shared by pytest wrappers and the standalone runner) ──


def check_allows_non_push(tmp: Path) -> str:
    """A non-push command (e.g. `ls`) passes through with exit 0."""
    repo = _make_repo(tmp, "main")
    rc = _run_hook(json.dumps({"tool_input": {"command": "ls -la"}}), repo)
    if rc != 0:
        return f"FAIL: expected allow (0) for a non-push command, got {rc}"
    return "PASS"


def check_blocks_push_on_main(tmp: Path) -> str:
    """A `git push` while the current branch is main is blocked with exit 2."""
    repo = _make_repo(tmp, "main")
    rc = _run_hook(PUSH_MAIN, repo)
    if rc != 2:
        return f"FAIL: expected block (2) pushing from main, got {rc}"
    return "PASS"


def check_allows_push_on_feature(tmp: Path) -> str:
    """A `git push` from a feature branch is allowed with exit 0."""
    repo = _make_repo(tmp, "feature/test-branch")
    rc = _run_hook(PUSH_MAIN, repo)
    if rc != 0:
        return f"FAIL: expected allow (0) pushing from a feature branch, got {rc}"
    return "PASS"


def check_fail_open_on_empty(tmp: Path) -> str:
    """Empty stdin (non-hook invocation) fails open with exit 0."""
    repo = _make_repo(tmp, "main")
    rc = _run_hook("", repo)
    if rc != 0:
        return f"FAIL: expected fail-open allow (0) on empty stdin, got {rc}"
    return "PASS"


CHECKS = [
    "check_allows_non_push",
    "check_blocks_push_on_main",
    "check_allows_push_on_feature",
    "check_fail_open_on_empty",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.fixture(scope="session")
    def hookenv(tmp_path_factory: "pytest.TempPathFactory") -> Path:
        return tmp_path_factory.mktemp("amia-hooktest")

    def test_allows_non_push(hookenv: Path) -> None:
        assert check_allows_non_push(hookenv / "a").startswith("PASS")

    def test_blocks_push_on_main(hookenv: Path) -> None:
        assert check_blocks_push_on_main(hookenv / "b").startswith("PASS")

    def test_allows_push_on_feature(hookenv: Path) -> None:
        assert check_allows_push_on_feature(hookenv / "c").startswith("PASS")

    def test_fail_open_on_empty(hookenv: Path) -> None:
        assert check_fail_open_on_empty(hookenv / "d").startswith("PASS")

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="amia-hooktest-"))

    # Each check gets its own subdir so repos never collide.
    runners = {
        "check_allows_non_push": lambda: check_allows_non_push(_sub(tmp, "a")),
        "check_blocks_push_on_main": lambda: check_blocks_push_on_main(_sub(tmp, "b")),
        "check_allows_push_on_feature": lambda: check_allows_push_on_feature(_sub(tmp, "c")),
        "check_fail_open_on_empty": lambda: check_fail_open_on_empty(_sub(tmp, "d")),
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


def _sub(tmp: Path, name: str) -> Path:
    d = tmp / name
    d.mkdir(exist_ok=True)
    return d


if __name__ == "__main__":
    sys.exit(main())
