#!/usr/bin/env python3
"""
Detect platform-specific code patterns that may cause CI failures.

This script scans source code for patterns that work on one platform but
may fail on others (e.g., hardcoded paths, Windows-specific APIs).

Usage:
    python amia_detect_platform_issue.py --path /path/to/project
    python amia_detect_platform_issue.py --path . --extensions .py .js .sh
    python amia_detect_platform_issue.py --path . --json
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class Issue:
    """A detected platform-specific code issue."""

    file: str
    line: int
    pattern: str
    category: str
    description: str
    fix: str
    code: str


# Platform-specific code patterns to detect
DETECTION_PATTERNS = [
    # Hardcoded temp paths
    {
        "name": "hardcoded_tmp",
        "regex": r'["\']\/tmp(?:\/[^"\']*)?["\']',
        "category": "cross-platform",
        "description": "Hardcoded /tmp path fails on Windows",
        "fix": "Use tempfile.gettempdir() (Python) or os.tmpdir() (JS)",
        "extensions": [".py", ".js", ".ts", ".sh"],
    },
    {
        "name": "windows_temp",
        "regex": r"\$env:TEMP|\$env:TMP|%TEMP%|%TMP%",
        "category": "cross-platform",
        "description": "Windows-specific temp variable fails on Linux/macOS",
        "fix": "Use [System.IO.Path]::GetTempPath() or cross-platform API",
        "extensions": [".ps1", ".bat", ".cmd"],
    },
    # Path separators
    {
        "name": "backslash_path",
        "regex": r'["\'][A-Za-z]:\\\\[^"\']+["\']|["\']\\\\[^"\']+\\\\[^"\']+["\']',
        "category": "cross-platform",
        "description": "Backslash path fails on Linux/macOS",
        "fix": "Use path.join() or os.path.join() for cross-platform paths",
        "extensions": [".py", ".js", ".ts"],
    },
    # Shell-specific syntax
    {
        "name": "bash_array",
        "regex": r"\$\{[a-zA-Z_][a-zA-Z0-9_]*\[@\]\}|\(\s*[^)]+\s*\)",
        "category": "syntax",
        "description": "Bash array syntax not available in POSIX sh",
        "fix": "Use POSIX-compatible syntax or ensure bash shell",
        "extensions": [".sh"],
    },
    {
        "name": "ansi_c_quoting",
        "regex": r"\$'[^']*'",
        "category": "syntax",
        "description": "$'...' ANSI-C quoting not available in POSIX sh",
        "fix": "Use printf for escape sequences in POSIX sh",
        "extensions": [".sh"],
    },
    # Exit code handling
    {
        "name": "unchecked_exit",
        "regex": r"^\s*(?:git|npm|pip|cargo|go)\s+[^|&;]+$",
        "category": "exit-code",
        "description": "Command exit code not checked",
        "fix": "Add error checking: 'command || exit 1' or 'set -e'",
        "extensions": [".sh"],
    },
    # Platform-specific commands
    {
        "name": "linux_command",
        "regex": r"\b(?:apt-get|yum|dnf|systemctl|journalctl)\b",
        "category": "platform",
        "description": "Linux-specific command fails on macOS/Windows",
        "fix": "Add platform detection or use cross-platform alternatives",
        "extensions": [".sh", ".yml", ".yaml"],
    },
    {
        "name": "macos_command",
        "regex": r"\b(?:brew|launchctl|defaults|open)\b",
        "category": "platform",
        "description": "macOS-specific command fails on Linux/Windows",
        "fix": "Add platform detection or use cross-platform alternatives",
        "extensions": [".sh", ".yml", ".yaml"],
    },
    # Environment variables
    {
        "name": "home_env",
        "regex": r"\$HOME(?![A-Z_])|~/",
        "category": "cross-platform",
        "description": "$HOME may not be set on all platforms",
        "fix": "Use os.path.expanduser('~') or platform-specific handling",
        "extensions": [".sh", ".py"],
    },
    # Python-specific
    {
        "name": "python_posix",
        "regex": r"\bos\.system\s*\([^)]*(?:ls|cat|grep|awk|sed)",
        "category": "python",
        "description": "os.system with Unix commands fails on Windows",
        "fix": "Use subprocess with shell=False and cross-platform commands",
        "extensions": [".py"],
    },
    # JavaScript-specific
    {
        "name": "exec_unix",
        "regex": r"exec(?:Sync)?\s*\([^)]*(?:ls|cat|grep|chmod)",
        "category": "javascript",
        "description": "exec with Unix commands fails on Windows",
        "fix": "Use cross-platform Node.js APIs (fs, path, etc.)",
        "extensions": [".js", ".ts"],
    },
]


def scan_file(file_path: Path, patterns: list[dict[str, Any]]) -> list[Issue]:
    """Scan a single file for platform-specific patterns."""
    issues: list[Issue] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except (OSError, IOError):
        return issues
    lines = content.splitlines()
    suffix = file_path.suffix.lower()
    for pattern in patterns:
        if suffix not in pattern.get("extensions", []):
            continue
        regex = re.compile(pattern["regex"], re.IGNORECASE)
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                issues.append(
                    Issue(
                        file=str(file_path),
                        line=i,
                        pattern=pattern["name"],
                        category=pattern["category"],
                        description=pattern["description"],
                        fix=pattern["fix"],
                        code=line.strip()[:100],
                    )
                )
    return issues


def scan_directory(root: Path, extensions: Optional[list[str]] = None) -> list[Issue]:
    """Recursively scan directory for platform-specific patterns."""
    all_issues = []
    skip_dirs = {
        ".git",
        "node_modules",
        "__pycache__",
        ".venv",
        "venv",
        "target",
        "dist",
        "build",
    }
    default_extensions = {
        ".py",
        ".js",
        ".ts",
        ".sh",
        ".ps1",
        ".bat",
        ".cmd",
        ".yml",
        ".yaml",
    }
    allowed = set(extensions) if extensions else default_extensions
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            file_path = Path(dirpath) / filename
            if file_path.suffix.lower() in allowed:
                all_issues.extend(scan_file(file_path, DETECTION_PATTERNS))
    return all_issues


def format_text_output(issues: list[Issue]) -> str:
    """Format issues as human-readable text."""
    if not issues:
        return "No platform-specific issues detected."
    lines = [f"Found {len(issues)} potential platform-specific issue(s):\n"]
    for i, issue in enumerate(issues, 1):
        lines.append(f"{i}. {issue.file}:{issue.line} - {issue.pattern}")
        lines.append(f"   Category: {issue.category}")
        lines.append(f"   Problem: {issue.description}")
        lines.append(f"   Fix: {issue.fix}")
        lines.append(f"   Code: {issue.code}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect platform-specific code patterns"
    )
    parser.add_argument(
        "--path", required=True, help="Path to scan (file or directory)"
    )
    parser.add_argument(
        "--extensions", nargs="*", help="File extensions to scan (e.g., .py .js)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    target = Path(args.path)
    if not target.exists():
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        return 1

    if target.is_file():
        issues = scan_file(target, DETECTION_PATTERNS)
    else:
        issues = scan_directory(target, args.extensions)

    if args.json:
        output = {
            "issues": [
                {
                    "file": i.file,
                    "line": i.line,
                    "pattern": i.pattern,
                    "category": i.category,
                    "description": i.description,
                    "fix": i.fix,
                    "code": i.code,
                }
                for i in issues
            ],
            "count": len(issues),
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_text_output(issues))
    return 0 if not issues else 2


if __name__ == "__main__":
    sys.exit(main())
