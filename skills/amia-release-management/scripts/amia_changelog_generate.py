#!/usr/bin/env python3
"""
amia_changelog_generate.py - Generate changelog from commits.

Generates a structured changelog by comparing commits between two refs,
categorizing them by conventional commit prefixes.

Usage:
    amia_changelog_generate.py --repo owner/repo --from v1.2.2 --to HEAD
    amia_changelog_generate.py --repo owner/repo --from v1.2.2 --to v1.2.3 --output CHANGELOG.md

Output:
    JSON object with categorized commits and markdown changelog to stdout.

Example output:
    {
        "repo": "owner/repo",
        "from_ref": "v1.2.2",
        "to_ref": "HEAD",
        "total_commits": 12,
        "categories": {
            "feat": [{"sha": "abc1234", "message": "add dark mode"}],
            "fix": [{"sha": "def5678", "message": "resolve login crash"}]
        },
        "markdown": "## What's Changed\n\n### Features\n- add dark mode (abc1234)\n..."
    }

Exit codes (standardized):
    0 - Success, changelog generated
    1 - Invalid parameters (missing refs, bad repo format)
    2 - Resource not found (repo or ref not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Not applicable
    6 - Not applicable
"""

import argparse
import json
import os
import re
import subprocess
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


# Conventional commit prefix to human-readable category
CATEGORY_MAP = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "refactor": "Refactoring",
    "perf": "Performance",
    "docs": "Documentation",
    "test": "Tests",
    "chore": "Chores",
    "ci": "CI/CD",
    "build": "Build",
    "style": "Style",
}

COMMIT_PATTERN = re.compile(r"^(\w+)(?:\(.*?\))?!?:\s*(.+)$")


def categorize_commit(message: str) -> tuple[str, str]:
    """Parse a commit message and return (category, description)."""
    match = COMMIT_PATTERN.match(message)
    if match:
        prefix = match.group(1).lower()
        description = match.group(2).strip()
        category = prefix if prefix in CATEGORY_MAP else "other"
        return category, description
    return "other", message.strip()


def generate_changelog(repo: str, from_ref: str, to_ref: str) -> dict[str, Any]:
    """Fetch commits between two refs and generate a categorized changelog."""
    success, output = run_gh_command([
        "api", f"repos/{repo}/compare/{from_ref}...{to_ref}",
        "--jq", "[.commits[] | {sha: .sha[0:7], message: .commit.message | split(\"\\n\")[0]}]",
    ])

    if not success:
        if "not logged in" in output.lower():
            return {"error": True, "message": output, "code": "AUTH_REQUIRED"}
        if "Not Found" in output:
            return {"error": True, "message": f"Repository or ref not found: {output}", "code": "NOT_FOUND"}
        return {"error": True, "message": output, "code": "API_ERROR"}

    try:
        commits = json.loads(output)
    except json.JSONDecodeError:
        return {"error": True, "message": f"Could not parse commit data: {output[:200]}", "code": "API_ERROR"}

    # Categorize commits
    categories: dict[str, list[dict[str, str]]] = {}
    for commit in commits:
        cat, desc = categorize_commit(commit["message"])
        categories.setdefault(cat, []).append({"sha": commit["sha"], "message": desc})

    # Build markdown
    lines = [f"## What's Changed ({from_ref} → {to_ref})", ""]
    for cat_key in ["feat", "fix", "perf", "refactor", "docs", "test", "chore", "ci", "build", "style", "other"]:
        if cat_key not in categories:
            continue
        heading = CATEGORY_MAP.get(cat_key, "Other")
        lines.append(f"### {heading}")
        for item in categories[cat_key]:
            lines.append(f"- {item['message']} ({item['sha']})")
        lines.append("")

    markdown = "\n".join(lines)

    return {
        "repo": repo,
        "from_ref": from_ref,
        "to_ref": to_ref,
        "total_commits": len(commits),
        "categories": categories,
        "markdown": markdown,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate changelog from commits.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--from", dest="from_ref", required=True, help="Starting ref (tag, branch, SHA)")
    parser.add_argument("--to", default="HEAD", help="Ending ref (default: HEAD)")
    parser.add_argument("--output", help="Write markdown changelog to this file")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "amia_changelog_generate", args.output_file)
        sys.exit(1)

    result = generate_changelog(repo=args.repo, from_ref=args.from_ref, to_ref=args.to)
    write_output(result, "amia_changelog_generate", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code == "NOT_FOUND":
            sys.exit(2)
        elif code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result["markdown"])


if __name__ == "__main__":
    main()
