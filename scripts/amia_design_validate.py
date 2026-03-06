#!/usr/bin/env python3
"""
amia_design_validate.py - Validate design document frontmatter.

Scans design documents for valid YAML frontmatter, checking required fields,
valid status values, GUID format, and UTF-8 encoding. Follows the same
frontmatter parsing pattern as amia_design_search.py.

Usage:
    amia_design_validate.py --all
    amia_design_validate.py --path design/pdr/auth-system.md
    amia_design_validate.py --type pdr
    amia_design_validate.py --all --strict

Output:
    JSON object with validation results to stdout.

Example output:
    {
        "total_scanned": 5,
        "valid": 4,
        "invalid": 1,
        "results": [
            {
                "file": "design/pdr/auth-system.md",
                "valid": true,
                "issues": []
            },
            {
                "file": "design/spec/api-v2.md",
                "valid": false,
                "issues": ["Missing required field: status", "Invalid UUID format: BAD-ID"]
            }
        ]
    }

Exit codes (standardized):
    0 - Success, all documents valid
    1 - Invalid parameters
    2 - No design documents found
    3 - File read error
    4 - Not applicable
    5 - Validation failures found (with --strict)
    6 - Not applicable
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


VALID_STATUSES = {"DRAFT", "REVIEW", "APPROVED", "IMPLEMENTED", "ARCHIVED", "DEPRECATED", "REJECTED"}
UUID_PATTERN = re.compile(r"^GUUID-\d{8}-\d{4}$")
REQUIRED_FIELDS = {"type", "status"}


def parse_frontmatter(file_path: Path) -> tuple[dict[str, str] | None, str | None]:
    """Parse YAML frontmatter from a markdown file.

    Returns (frontmatter_dict, error_message).
    """
    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None, "File is not valid UTF-8"
    except OSError as e:
        return None, f"Could not read file: {e}"

    if not content.startswith("---"):
        return None, "No YAML frontmatter delimiter found"

    lines = content.split("\n")
    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        return None, "Unclosed YAML frontmatter (missing closing ---)"

    frontmatter: dict[str, str] = {}
    for line in lines[1:end_idx]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip().strip("'\"")
            frontmatter[key] = value

    return frontmatter, None


def validate_document(file_path: Path) -> dict[str, Any]:
    """Validate a single design document's frontmatter."""
    issues: list[str] = []
    relative = str(file_path)

    frontmatter, error = parse_frontmatter(file_path)
    if error:
        return {"file": relative, "valid": False, "issues": [error]}

    if frontmatter is None:
        return {"file": relative, "valid": False, "issues": ["No frontmatter parsed"]}

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in frontmatter:
            issues.append(f"Missing required field: {field}")

    # Validate status value
    status = frontmatter.get("status", "").upper()
    if "status" in frontmatter and status not in VALID_STATUSES:
        issues.append(f"Invalid status: '{frontmatter['status']}'. Valid: {', '.join(sorted(VALID_STATUSES))}")

    # Validate UUID format if present
    uuid_val = frontmatter.get("uuid", "")
    if uuid_val and not UUID_PATTERN.match(uuid_val):
        issues.append(f"Invalid UUID format: '{uuid_val}'. Expected: GUUID-YYYYMMDD-NNNN")

    return {"file": relative, "valid": len(issues) == 0, "issues": issues}


def find_design_docs(base_path: Path, doc_type: str | None = None) -> list[Path]:
    """Find design documents under the given path."""
    if doc_type:
        search_dir = base_path / doc_type
        if search_dir.is_dir():
            return sorted(search_dir.glob("**/*.md"))
        return []
    return sorted(base_path.glob("**/*.md"))


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate design document frontmatter.")
    parser.add_argument("--all", action="store_true", help="Scan all design documents under design/")
    parser.add_argument("--path", help="Validate a specific file")
    parser.add_argument("--type", help="Validate documents of a specific type (pdr, spec, etc.)")
    parser.add_argument("--design-root", default="design", help="Root directory for design docs (default: design)")
    parser.add_argument("--strict", action="store_true", help="Exit with code 5 if any validation fails")

    args = parser.parse_args()

    if not args.all and not args.path and not args.type:
        parser.error("Specify --all, --path, or --type")

    files: list[Path] = []
    if args.path:
        p = Path(args.path)
        if not p.is_file():
            print(json.dumps({"error": True, "message": f"File not found: {args.path}"}))
            sys.exit(2)
        files = [p]
    else:
        design_root = Path(args.design_root)
        if not design_root.is_dir():
            print(json.dumps({"error": True, "message": f"Design root not found: {args.design_root}"}))
            sys.exit(2)
        files = find_design_docs(design_root, doc_type=args.type)

    if not files:
        print(json.dumps({"error": True, "message": "No design documents found", "total_scanned": 0}))
        sys.exit(2)

    results = [validate_document(f) for f in files]
    valid_count = sum(1 for r in results if r["valid"])
    invalid_count = len(results) - valid_count

    output = {
        "total_scanned": len(results),
        "valid": valid_count,
        "invalid": invalid_count,
        "results": results,
    }
    print(json.dumps(output, indent=2))

    if invalid_count > 0 and args.strict:
        sys.exit(5)


if __name__ == "__main__":
    main()
