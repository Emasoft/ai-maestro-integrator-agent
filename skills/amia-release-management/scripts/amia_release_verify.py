#!/usr/bin/env python3
"""
amia_release_verify.py - Pre-release verification checklist.

Verifies that a repository is ready for release by checking CI status,
open bugs, changelog existence, and version consistency.

Usage:
    amia_release_verify.py --repo owner/repo --version 1.2.3
    amia_release_verify.py --repo owner/repo --version 1.2.3 --strict

Output:
    JSON object with verification checklist results to stdout.

Example output:
    {
        "repo": "owner/repo",
        "version": "1.2.3",
        "all_passed": true,
        "gates": [
            {"name": "ci_status", "passed": true, "detail": "Last CI run succeeded"},
            {"name": "open_bugs", "passed": true, "detail": "0 open bugs"},
            {"name": "changelog", "passed": true, "detail": "CHANGELOG.md exists"},
            {"name": "version_consistency", "passed": true, "detail": "Version 1.2.3 found in plugin.json"}
        ]
    }

Exit codes (standardized):
    0 - Success, all gates passed
    1 - Invalid parameters (missing version, bad repo format)
    2 - Resource not found (repo not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Verification failed (one or more gates failed)
    6 - Not applicable
"""

import argparse
import json
import os
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


def check_ci_status(repo: str) -> dict[str, Any]:
    """Check if the latest CI run on the default branch succeeded."""
    success, output = run_gh_command([
        "api", f"repos/{repo}/actions/runs",
        "--jq", ".workflow_runs[0] | {status, conclusion, name}",
    ])
    if not success:
        return {"name": "ci_status", "passed": False, "detail": f"Could not fetch CI status: {output}"}

    try:
        run_info = json.loads(output)
        passed = run_info.get("conclusion") == "success"
        detail = f"Latest run '{run_info.get('name', 'unknown')}': {run_info.get('conclusion', 'unknown')}"
        return {"name": "ci_status", "passed": passed, "detail": detail}
    except (json.JSONDecodeError, KeyError):
        return {"name": "ci_status", "passed": False, "detail": f"Unexpected CI response: {output[:200]}"}


def check_open_bugs(repo: str) -> dict[str, Any]:
    """Check for open issues labeled 'bug'."""
    success, output = run_gh_command([
        "issue", "list", "--repo", repo, "--label", "bug", "--state", "open", "--json", "number",
    ])
    if not success:
        return {"name": "open_bugs", "passed": False, "detail": f"Could not fetch bugs: {output}"}

    try:
        bugs = json.loads(output)
        count = len(bugs)
        passed = count == 0
        detail = f"{count} open bug(s)" + ("" if passed else " — consider fixing before release")
        return {"name": "open_bugs", "passed": passed, "detail": detail}
    except json.JSONDecodeError:
        return {"name": "open_bugs", "passed": False, "detail": f"Unexpected response: {output[:200]}"}


def check_changelog(repo: str) -> dict[str, Any]:
    """Check if CHANGELOG.md exists in the repository root."""
    success, output = run_gh_command([
        "api", f"repos/{repo}/contents/CHANGELOG.md", "--jq", ".name",
    ])
    if success and output:
        return {"name": "changelog", "passed": True, "detail": "CHANGELOG.md exists"}
    return {"name": "changelog", "passed": False, "detail": "CHANGELOG.md not found in repository root"}


def check_version_consistency(repo: str, version: str) -> dict[str, Any]:
    """Check if the target version appears in known version files."""
    version_files = ["plugin.json", "package.json", "pyproject.toml", "setup.cfg"]
    found_in: list[str] = []

    for filename in version_files:
        success, output = run_gh_command([
            "api", f"repos/{repo}/contents/{filename}", "--jq", ".content",
        ])
        if success and version in output:
            found_in.append(filename)

    if found_in:
        return {"name": "version_consistency", "passed": True, "detail": f"Version {version} found in: {', '.join(found_in)}"}
    return {"name": "version_consistency", "passed": False, "detail": f"Version {version} not found in any known version file"}


def verify_release(repo: str, version: str) -> dict[str, Any]:
    """Run all pre-release verification gates."""
    gates = [
        check_ci_status(repo),
        check_open_bugs(repo),
        check_changelog(repo),
        check_version_consistency(repo, version),
    ]
    all_passed = all(g["passed"] for g in gates)
    return {
        "repo": repo,
        "version": version,
        "all_passed": all_passed,
        "gates": gates,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Pre-release verification checklist.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--version", required=True, help="Target release version (e.g. 1.2.3)")
    parser.add_argument("--strict", action="store_true", help="Exit with code 5 if any gate fails")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "amia_release_verify", args.output_file)
        sys.exit(1)

    result = verify_release(repo=args.repo, version=args.version)
    write_output(result, "amia_release_verify", args.output_file)

    if result.get("all_passed"):
        sys.exit(0)
    elif args.strict:
        sys.exit(5)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
