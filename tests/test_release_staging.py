#!/usr/bin/env python3
"""Real tests that the release commit stages the right paths, by name.

## Why this exists

The release commit used to run `git add -A`, which also stages UNTRACKED files.
Stage 1 guarantees a clean tree, but stages 7-9 (bump, badge, changelog, uv lock)
run between that check and the commit — so anything appearing in that window (a
scratch note, a tool's temp output, an agent report) was swept into a PUBLIC,
irreversible release commit with nobody reviewing it. Filed upstream as
claude-plugins-validation#206; CORE confirmed the same defect in a third repo.

## The bug the fix introduced, which these tests pin

Replacing it with `git diff --name-only` looked correct and passed on every path
in this repo — because git only quotes NON-ASCII paths, and this repo has none.
Given `café-ünïcode.txt`, git emits `"caf\\303\\251-\\303\\274n\\303\\257code.txt"`
— quotes AND octal escapes — and feeding that back to `git add` dies with
`fatal: pathspec ... did not match any files` (exit 128, reproduced).

It fails CLOSED, so nothing wrong gets committed; but a plugin containing one
non-ASCII filename could never publish at all. Stripping the quotes is NOT the
fix — the octal escapes remain. `-z` is: NUL-separated, no quoting, no escaping.

Spaces are the near-miss worth knowing: `My Project/file.txt` round-trips fine
unquoted, so a test using only spaces would have passed and certified nothing.

Runs two ways:

  uv run --with pytest pytest tests/test_release_staging.py -q
  uv run python tests/test_release_staging.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

# E402 is covered by the tests/*.py per-file-ignore in pyproject.toml, so no
# inline noqa here — a long trailing comment is what makes ruff rewrap the import
# into parens, which strands any noqa INSIDE them where it no longer suppresses.
from _table_runner import run_table  # pyright: ignore[reportMissingImports]

PUBLISH_SRC = PLUGIN_ROOT / "scripts" / "publish.py"


def _repo_with_awkward_paths() -> Path:
    """A real repo holding a unicode path, a spaced path, and a rename."""
    tmp = Path(tempfile.mkdtemp(prefix="amia-stage-"))
    def g(*a: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *a], cwd=tmp, capture_output=True, text=True, check=False)
    g("init", "-q")
    g("config", "user.email", "713559+Emasoft@users.noreply.github.com")
    g("config", "user.name", "Emasoft")
    (tmp / "My Project").mkdir()
    (tmp / "My Project" / "file with space.txt").write_text("a\n", encoding="utf-8")
    (tmp / "café-ünïcode.txt").write_text("a\n", encoding="utf-8")
    (tmp / "plain.txt").write_text("a\n", encoding="utf-8")
    g("add", "-A")
    g("commit", "-q", "-m", "init")
    (tmp / "My Project" / "file with space.txt").write_text("b\n", encoding="utf-8")
    (tmp / "café-ünïcode.txt").write_text("b\n", encoding="utf-8")
    g("mv", "plain.txt", "renamed.txt")
    return tmp


def check_no_git_add_all_in_release_commit() -> str:
    """The release commit never runs `git add -A` (claude-plugins-validation#206)."""
    src = PUBLISH_SRC.read_text(encoding="utf-8")
    if '"git", "add", "-A"' in src:
        return "FAIL: publish.py still stages the release commit with git add -A"
    return "PASS"


def check_staging_uses_nul_separated_paths() -> str:
    """The changed-file read uses -z, so git cannot quote or octal-escape a path."""
    src = PUBLISH_SRC.read_text(encoding="utf-8")
    if '"git", "diff", "--name-only", "-z"' not in src:
        return "FAIL: the changed-file read is not -z (non-ASCII paths will be quoted)"
    return "PASS"


def check_unicode_path_round_trips_to_git_add() -> str:
    """A non-ASCII path parsed from -z output can be staged; the non-z form CANNOT."""
    tmp = _repo_with_awkward_paths()
    try:
        def diff(*extra: str) -> str:
            return subprocess.run(["git", "diff", "--name-only", *extra],
                                  cwd=tmp, capture_output=True, text=True, check=False).stdout

        # The form that ships.
        paths = [p for p in diff("-z").split("\0") if p]
        if not any("café" in p for p in paths):
            return f"FAIL: -z did not yield the unicode path verbatim: {paths}"
        r = subprocess.run(["git", "add", "--", *paths], cwd=tmp,
                           capture_output=True, text=True, check=False)
        if r.returncode != 0:
            return f"FAIL: -z paths rejected by git add: {(r.stderr or '').strip()[:140]}"

        # The form that was there before, which must be shown to FAIL — otherwise
        # this test would pass on any implementation and prove nothing.
        subprocess.run(["git", "reset", "-q"], cwd=tmp, check=False)
        naive = [p.strip() for p in diff().splitlines() if p.strip()]
        r2 = subprocess.run(["git", "add", "--", *naive], cwd=tmp,
                            capture_output=True, text=True, check=False)
        if r2.returncode == 0:
            return ("FAIL: the naive splitlines() form ALSO succeeded — the regression "
                    "this pins is not reproducible here, so the check proves nothing")
        return "PASS"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_untracked_file_is_not_staged() -> str:
    """An untracked file appearing mid-publish is NOT swept into the release commit."""
    tmp = _repo_with_awkward_paths()
    try:
        (tmp / "SCRATCH-do-not-ship.txt").write_text("secret-ish\n", encoding="utf-8")
        paths = [p for p in subprocess.run(
            ["git", "diff", "--name-only", "-z"], cwd=tmp,
            capture_output=True, text=True, check=False).stdout.split("\0") if p]
        if any("SCRATCH" in p for p in paths):
            return "FAIL: an untracked file appeared in the staged set"
        return "PASS"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


CHECKS = [
    "check_no_git_add_all_in_release_commit",
    "check_staging_uses_nul_separated_paths",
    "check_unicode_path_round_trips_to_git_add",
    "check_untracked_file_is_not_staged",
]


try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_release_staging(check_name: str) -> None:
        outcome = globals()[check_name]()
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
