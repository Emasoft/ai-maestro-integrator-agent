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
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)


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


# Vacuity floor. Every per-skill check below iterates the forked set, so all of them
# degrade to ZERO assertions as that set shrinks — green while asserting nothing. This is
# the one failure a guard cannot report about itself, so it needs a second guard.
#
# A bare "at least one" is not enough: a bad merge, or a rename of the `context:` value,
# that stripped the field from 18 of 19 skills would leave a single passing skill and a
# silent suite — the exact silent-erosion class this file exists to catch.
#
# The floor sits deliberately BELOW the current count (19) rather than equal to it, so a
# legitimate removal or two does not require a test edit, while mass erosion still fails.
# Adopted from ai-maestro-chief-of-staff 9bb29e3, which hardened this idea after taking
# the rest of this file's shape from TRDD-GJF8C8SR.
FORKED_SKILL_FLOOR = 15


def check_forked_skill_count_above_floor() -> str:
    """The forked-skill count stays above its floor, so the per-skill checks stay meaningful."""
    n = len(_forked())
    if n < FORKED_SKILL_FLOOR:
        return (
            f"FAIL: only {n} skill(s) declare 'context: fork', below the floor of "
            f"{FORKED_SKILL_FLOOR} — the per-skill background checks have quietly stopped "
            "asserting. Either mass erosion happened, or the 'context:' value was renamed."
        )
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
    "check_forked_skill_count_above_floor",
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
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
