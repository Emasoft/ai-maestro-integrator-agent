#!/usr/bin/env python3
"""Real tests for the `{plugin-name}--v{version}` resolver tag (integrator#22).

Exercises scripts/publish.py against REAL temporary git repos — no mocks. The
dry-run check builds an actual repo with a real manifest and a real commit, then
calls the real `stage_commit_and_push` in dry-run mode and asserts on what it
says it would push.

## Why this tag is load-bearing

Claude Code resolves a VERSIONED plugin dependency (`{"name": "x", "version":
"^2.7.0"}`) only via a `{name}--v{version}` tag. A plain `v{version}` tag is not
enough: the resolver reports *"has no git tag satisfying >=…"* even though
`git ls-remote --tags` plainly lists the versions. That mismatch grounded the
whole plugin fleet for a day (ai-maestro TRDD-JT3U4ZVM, integrator#22).

The failure mode is silent and DOWNSTREAM — this repo publishes fine without the
tag; it is whoever *depends* on this repo that cannot install. Nothing in a local
publish would ever reveal it, which is exactly why it needs a test.

Two traps these tests pin down:

  1. The resolver tag must be pushed in the SAME `--atomic` transaction as the
     release tag. Pushed separately, a partial failure leaves a published release
     that no dependant can resolve.
  2. A nameless manifest must HARD-FAIL rather than degrade to some fallback tag
     name — a silently-wrong tag is the very bug being fixed.

Runs two ways:

  uv run --with pytest pytest tests/test_publish_resolver_tag.py -q
  uv run python tests/test_publish_resolver_tag.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)
from publish import (  # noqa: E402  # pyright: ignore[reportMissingImports]
    get_plugin_name,
    resolver_tag,
    stage_commit_and_push,
)


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True)


def _make_plugin_repo(tmp: Path, name: str | None, version: str = "9.9.9") -> Path:
    """A real git repo with a real .claude-plugin/plugin.json and one commit."""
    repo = tmp / "repo"
    (repo / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    manifest: dict[str, str] = {"version": version}
    if name is not None:
        manifest["name"] = name
    (repo / ".claude-plugin" / "plugin.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "test@example.com"], repo)
    _git(["config", "user.name", "Test"], repo)
    _git(["add", "."], repo)
    _git(["commit", "-q", "-m", "init"], repo)
    return repo


# ── The checks (shared by pytest wrappers and the standalone runner) ──


def check_reads_name_from_manifest() -> str:
    """The plugin name is read from this repo's own .claude-plugin/plugin.json."""
    name = get_plugin_name(PLUGIN_ROOT)
    if name != "ai-maestro-integrator-agent":
        return f"FAIL: expected 'ai-maestro-integrator-agent', got {name!r}"
    return "PASS"


def check_resolver_tag_shape() -> str:
    """The resolver tag is exactly {plugin-name}--v{version}."""
    got = resolver_tag(PLUGIN_ROOT, "1.2.3")
    if got != "ai-maestro-integrator-agent--v1.2.3":
        return f"FAIL: got {got!r}"
    return "PASS"


def check_resolver_tag_differs_from_release_tag() -> str:
    """The resolver tag is NOT the plain vX.Y.Z tag — that distinction is the whole point."""
    # A publish that emitted only `v1.2.3` is precisely the broken state: the
    # release exists and no dependant can resolve it.
    if resolver_tag(PLUGIN_ROOT, "1.2.3") == "v1.2.3":
        return "FAIL: resolver tag collapsed to the plain release tag"
    return "PASS"


def check_nameless_manifest_hard_fails(tmp: Path) -> str:
    """A manifest with no `name` hard-fails instead of degrading to a fallback tag."""
    repo = _make_plugin_repo(tmp, name=None)
    try:
        got = resolver_tag(repo, "1.0.0")
    except SystemExit:
        return "PASS"
    return f"FAIL: expected SystemExit, got tag {got!r}"


def check_missing_manifest_hard_fails(tmp: Path) -> str:
    """A missing manifest hard-fails rather than inventing a tag name."""
    empty = tmp / "empty"
    empty.mkdir(parents=True, exist_ok=True)
    try:
        got = resolver_tag(empty, "1.0.0")
    except SystemExit:
        return "PASS"
    return f"FAIL: expected SystemExit, got tag {got!r}"


def check_push_is_atomic_and_carries_both_tags(tmp: Path) -> str:
    """Dry-run reports BOTH tags created and pushed in one atomic transaction."""
    repo = _make_plugin_repo(tmp, name="demo-plugin")
    buf = io.StringIO()
    with redirect_stdout(buf):
        stage_commit_and_push(repo, "9.9.9", dry_run=True)
    out = buf.getvalue()

    if "Would tag: v9.9.9" not in out:
        return f"FAIL: release tag not announced. Got: {out.strip()[:200]}"
    if "Would tag: demo-plugin--v9.9.9" not in out:
        return f"FAIL: resolver tag not announced. Got: {out.strip()[:200]}"

    push_lines = [ln for ln in out.splitlines() if "Would push" in ln]
    if not push_lines:
        return f"FAIL: no push line. Got: {out.strip()[:200]}"
    push = push_lines[0]
    if "atomic" not in push:
        return f"FAIL: push is not atomic: {push!r}"
    if "v9.9.9" not in push or "demo-plugin--v9.9.9" not in push:
        return f"FAIL: push omits a tag — a release no dependant can resolve: {push!r}"
    return "PASS"


CHECKS = [
    "check_reads_name_from_manifest",
    "check_resolver_tag_shape",
    "check_resolver_tag_differs_from_release_tag",
    "check_nameless_manifest_hard_fails",
    "check_missing_manifest_hard_fails",
    "check_push_is_atomic_and_carries_both_tags",
]

_NEEDS_TMP = {
    "check_nameless_manifest_hard_fails",
    "check_missing_manifest_hard_fails",
    "check_push_is_atomic_and_carries_both_tags",
}


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_resolver_tag(check_name: str, tmp_path: Path) -> None:
        fn = globals()[check_name]
        outcome = fn(tmp_path) if check_name in _NEEDS_TMP else fn()
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="amia-rtagtest-"))

    def call(name: str) -> str:
        fn = globals()[name]
        if name in _NEEDS_TMP:
            sub = tmp / f"c{CHECKS.index(name)}"
            sub.mkdir(parents=True, exist_ok=True)
            return fn(sub)
        return fn()

    try:
        return run_table(CHECKS, call, lambda n: globals()[n].__doc__)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
