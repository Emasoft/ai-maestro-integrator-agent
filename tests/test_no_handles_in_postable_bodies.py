#!/usr/bin/env python3
"""Placeholder `@handle`s inside postable `gh ... --body "..."` strings page real accounts (TRDD-T3CLWN5Y).

Ported from the ai-maestro hub's `tests/governance/no-handles-in-postable-bodies.test.ts`
(hub TRDD-BDRWMBDC point 7): an `@name` outside a code span pages a real GitHub account,
and a *template* is exactly the artifact copy-pasted verbatim under time pressure. Five of
six placeholder-looking names checked against `gh api users/<name>` resolved to real
accounts — "descriptive" names like `@human-dev` are not obviously placeholders.

Scope is deliberately narrow: only text inside a `gh ... --body "..."` argument is
POSTABLE (it is what actually reaches the GitHub API verbatim). Prose elsewhere in a doc
("Assigned to: @agent-1") is not scanned — sweeping all `@word` hits would also disable the
27 real `@claude` bot triggers (see the TRDD's classification table), which is the exact
mistake this check exists to prevent.

  uv run --with pytest pytest tests/test_no_handles_in_postable_bodies.py -q
  uv run python tests/test_no_handles_in_postable_bodies.py

Standalone exit: 0 all pass, 1 any failure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "tests"))

from _table_runner import (
    run_table,  # noqa: E402  # pyright: ignore[reportMissingImports]
)

# Real GitHub Apps/bots legitimately invoked BY NAME inside a posted comment body —
# these are not placeholders, they are the literal trigger the workflow depends on
# (e.g. `gh pr comment N --body "@claude Please review..."`). Unlike a user placeholder,
# there is no syntactic way to tell "this @word is a real bot trigger" apart from "this
# @word is a made-up example name" other than knowing the bot account exists.
KNOWN_BOT_TRIGGERS = {"claude", "copilot", "dependabot"}

# `--body "..."` / `--body '...'` — the only positions in a `gh` invocation whose text
# is actually POSTED verbatim to GitHub. Content is captured up to the FIRST matching
# closing quote (or end of line for an unterminated multi-line body), so a trailing
# `--assignee "@me"` on the same line never falls inside the captured body text —
# `@me` passes by POSITION (it is not inside a body argument), never by a name check.
BODY_ARG_DQ = re.compile(r'--body\s+"([^"]*)')
BODY_ARG_SQ = re.compile(r"--body\s+'([^']*)")
# Negative lookbehind excludes `pkg@version` specifiers (e.g. `biome@latest`) where the
# `@` is glued to a preceding word — a real handle is always preceded by whitespace/start.
HANDLE = re.compile(r"(?<![\w/])@([a-zA-Z][a-zA-Z0-9_-]*)")


def find_placeholder_handles(text: str) -> list[str]:
    """Return every `@handle` inside a `--body "..."` argument that is NOT a known bot trigger."""
    hits: list[str] = []
    for body_match in list(BODY_ARG_DQ.finditer(text)) + list(
        BODY_ARG_SQ.finditer(text)
    ):
        body_text = body_match.group(1)
        for handle_match in HANDLE.finditer(body_text):
            name = handle_match.group(1)
            end = handle_match.end()
            if body_text[end : end + 1] == "/":
                continue  # npm scope specifier, e.g. @biomejs/biome — not a handle
            if name.lower() in KNOWN_BOT_TRIGGERS:
                continue
            hits.append(f"@{name}")
    return hits


SCAN_DIRS = [PLUGIN_ROOT / "skills", PLUGIN_ROOT / "agents"]


def check_no_placeholder_handles_in_repo() -> str:
    """No placeholder @handle sits inside a postable `gh ... --body` string anywhere in skills/ or agents/."""
    offenders: list[str] = []
    for scan_dir in SCAN_DIRS:
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.rglob("*.md")):
            hits = find_placeholder_handles(md_file.read_text(encoding="utf-8"))
            if hits:
                rel = md_file.relative_to(PLUGIN_ROOT)
                offenders.append(f"{rel}: {hits}")
    if offenders:
        return f"FAIL: placeholder handles in postable bodies: {offenders}"
    return "PASS"


def check_known_bot_triggers_and_flag_values_survive() -> str:
    """@claude / @dependabot bodies and --assignee @me/@copilot are never flagged by this check."""
    sample = (
        'gh pr comment 1 --body "@claude Please review this PR."\n'
        'gh pr comment 2 --body "@dependabot rebase"\n'
        'gh issue comment 3 --body "Closes #42" --assignee "@me"\n'
        'gh pr create --body "install with @biomejs/biome@latest"\n'
    )
    hits = find_placeholder_handles(sample)
    if hits:
        return f"FAIL: false positive on real trigger/flag/scope tokens: {hits}"
    return "PASS"


def check_non_vacuity_fails_on_injected_placeholder() -> str:
    """The check genuinely fails when a placeholder handle is injected into a postable body, and clears once removed."""
    injected = 'gh issue comment 1 --body "@someone please take a look"'
    hits_with_injection = find_placeholder_handles(injected)
    if hits_with_injection != ["@someone"]:
        return (
            f"FAIL: injected placeholder was not detected — got {hits_with_injection}"
        )
    clean = 'gh issue comment 1 --body "please take a look"'
    hits_after_removal = find_placeholder_handles(clean)
    if hits_after_removal:
        return f"FAIL: clean body still flagged — got {hits_after_removal}"
    return "PASS"


CHECKS = [
    "check_no_placeholder_handles_in_repo",
    "check_known_bot_triggers_and_flag_values_survive",
    "check_non_vacuity_fails_on_injected_placeholder",
]


def test_no_placeholder_handles_in_repo() -> None:
    assert check_no_placeholder_handles_in_repo().startswith("PASS")


def test_known_bot_triggers_and_flag_values_survive() -> None:
    assert check_known_bot_triggers_and_flag_values_survive().startswith("PASS")


def test_non_vacuity_fails_on_injected_placeholder() -> None:
    assert check_non_vacuity_fails_on_injected_placeholder().startswith("PASS")


# ── Standalone runner with the human-readable result table ──


def main() -> int:
    return run_table(CHECKS, lambda n: globals()[n](), lambda n: globals()[n].__doc__)


if __name__ == "__main__":
    sys.exit(main())
