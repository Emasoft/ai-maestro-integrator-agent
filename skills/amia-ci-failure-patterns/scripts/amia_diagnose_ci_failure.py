#!/usr/bin/env python3
"""
Diagnose CI failure logs by identifying common failure patterns.

This script analyzes CI failure logs and identifies likely causes based on
known patterns across platforms (Linux, macOS, Windows) and languages.

Usage:
    python amia_diagnose_ci_failure.py --log-file /path/to/ci.log
    cat ci.log | python amia_diagnose_ci_failure.py --stdin
    python amia_diagnose_ci_failure.py --log-file ci.log --json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass


@dataclass
class Pattern:
    """A CI failure pattern with detection regex and fix suggestion."""

    name: str
    category: str
    regex: str
    description: str
    fix: str


# Known CI failure patterns
PATTERNS = [
    # Cross-platform patterns
    Pattern(
        name="temp_path_not_found",
        category="cross-platform",
        regex=r"(?:FileNotFoundError|ENOENT).*(?:/tmp|\\Temp)",
        description="Hardcoded temp path not found on this platform",
        fix="Use tempfile.gettempdir() (Python) or os.tmpdir() (JS) instead of hardcoded paths",
    ),
    Pattern(
        name="path_separator_issue",
        category="cross-platform",
        regex=r"(?:ENOENT|not found).*(?:\\\\[^\\s]+/|/[^\\s]+\\\\)",
        description="Mixed path separators causing file not found",
        fix="Use path.join() or os.path.join() for cross-platform paths",
    ),
    Pattern(
        name="case_sensitivity",
        category="cross-platform",
        regex=r"(?:ModuleNotFoundError|Cannot find module).*(?:[A-Z][a-z]+|[a-z]+[A-Z])",
        description="Possible case sensitivity issue in import",
        fix="Ensure import statement matches exact file casing",
    ),
    # Exit code patterns
    Pattern(
        name="exit_code_persistence",
        category="exit-code",
        regex=r"(?:exit code|exited with|returned) (?:129|128|1[0-9]{2})",
        description="Unusual exit code may indicate persistent $LASTEXITCODE",
        fix="Add explicit 'exit 0' at end of PowerShell scripts",
    ),
    Pattern(
        name="git_diff_exit",
        category="exit-code",
        regex=r"git diff.*(?:exit|code).*1",
        description="git diff --exit-code returns 1 when differences exist",
        fix="Handle git diff exit code explicitly or remove --exit-code flag",
    ),
    # Syntax patterns
    Pattern(
        name="heredoc_terminator",
        category="syntax",
        regex=r"(?:unexpected end of file|here-document.*delimited by end-of-file)",
        description="Heredoc terminator not at column 0 or has trailing whitespace",
        fix="Ensure EOF/terminator is at column 0 with no trailing spaces",
    ),
    Pattern(
        name="powershell_herestring",
        category="syntax",
        regex=r"(?:Unrecognized token|ExpectedExpression).*@[\"']",
        description="PowerShell here-string closing delimiter not at column 0",
        fix="Ensure \"@ or '@ is at the very start of the line",
    ),
    # Dependency patterns
    Pattern(
        name="module_not_found_python",
        category="dependency",
        regex=r"ModuleNotFoundError: No module named ['\"]([^'\"]+)['\"]",
        description="Python module not found",
        fix="Run 'pip install -e .' or set PYTHONPATH to include source directory",
    ),
    Pattern(
        name="module_not_found_js",
        category="dependency",
        regex=r"Cannot find module ['\"]([^'\"]+)['\"]",
        description="JavaScript module not found",
        fix="Run 'npm ci' to install dependencies from lock file",
    ),
    Pattern(
        name="lock_file_mismatch",
        category="dependency",
        regex=r"(?:npm ERR!.*npm ci|EINTEGRITY|checksum mismatch)",
        description="Lock file out of sync with package.json",
        fix="Run 'npm install' locally and commit updated package-lock.json",
    ),
    # GitHub infrastructure patterns
    Pattern(
        name="label_not_found",
        category="infrastructure",
        regex=r"(?:Label.*not found|Resource not accessible)",
        description="GitHub label doesn't exist",
        fix="Create label via API or UI before workflow uses it",
    ),
    Pattern(
        name="permission_denied",
        category="infrastructure",
        regex=r"(?:permission denied|403|Resource not accessible by integration)",
        description="Insufficient GitHub token permissions",
        fix="Add required permissions to workflow (issues: write, pull-requests: write, etc.)",
    ),
    Pattern(
        name="disk_space",
        category="infrastructure",
        regex=r"(?:No space left on device|ENOSPC)",
        description="CI runner out of disk space",
        fix="Add disk cleanup step or reduce artifact size",
    ),
    Pattern(
        name="memory_limit",
        category="infrastructure",
        regex=r"(?:heap out of memory|ENOMEM|Killed)",
        description="CI runner out of memory",
        fix="Increase NODE_OPTIONS max-old-space-size or optimize memory usage",
    ),
    # Language-specific patterns
    Pattern(
        name="pytest_no_tests",
        category="python",
        regex=r"collected 0 items|no tests ran",
        description="pytest found no tests to run",
        fix="Check testpaths in pyproject.toml and ensure test files match pattern",
    ),
    Pattern(
        name="gcc_not_found",
        category="build",
        regex=r"(?:gcc|cc).*(?:not found|failed|exit code)",
        description="C compiler not found for building native extensions",
        fix="Install build-essential (Linux) or Visual C++ Build Tools (Windows)",
    ),
    Pattern(
        name="esm_commonjs_conflict",
        category="javascript",
        regex=r"(?:require is not defined in ES module|Cannot use import statement outside)",
        description="ESM/CommonJS module type conflict",
        fix="Check package.json 'type' field and use correct file extensions (.mjs/.cjs)",
    ),
    Pattern(
        name="rust_target_missing",
        category="rust",
        regex=r"target.*not found in channel|can't find crate",
        description="Rust compilation target not installed",
        fix="Run 'rustup target add <target>' before build",
    ),
    Pattern(
        name="go_module_not_found",
        category="go",
        regex=r"go:.*module.*not found|unknown revision",
        description="Go module resolution failed",
        fix="Run 'go mod tidy' and commit go.sum",
    ),
]


def analyze_log(log_content: str) -> list[dict]:
    """Analyze log content and return matching patterns."""
    results = []
    for pattern in PATTERNS:
        match = re.search(pattern.regex, log_content, re.IGNORECASE | re.MULTILINE)
        if match:
            context_start = max(0, match.start() - 100)
            context_end = min(len(log_content), match.end() + 100)
            context = log_content[context_start:context_end].strip()
            results.append(
                {
                    "pattern": pattern.name,
                    "category": pattern.category,
                    "description": pattern.description,
                    "fix": pattern.fix,
                    "matched_text": match.group(0)[:200],
                    "context": context[:300],
                }
            )
    return results


def format_text_output(results: list[dict]) -> str:
    """Format results as human-readable text."""
    if not results:
        return "No known CI failure patterns detected in the log."
    lines = [f"Found {len(results)} potential CI failure pattern(s):\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. {r['pattern']} ({r['category']})")
        lines.append(f"   Description: {r['description']}")
        lines.append(f"   Fix: {r['fix']}")
        lines.append(f"   Matched: {r['matched_text'][:80]}...")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Diagnose CI failure logs")
    parser.add_argument("--log-file", help="Path to CI log file")
    parser.add_argument("--stdin", action="store_true", help="Read log from stdin")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.stdin:
        log_content = sys.stdin.read()
    elif args.log_file:
        with open(args.log_file, "r", encoding="utf-8", errors="replace") as f:
            log_content = f.read()
    else:
        parser.print_help()
        return 1

    results = analyze_log(log_content)
    if args.json:
        print(json.dumps({"patterns": results, "count": len(results)}, indent=2))
    else:
        print(format_text_output(results))
    return 0 if results else 2


if __name__ == "__main__":
    sys.exit(main())
