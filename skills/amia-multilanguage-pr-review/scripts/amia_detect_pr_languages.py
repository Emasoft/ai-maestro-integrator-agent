#!/usr/bin/env python3
"""Detect programming languages in a PR's changed files.

This script analyzes changed files in a GitHub PR or local diff
and returns a breakdown of languages present.

Usage:
    python amia_detect_pr_languages.py --repo owner/repo --pr 123
    python amia_detect_pr_languages.py --diff-file changes.diff
    python amia_detect_pr_languages.py --files file1.py file2.ts file3.rs
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any, TypedDict


class LanguageInfo(TypedDict):
    """Type for language statistics."""

    files: int
    paths: list[str]
    lines_changed: int


EXTENSION_MAP = {
    ".py": "python",
    ".pyi": "python",
    ".pyx": "python",
    ".js": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".java": "java",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".scala": "scala",
    ".html": "html",
    ".htm": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".mdx": "markdown",
    ".sql": "sql",
    ".dockerfile": "dockerfile",
}

SPECIAL_FILENAMES = {
    "Makefile": "makefile",
    "GNUmakefile": "makefile",
    "Dockerfile": "dockerfile",
    "Jenkinsfile": "groovy",
    "Vagrantfile": "ruby",
    "Gemfile": "ruby",
    "Rakefile": "ruby",
    "CMakeLists.txt": "cmake",
}


def detect_language(filepath: str) -> str:
    """Detect language from file path."""
    path = Path(filepath)
    filename = path.name
    if filename in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[filename]
    ext = path.suffix.lower()
    return EXTENSION_MAP.get(ext, "other")


def get_pr_files(repo: str, pr_number: int) -> list[dict[str, Any]]:
    """Get changed files from a GitHub PR using gh CLI."""
    cmd = ["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", "files"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    data: dict[str, Any] = json.loads(result.stdout)
    files: list[dict[str, Any]] = data.get("files", [])
    return files


def parse_diff_file(diff_path: str) -> list[str]:
    """Parse a diff file to extract changed file paths."""
    files = []
    with open(diff_path, "r") as f:
        for line in f:
            if line.startswith("diff --git"):
                parts = line.split()
                if len(parts) >= 4:
                    filepath = parts[3].lstrip("b/")
                    files.append(filepath)
    return files


def analyze_files(files: list[str | dict[str, Any]]) -> dict[str, Any]:
    """Analyze files and return language breakdown."""
    languages: dict[str, LanguageInfo] = {}

    for item in files:
        if isinstance(item, dict):
            filepath = str(item.get("path", ""))
            additions = int(item.get("additions", 0))
            deletions = int(item.get("deletions", 0))
            lines_changed = additions + deletions
        else:
            filepath = item
            lines_changed = 0

        if not filepath:
            continue

        lang = detect_language(filepath)
        if lang not in languages:
            languages[lang] = {"files": 0, "paths": [], "lines_changed": 0}
        languages[lang]["files"] += 1
        languages[lang]["paths"].append(filepath)
        languages[lang]["lines_changed"] += lines_changed

    if not languages:
        return {"languages": {}, "primary_language": None, "total_files": 0}

    primary = max(languages.keys(), key=lambda k: languages[k]["files"])
    total_files = sum(d["files"] for d in languages.values())

    return {
        "languages": languages,
        "primary_language": primary,
        "total_files": total_files,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Detect languages in PR changed files")
    parser.add_argument("--repo", help="GitHub repository (owner/repo)")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--diff-file", help="Path to diff file")
    parser.add_argument("--files", nargs="+", help="List of file paths")
    parser.add_argument("--output", choices=["json", "text"], default="json")

    args = parser.parse_args()

    files: list[str | dict[str, Any]] = []
    if args.repo and args.pr:
        files.extend(get_pr_files(args.repo, args.pr))
    elif args.diff_file:
        files.extend(parse_diff_file(args.diff_file))
    elif args.files:
        files.extend(args.files)
    else:
        parser.error("Provide --repo and --pr, --diff-file, or --files")

    result = analyze_files(files)

    if args.output == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Primary language: {result['primary_language']}")
        print(f"Total files: {result['total_files']}")
        print("\nBreakdown:")
        for lang, data in sorted(
            result["languages"].items(), key=lambda x: -x[1]["files"]
        ):
            print(f"  {lang}: {data['files']} files")


if __name__ == "__main__":
    main()
