#!/usr/bin/env python3
"""
amia_version_bump.py - Bump version in project files.

Finds version files (plugin.json, pyproject.toml, package.json, setup.py,
setup.cfg) in the current working directory, parses the current semver,
and increments based on the specified bump type.

Usage:
    amia_version_bump.py --repo owner/repo --type patch
    amia_version_bump.py --repo owner/repo --type minor --dry-run
    amia_version_bump.py --repo owner/repo --type major

Output:
    JSON object with bump results to stdout.

Example output:
    {
        "repo": "owner/repo",
        "bump_type": "patch",
        "old_version": "1.2.2",
        "new_version": "1.2.3",
        "files_updated": ["plugin.json", "pyproject.toml"],
        "dry_run": false
    }

Exit codes (standardized):
    0 - Success, version bumped
    1 - Invalid parameters (bad bump type, bad repo format)
    2 - No version files found
    3 - API error (file write failure)
    4 - Not authenticated (N/A for local operation)
    5 - Not applicable
    6 - Not applicable
"""

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any


SEMVER_PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)")

# Map of filename to regex patterns that capture the version string in context
VERSION_FILE_PATTERNS: dict[str, list[re.Pattern[str]]] = {
    "plugin.json": [re.compile(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")')],
    "package.json": [re.compile(r'("version"\s*:\s*")(\d+\.\d+\.\d+)(")')],
    "pyproject.toml": [re.compile(r'(version\s*=\s*")(\d+\.\d+\.\d+)(")')],
    "setup.py": [re.compile(r'(version\s*=\s*["\'])(\d+\.\d+\.\d+)(["\'])')],
    "setup.cfg": [re.compile(r'(version\s*=\s*)(\d+\.\d+\.\d+)(\s*)')],
}


def bump_semver(version_str: str, bump_type: str) -> str:
    """Increment a semver string by the specified bump type."""
    match = SEMVER_PATTERN.match(version_str)
    if not match:
        return version_str
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def find_and_bump_files(bump_type: str, dry_run: bool) -> dict[str, Any]:
    """Find version files and bump the version in each."""
    old_version = None
    new_version = None
    files_updated: list[str] = []

    for filename, patterns in VERSION_FILE_PATTERNS.items():
        matches = glob.glob(f"**/{filename}", recursive=True)
        for filepath in matches:
            path = Path(filepath)
            content = path.read_text(encoding="utf-8")
            for pattern in patterns:
                match = pattern.search(content)
                if match:
                    current = match.group(2)
                    if old_version is None:
                        old_version = current
                        new_version = bump_semver(current, bump_type)
                    bumped = bump_semver(current, bump_type)
                    new_content = pattern.sub(rf"\g<1>{bumped}\g<3>", content)
                    if not dry_run:
                        path.write_text(new_content, encoding="utf-8")
                    files_updated.append(filepath)
                    break

    if not files_updated:
        return {"error": True, "message": "No version files found", "code": "NOT_FOUND"}

    return {
        "bump_type": bump_type,
        "old_version": old_version,
        "new_version": new_version,
        "files_updated": files_updated,
        "dry_run": dry_run,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Bump version in project files.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format (for metadata)")
    parser.add_argument("--type", required=True, choices=["patch", "minor", "major"], help="Bump type")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without writing")

    args = parser.parse_args()

    if "/" not in args.repo:
        print(json.dumps({"error": True, "message": "Repository must be in owner/repo format"}))
        sys.exit(1)

    result = find_and_bump_files(bump_type=args.type, dry_run=args.dry_run)
    result["repo"] = args.repo
    print(json.dumps(result, indent=2))

    if result.get("error"):
        code = result.get("code", "")
        if code == "NOT_FOUND":
            sys.exit(2)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
