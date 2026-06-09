#!/usr/bin/env python3
"""Validate a markdown memory note against the memory-protocol schema.

Checks (rules/memory-protocol.md "The note format"):
  1. YAML frontmatter present and parseable.
  2. `name` present, kebab/snake slug, and == the filename stem.
  3. `description` present and non-empty (the load-bearing recall surface).
  4. `metadata.node_type` == "memory".
  5. `metadata.type` in {user, feedback, project, reference}.
  6. Non-empty body after the frontmatter.
  7. The sibling MEMORY.md index contains a line linking this note
     (warn-only when MEMORY.md is absent: recall works without the index).

Fail-fast: any schema violation exits 1 with one ERROR line per finding.

Usage:
    python3 validate_memory_note.py <note.md> [<note.md> ...]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

VALID_TYPES = {"user", "feedback", "project", "reference"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:[-_][a-z0-9]+)*$")


def validate_note(path: Path) -> list[str]:
    """Return a list of ERROR strings for one note (empty = valid)."""
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path}: unreadable: {exc}"]

    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    if not match:
        return [f"{path}: no YAML frontmatter block (--- ... ---)"]
    front_raw, body = match.group(1), match.group(2)

    try:
        front = yaml.safe_load(front_raw)
    except yaml.YAMLError as exc:
        return [f"{path}: frontmatter is not valid YAML: {exc}"]
    if not isinstance(front, dict):
        return [f"{path}: frontmatter is not a mapping"]

    name = front.get("name")
    if not isinstance(name, str) or not name:
        errors.append(f"{path}: missing 'name'")
    else:
        if not SLUG_RE.match(name):
            errors.append(f"{path}: 'name' is not a kebab/snake slug: {name!r}")
        if name != path.stem:
            errors.append(f"{path}: 'name' ({name!r}) != filename stem ({path.stem!r})")

    description = front.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{path}: missing/empty 'description' (the recall surface)")

    metadata = front.get("metadata")
    if not isinstance(metadata, dict):
        errors.append(f"{path}: missing 'metadata' mapping")
    else:
        if metadata.get("node_type") != "memory":
            errors.append(f"{path}: metadata.node_type must be 'memory', got {metadata.get('node_type')!r}")
        note_type = metadata.get("type")
        if note_type not in VALID_TYPES:
            errors.append(f"{path}: metadata.type must be one of {sorted(VALID_TYPES)}, got {note_type!r}")

    if not body.strip():
        errors.append(f"{path}: empty body — a note must carry its one fact")

    index = path.parent / "MEMORY.md"
    if index.exists():
        if f"({path.name})" not in index.read_text(encoding="utf-8"):
            errors.append(f"{path}: MEMORY.md has no index line linking ({path.name})")
    else:
        # The index is the human-loaded surface, not a recall dependency —
        # its absence is survivable, so warn instead of failing.
        print(f"WARNING: {index} not found — add the index line when it exists", file=sys.stderr)

    return errors


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    all_errors: list[str] = []
    for arg in sys.argv[1:]:
        all_errors.extend(validate_note(Path(arg)))

    for err in all_errors:
        print(f"ERROR: {err}", file=sys.stderr)
    if all_errors:
        return 1
    print(f"OK: {len(sys.argv) - 1} note(s) schema-valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
