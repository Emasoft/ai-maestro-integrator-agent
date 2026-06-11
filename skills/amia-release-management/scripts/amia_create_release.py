#!/usr/bin/env python3
"""
amia_create_release.py - Create a GitHub release with tag.

Creates a new GitHub release using the gh CLI, tagging the current HEAD
with the specified version and attaching release notes.

Creating a release enters the release pipeline (complete -> publish), a
NON-EXEMPT Tier-2 governance action. This script REFUSES to run until it can
prove a recorded MANAGER approval. Pass --approval-trdd pointing at the
approving TRDD (whose "## Approval log" records an APPROVED release entry), or
--solo-user-approval "<reason>" when the project owner is acting as MANAGER on a
solo / autonomous project. See ~/.claude/rules/trdd-approval-tiers.md (Tier 2).

Usage:
    amia_create_release.py --repo owner/repo --version 1.2.3 --notes notes.md \
        --approval-trdd design/tasks/TRDD-<id>-...md
    amia_create_release.py --repo owner/repo --version 1.2.3 --notes notes.md \
        --solo-user-approval "owner approves the 1.2.3 patch release"
    amia_create_release.py --repo owner/repo --version 1.2.3 --notes notes.md \
        --approval-trdd <trdd> --prerelease
    amia_create_release.py --repo owner/repo --version 1.2.3 --notes notes.md \
        --approval-trdd <trdd> --draft

Output:
    JSON object with release details (incl. the approval evidence) to stdout.

Example output:
    {
        "repo": "owner/repo",
        "version": "1.2.3",
        "tag": "v1.2.3",
        "url": "https://github.com/owner/repo/releases/tag/v1.2.3",
        "prerelease": false,
        "draft": false
    }

Exit codes (standardized):
    0 - Success, release created
    1 - Invalid parameters (missing version, bad repo format)
    2 - Resource not found (repo not found, notes file missing)
    3 - API error (network, rate limit, tag already exists)
    4 - Not authenticated (gh CLI not logged in)
    5 - Not applicable
    6 - Not applicable
    7 - Governance block (no recorded MANAGER approval for the release)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.release_governance import governance_block_message, verify_release_approval
from shared.thresholds import write_output


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command and return success status and output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0, result.stdout.strip() if result.returncode == 0 else result.stderr.strip()


def create_release(
    repo: str,
    version: str,
    notes_file: str,
    prerelease: bool = False,
    draft: bool = False,
) -> dict[str, Any]:
    """Create a GitHub release with the specified parameters."""
    tag = f"v{version}" if not version.startswith("v") else version

    # Verify notes file exists
    if not Path(notes_file).is_file():
        return {"error": True, "message": f"Notes file not found: {notes_file}", "code": "NOT_FOUND"}

    cmd = [
        "release", "create", tag,
        "--repo", repo,
        "--title", tag,
        "--notes-file", notes_file,
    ]

    if prerelease:
        cmd.append("--prerelease")
    if draft:
        cmd.append("--draft")

    success, output = run_gh_command(cmd)

    if not success:
        if "not logged in" in output.lower():
            return {"error": True, "message": output, "code": "AUTH_REQUIRED"}
        if "already exists" in output.lower():
            return {"error": True, "message": f"Tag {tag} already exists: {output}", "code": "TAG_EXISTS"}
        if "Could not resolve" in output:
            return {"error": True, "message": output, "code": "REPO_NOT_FOUND"}
        return {"error": True, "message": output, "code": "CREATE_FAILED"}

    return {
        "repo": repo,
        "version": version,
        "tag": tag,
        "url": output,
        "prerelease": prerelease,
        "draft": draft,
    }


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Create a GitHub release with tag.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--version", required=True, help="Release version (e.g. 1.2.3)")
    parser.add_argument("--notes", required=True, help="Path to release notes markdown file")
    parser.add_argument("--prerelease", action="store_true", help="Mark as pre-release")
    parser.add_argument("--draft", action="store_true", help="Create as draft release")
    parser.add_argument(
        "--approval-trdd",
        help="Path to the approving TRDD whose '## Approval log' records the MANAGER release approval",
    )
    parser.add_argument(
        "--solo-user-approval",
        help="Project owner acting as MANAGER on a solo/autonomous project: one-line rationale (logged)",
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "amia_create_release", args.output_file)
        sys.exit(1)

    # Tier-2 governance gate: creating a release is a NON-EXEMPT release-pipeline
    # action. Refuse to touch the public release surface without proof of a
    # recorded MANAGER approval (or an explicit solo USER-as-MANAGER assertion).
    if args.approval_trdd:
        verdict = verify_release_approval(args.approval_trdd)
        if not verdict.approved:
            write_output(
                {
                    "error": True,
                    "message": verdict.detail + "\n\n" + governance_block_message(args.repo, args.version),
                    "code": "GOVERNANCE_BLOCK",
                },
                "amia_create_release",
                args.output_file,
            )
            sys.exit(7)
        approval_evidence = f"MANAGER approval (TRDD): {verdict.evidence_line}"
    elif args.solo_user_approval and args.solo_user_approval.strip():
        approval_evidence = f"solo USER-as-MANAGER approval: {args.solo_user_approval.strip()}"
    else:
        write_output(
            {"error": True, "message": governance_block_message(args.repo, args.version), "code": "GOVERNANCE_BLOCK"},
            "amia_create_release",
            args.output_file,
        )
        sys.exit(7)

    result = create_release(
        repo=args.repo,
        version=args.version,
        notes_file=args.notes,
        prerelease=args.prerelease,
        draft=args.draft,
    )
    if not result.get("error"):
        result["approval"] = approval_evidence
    write_output(result, "amia_create_release", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code in ("NOT_FOUND", "REPO_NOT_FOUND"):
            sys.exit(2)
        elif code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
