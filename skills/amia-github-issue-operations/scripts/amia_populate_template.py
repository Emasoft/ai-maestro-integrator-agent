#!/usr/bin/env python3
"""
amia_populate_template.py - Populate issue templates and create issues.

Demonstrates the full programmatic-template flow used by the issue-operations
skill: select a template by issue type, inject dynamic system/git context,
substitute variables safely, and (optionally) submit the result as a GitHub
issue via the gh CLI.

All GitHub and git access goes through fixed argument vectors (never a shell
string), so no untrusted value is ever interpolated into a shell command.

Usage:
    amia_populate_template.py --type bug --title "Crash on save" \
        --description "App crashes when saving large files" \
        --repo owner/repo --label bug --submit

    # Print the body only, without creating an issue:
    amia_populate_template.py --type feature --title "Add OAuth" \
        --description "Support Google login"

Output:
    The populated issue body to stdout; when --submit is given, the created
    issue URL is printed on the final line.

Exit codes (standardized):
    0 - Success
    1 - Invalid parameters
    3 - API error (issue creation failed)
"""

import argparse
import platform
import subprocess
import sys
from datetime import datetime
from enum import Enum
from string import Template


class IssueType(Enum):
    BUG = "bug"
    FEATURE = "feature"
    TASK = "task"


TEMPLATES: dict[IssueType, str] = {
    IssueType.BUG: """## Bug Report

**Reporter**: ${reporter}
**Date**: ${date}

### Description
${description}

### Environment
${environment}
""",
    IssueType.FEATURE: """## Feature Request

**Requested by**: ${reporter}
**Date**: ${date}

### Problem
${description}
""",
    IssueType.TASK: """## Task

**Created by**: ${reporter}
**Date**: ${date}

### Summary
${description}
""",
}


def run_git(args: list[str]) -> str:
    """Run a git command with a fixed argv; return stdout or 'unknown'."""
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def get_environment_info() -> str:
    """Collect OS / Python / git context for an issue's Environment section."""
    info = {
        "OS": f"{platform.system()} {platform.release()}",
        "Python": platform.python_version(),
        "Git Branch": run_git(["branch", "--show-current"]) or "detached",
    }
    return "\n".join(f"- **{key}**: {value}" for key, value in info.items())


def populate(issue_type: IssueType, reporter: str, description: str) -> str:
    """Render the template for `issue_type` with the supplied fields."""
    template = Template(TEMPLATES[issue_type])
    return template.safe_substitute(
        reporter=reporter,
        date=datetime.now().strftime("%Y-%m-%d"),
        description=description,
        environment=get_environment_info(),
    )


def submit_issue(repo: str, title: str, body: str, labels: list[str]) -> str:
    """Create an issue via gh CLI and return its URL (raises on failure)."""
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels:
        cmd.extend(["--label", label])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Failed to create issue: {result.stderr.strip()}")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Populate and optionally submit an issue template.")
    parser.add_argument("--type", choices=[t.value for t in IssueType], required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--reporter", default="@me")
    parser.add_argument("--repo", help="Repository in owner/repo format (required with --submit)")
    parser.add_argument("--label", action="append", default=[], help="Label (repeatable)")
    parser.add_argument("--submit", action="store_true", help="Create the issue via gh CLI")
    args = parser.parse_args()

    body = populate(IssueType(args.type), args.reporter, args.description)
    print(body)

    if args.submit:
        if not args.repo:
            print("error: --repo is required with --submit", file=sys.stderr)
            return 1
        try:
            url = submit_issue(args.repo, args.title, body, args.label)
        except RuntimeError as exc:
            print(str(exc), file=sys.stderr)
            return 3
        print(url)

    return 0


if __name__ == "__main__":
    sys.exit(main())
