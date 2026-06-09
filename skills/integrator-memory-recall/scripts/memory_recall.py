#!/usr/bin/env python3
"""Symptom-based recall over a markdown memory dir.

Cross-platform implementation of the memory-recall protocol
(rules/memory-protocol.md): uses `memgrep recall` when the binary is on
PATH and degrades to a pure-Python case-insensitive regex search over the
notes' frontmatter + bodies otherwise. Recall degrades, never breaks.

Exit codes:
  0 - search ran (zero or more matches printed)
  2 - usage / environment error (missing memdir, bad regex)
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


def memgrep_recall(symptom: str, memdir: Path) -> int:
    """Run `memgrep recall` and stream its ranked output verbatim."""
    # memgrep ranks on description + title + tags and appends each note's
    # [^N] lessons — strictly better than the fallback, so prefer it.
    result = subprocess.run(
        ["memgrep", "recall", symptom, str(memdir)],
        capture_output=True,
        text=True,
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        # Surface memgrep's own diagnostics, then fail fast — a broken
        # memgrep install must be visible, not silently swallowed.
        sys.stderr.write(result.stderr)
        return result.returncode
    return 0


def fallback_recall(symptom: str, memdir: Path) -> int:
    """Pure-Python fallback: list notes whose text matches the symptom.

    Mirrors `grep -rliE "$SYMPTOM" "$MEMDIR"`: case-insensitive regex over
    each note's full text (frontmatter + body), one matching path per line.
    No ranking — the fallback degrades gracefully, it does not imitate
    memgrep's scoring.
    """
    try:
        pattern = re.compile(symptom, re.IGNORECASE)
    except re.error as exc:
        print(f"ERROR: symptom is not a valid regex: {exc}", file=sys.stderr)
        return 2

    print("(memgrep not found — pure-Python fallback, unranked)", file=sys.stderr)
    for note in sorted(memdir.rglob("*.md")):
        try:
            text = note.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if pattern.search(text):
            print(note)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symptom", required=True, help="The SYMPTOM query — the user's words / the error text, NOT the answer's jargon")
    parser.add_argument("--memdir", required=True, type=Path, help="The markdown memory directory to search")
    parser.add_argument(
        "--force-fallback",
        action="store_true",
        help="Skip memgrep even if installed (used by the test suite to exercise the degraded path deterministically)",
    )
    args = parser.parse_args()

    if not args.memdir.is_dir():
        print(f"ERROR: memory dir not found: {args.memdir}", file=sys.stderr)
        return 2

    if not args.force_fallback and shutil.which("memgrep"):
        return memgrep_recall(args.symptom, args.memdir)
    return fallback_recall(args.symptom, args.memdir)


if __name__ == "__main__":
    sys.exit(main())
