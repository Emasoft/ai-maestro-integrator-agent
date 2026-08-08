#!/usr/bin/env python3
"""Real tests that CHANGELOG.md ACCUMULATES instead of being overwritten.

## The bug these pin down

`stage_changelog` ran `git-cliff --bump --unreleased --tag v<N> -o CHANGELOG.md`.
With `--unreleased`, `-o` writes ONLY the new section over the whole file — so
every release silently destroyed its predecessor's entry.

Measured on this repo at v1.4.0: after 10+ releases CHANGELOG.md was 23 lines
holding exactly ONE section, beneath a header promising "all notable changes to
this project will be documented in this file". Nothing failed and nothing warned;
the file just never grew. The history was recoverable (git-cliff over all tags
rebuilt 26 sections) only because the TAGS survived — the commits, not the file,
were the real record.

Reported by the CORE session, which hit the identical defect in the shared
scaffold. Its warning is the reason there is a source-level check below: the fix
lives in CPV's canonical emitter, so a pin bump does NOT deliver it to a drifted
publish.py. Verify the behaviour, not the version.

## The derived bug, which is why two things are tested together

Release notes passed the whole CHANGELOG via `--notes-file`. That was harmless
only WHILE the file held one section — the moment step 9 correctly accumulates,
the same code publishes the entire project history as one release's notes.
Fixing the truncation alone would have created a worse bug, so the extractor is
tested here beside it.

Runs two ways:

  uv run --with pytest pytest tests/test_changelog_accumulation.py -q
  uv run python tests/test_changelog_accumulation.py

Standalone exit: 0 all pass (or honestly skipped), 1 any failure.
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

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)
from publish import (
    _changelog_section,  # noqa: E402  # pyright: ignore[reportMissingImports]
)

PUBLISH_SRC = PLUGIN_ROOT / "scripts" / "publish.py"
CHANGELOG = PLUGIN_ROOT / "CHANGELOG.md"

SAMPLE = """# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] — 2026-08-08

### Features

- Second release thing

## [1.0.0] — 2026-01-01

### Bug Fixes

- First release thing
"""


def check_emitter_uses_prepend_not_output() -> str:
    """Step 9 uses --prepend; the truncating `-o CHANGELOG.md` form is gone."""
    # A source-level guard on purpose: this is the exact string that regressed,
    # and a drifted publish.py never receives the upstream emitter fix, so the
    # only thing that can catch a re-drift here is this repo's own test.
    src = PUBLISH_SRC.read_text(encoding="utf-8")
    if '"-o", "CHANGELOG.md"' in src and "--prepend" not in src:
        return "FAIL: step 9 still writes -o CHANGELOG.md (overwrites history)"
    if '"--prepend", "CHANGELOG.md"' not in src:
        return "FAIL: step 9 does not use --prepend CHANGELOG.md"
    return "PASS"


def check_section_extracted_without_leakage() -> str:
    """Release notes carry ONLY the target version's section."""
    tmp = Path(tempfile.mkdtemp(prefix="amia-cl-")) / "CHANGELOG.md"
    tmp.write_text(SAMPLE, encoding="utf-8")
    try:
        got = _changelog_section(tmp, "2.0.0")
        if got is None:
            return "FAIL: no section extracted for 2.0.0"
        if "1.0.0" in got or "First release thing" in got:
            return f"FAIL: leaked an older section into the notes: {got!r}"
        if "Second release thing" not in got:
            return f"FAIL: target section body missing: {got!r}"
        older = _changelog_section(tmp, "1.0.0")
        if older is None or "Second release thing" in older:
            return "FAIL: extracting the OLDEST section leaked a newer one"
        return "PASS"
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)


def check_missing_version_returns_none() -> str:
    """An absent version yields None so the caller falls back to --generate-notes."""
    # Must NOT return a best-effort slice: shipping the previous release's notes
    # under this release's tag is worse than terse auto-generated notes.
    tmp = Path(tempfile.mkdtemp(prefix="amia-cl-")) / "CHANGELOG.md"
    tmp.write_text(SAMPLE, encoding="utf-8")
    try:
        got = _changelog_section(tmp, "9.9.9")
        return "PASS" if got is None else f"FAIL: returned {got!r} for an absent version"
    finally:
        shutil.rmtree(tmp.parent, ignore_errors=True)


def check_prepend_preserves_history_for_real() -> str:
    """git-cliff --prepend on a REAL repo keeps the older section; -o would not."""
    if not shutil.which("git-cliff"):
        return "SKIP: git-cliff not installed — cannot exercise the real emitter"
    tmp = Path(tempfile.mkdtemp(prefix="amia-clrepo-"))
    try:
        run = lambda *a: subprocess.run(a, cwd=tmp, capture_output=True, text=True, check=False)  # noqa: E731
        run("git", "init", "-q")
        run("git", "config", "user.email", "713559+Emasoft@users.noreply.github.com")
        run("git", "config", "user.name", "Emasoft")
        shutil.copy(PLUGIN_ROOT / "cliff.toml", tmp / "cliff.toml")
        (tmp / "CHANGELOG.md").write_text(SAMPLE, encoding="utf-8")
        (tmp / "f.txt").write_text("x", encoding="utf-8")
        run("git", "add", "f.txt", "cliff.toml", "CHANGELOG.md")
        run("git", "commit", "-q", "-m", "feat: a brand new feature")

        r = subprocess.run(
            ["git-cliff", "--bump", "--unreleased", "--tag", "v3.0.0", "--prepend", "CHANGELOG.md"],
            cwd=tmp, capture_output=True, text=True, check=False,
        )
        if r.returncode != 0:
            return f"FAIL: git-cliff --prepend errored: {(r.stderr or '').strip()[:160]}"
        after = (tmp / "CHANGELOG.md").read_text(encoding="utf-8")
        for old in ("## [2.0.0]", "## [1.0.0]"):
            if old not in after:
                return f"FAIL: --prepend DESTROYED {old} — history not preserved"
        if "## [3.0.0]" not in after:
            return "FAIL: the new 3.0.0 section was not added"
        if after.index("## [3.0.0]") > after.index("## [2.0.0]"):
            return "FAIL: new section was appended below the old ones, not prepended"
        return "PASS"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check_shipped_changelog_has_history() -> str:
    """This repo's own CHANGELOG.md carries its full release history, not one section."""
    if not CHANGELOG.is_file():
        return "FAIL: CHANGELOG.md missing"
    n = sum(1 for line in CHANGELOG.read_text(encoding="utf-8").splitlines() if line.startswith("## ["))
    # It held exactly 1 when the bug was found; 26 were recovered from the tags.
    if n < 10:
        return f"FAIL: CHANGELOG.md has only {n} version section(s) — history was truncated again"
    return "PASS"


CHECKS = [
    "check_emitter_uses_prepend_not_output",
    "check_section_extracted_without_leakage",
    "check_missing_version_returns_none",
    "check_prepend_preserves_history_for_real",
    "check_shipped_changelog_has_history",
]


# ── pytest wrappers ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_changelog_accumulation(check_name: str) -> None:
        outcome = globals()[check_name]()
        if outcome.startswith("SKIP:"):
            pytest.skip(outcome[5:].strip())
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
