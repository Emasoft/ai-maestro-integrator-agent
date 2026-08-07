#!/usr/bin/env python3
"""Real tests pinning skill-frontmatter invariants (no mocks — reads the shipped SKILL.md files).

The invariant that matters here is a **runtime-behaviour** one, and it is invisible
in review:

Claude Code 2.1.218 made skills declaring `context: fork` run in the BACKGROUND by
default. A backgrounded skill returns an agent name to its caller immediately and
delivers its real result later, as a notification. Every forked skill in this plugin
is a `user-invocable: false` knowledge-or-data skill that a specialist agent loads
*in order to act on it* — PR context before reviewing, quality gates before merging,
a taxonomy before labelling. If that result arrives asynchronously it lands after the
caller has already acted, which is silently wrong rather than loudly broken.

So each forked skill declares `background: false` EXPLICITLY. The declaration is the
point: it survives a future change to the platform default, whereas relying on the
default does not.

These tests exist so that a future default flip, or a new forked skill added without
the field, FAILS — naming the file — instead of quietly changing how the plugin runs.

Runs two ways:

  uv run --with pytest pytest tests/test_skill_frontmatter.py -q
  uv run python tests/test_skill_frontmatter.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PLUGIN_ROOT / "skills"


def _frontmatter(path: Path) -> dict[str, str]:
    """Top-level frontmatter keys of a SKILL.md.

    Deliberately dependency-free and indentation-aware: only column-0 `key: value`
    lines inside the leading `---` block count, so nested `metadata:` children are
    not mistaken for top-level fields.
    """
    out: dict[str, str] = {}
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return out
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if not line or line[0] in " \t#":
            continue
        key, sep, value = line.partition(":")
        if sep and key and not key[0].isspace():
            out[key.strip()] = value.strip()
    return out


def _skills() -> list[tuple[Path, dict[str, str]]]:
    found = [(p, _frontmatter(p)) for p in sorted(SKILLS_DIR.glob("*/SKILL.md"))]
    if not found:
        raise AssertionError(f"no SKILL.md found under {SKILLS_DIR} — wrong layout or bad path")
    return found


def _forked() -> list[tuple[Path, dict[str, str]]]:
    return [(p, fm) for p, fm in _skills() if fm.get("context") == "fork"]


# ── The checks (shared by pytest wrappers and the standalone runner) ──


def check_skills_are_discoverable() -> str:
    """The skills directory is found and every SKILL.md has parseable frontmatter."""
    skills = _skills()
    missing = [str(p.relative_to(PLUGIN_ROOT)) for p, fm in skills if not fm.get("name")]
    if missing:
        return f"FAIL: SKILL.md files with no parseable 'name': {', '.join(missing[:5])}"
    return "PASS"


def check_forked_skills_exist() -> str:
    """At least one skill declares context fork, so the checks below are not vacuous."""
    # Without this, deleting every forked skill would make the whole file pass green
    # while asserting nothing at all.
    if not _forked():
        return "FAIL: no skill declares 'context: fork' — the background checks assert nothing"
    return "PASS"


def check_every_forked_skill_declares_background() -> str:
    """Every skill with context fork declares background explicitly, never by default."""
    offenders = [
        str(p.relative_to(PLUGIN_ROOT)) for p, fm in _forked() if "background" not in fm
    ]
    if offenders:
        return (
            "FAIL: forked skill(s) with no explicit 'background:' — a platform default "
            f"change would silently alter their behaviour: {', '.join(offenders)}"
        )
    return "PASS"


def check_forked_skills_are_not_backgrounded() -> str:
    """Every forked skill sets background false so its result reaches the caller in-turn."""
    offenders = [
        f"{p.relative_to(PLUGIN_ROOT)} (background: {fm.get('background')})"
        for p, fm in _forked()
        if fm.get("background") != "false"
    ]
    if offenders:
        return (
            "FAIL: forked skill(s) not set to 'background: false' — their result would "
            f"arrive after the caller already acted: {', '.join(offenders)}"
        )
    return "PASS"


def check_background_value_is_a_bare_bool() -> str:
    """The background value is a bare false, not a quoted or capitalised near-miss."""
    # "false" / "False" / "no" are distinct tokens to a YAML parser; only bare false
    # is unambiguous, and a quoted "false" is a string, not a boolean.
    offenders = [
        f"{p.relative_to(PLUGIN_ROOT)} -> {fm['background']!r}"
        for p, fm in _skills()
        if "background" in fm and fm["background"] not in ("false", "true")
    ]
    if offenders:
        return f"FAIL: non-bare-boolean background value(s): {', '.join(offenders)}"
    return "PASS"


def check_background_only_on_forked_skills() -> str:
    """Only forked skills carry background — it is meaningless on a non-forked skill."""
    offenders = [
        str(p.relative_to(PLUGIN_ROOT))
        for p, fm in _skills()
        if "background" in fm and fm.get("context") != "fork"
    ]
    if offenders:
        return f"FAIL: 'background:' on skill(s) that are not 'context: fork': {', '.join(offenders)}"
    return "PASS"


CHECKS = [
    "check_skills_are_discoverable",
    "check_forked_skills_exist",
    "check_every_forked_skill_declares_background",
    "check_forked_skills_are_not_backgrounded",
    "check_background_value_is_a_bare_bool",
    "check_background_only_on_forked_skills",
]


# ── pytest wrappers (the publish pipeline runs `pytest tests/`) ──

try:
    import pytest  # pyright: ignore[reportMissingImports]

    @pytest.mark.parametrize("check_name", CHECKS)
    def test_skill_frontmatter(check_name: str) -> None:
        outcome = globals()[check_name]()
        assert outcome.startswith("PASS"), outcome

except ImportError:
    pass


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    results: list[tuple[str, str, str]] = []
    failures = 0
    for name in CHECKS:
        try:
            outcome = globals()[name]()
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
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
