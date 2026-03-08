#!/usr/bin/env python3
"""
amia_rollback.py - Rollback to a previous release version.

Deletes the problematic release and creates a rollback marker release
pointing to the previous version. Print-only by default; use --execute
to actually perform the rollback.

Usage:
    amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "critical bug"
    amia_rollback.py --repo owner/repo --from v1.2.3 --to v1.2.2 --reason "regression" --execute

Output:
    JSON object with rollback plan or execution results to stdout.

Example output:
    {
        "repo": "owner/repo",
        "from_version": "v1.2.3",
        "to_version": "v1.2.2",
        "reason": "critical bug",
        "executed": false,
        "plan": [
            "gh release delete v1.2.3 --yes --repo owner/repo",
            "gh release create v1.2.2-rollback --repo owner/repo --title 'Rollback to v1.2.2' --notes '...'"
        ],
        "manual_steps": [
            "Revert the default branch to the v1.2.2 tag commit",
            "Notify downstream consumers of the rollback",
            "Update deployment pipelines to use v1.2.2"
        ]
    }

Exit codes (standardized):
    0 - Success (plan shown or rollback executed)
    1 - Invalid parameters (missing versions, bad repo format)
    2 - Resource not found (repo or release not found)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Not applicable
    6 - Not applicable
"""

import argparse
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


def rollback_release(
    repo: str,
    from_version: str,
    to_version: str,
    reason: str,
    execute: bool = False,
) -> dict[str, Any]:
    """Plan or execute a release rollback."""
    delete_cmd = f"gh release delete {from_version} --yes --repo {repo}"
    rollback_tag = f"{to_version}-rollback"
    notes = f"Rollback from {from_version} to {to_version}.\n\nReason: {reason}"
    create_cmd = f"gh release create {rollback_tag} --repo {repo} --title 'Rollback to {to_version}' --notes '{notes}'"

    plan = [delete_cmd, create_cmd]
    manual_steps = [
        f"Revert the default branch to the {to_version} tag commit",
        "Notify downstream consumers of the rollback",
        f"Update deployment pipelines to use {to_version}",
    ]

    result: dict[str, Any] = {
        "repo": repo,
        "from_version": from_version,
        "to_version": to_version,
        "reason": reason,
        "executed": execute,
        "plan": plan,
        "manual_steps": manual_steps,
    }

    if not execute:
        return result

    # Execute step 1: delete the problematic release
    success, output = run_gh_command(["release", "delete", from_version, "--yes", "--repo", repo])
    if not success:
        if "not logged in" in output.lower():
            result["error"] = True
            result["message"] = output
            result["code"] = "AUTH_REQUIRED"
            return result
        if "release not found" in output.lower() or "Not Found" in output:
            result["error"] = True
            result["message"] = f"Release {from_version} not found: {output}"
            result["code"] = "NOT_FOUND"
            return result
        result["error"] = True
        result["message"] = f"Failed to delete release: {output}"
        result["code"] = "API_ERROR"
        return result

    result["delete_success"] = True

    # Execute step 2: create rollback marker release
    success, output = run_gh_command([
        "release", "create", rollback_tag,
        "--repo", repo,
        "--title", f"Rollback to {to_version}",
        "--notes", notes,
    ])
    if not success:
        result["error"] = True
        result["message"] = f"Deleted {from_version} but failed to create rollback release: {output}"
        result["code"] = "API_ERROR"
        return result

    result["rollback_url"] = output
    return result


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Rollback to a previous release version.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--from", dest="from_version", required=True, help="Version to rollback from")
    parser.add_argument("--to", dest="to_version", required=True, help="Version to rollback to")
    parser.add_argument("--reason", required=True, help="Reason for the rollback")
    parser.add_argument("--execute", action="store_true", help="Actually execute the rollback (default: print plan only)")
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")

    args = parser.parse_args()

    if "/" not in args.repo:
        write_output({"error": True, "message": "Repository must be in owner/repo format"}, "amia_rollback", args.output_file)
        sys.exit(1)

    result = rollback_release(
        repo=args.repo,
        from_version=args.from_version,
        to_version=args.to_version,
        reason=args.reason,
        execute=args.execute,
    )
    write_output(result, "amia_rollback", args.output_file)

    if result.get("error"):
        code = result.get("code", "")
        if code == "NOT_FOUND":
            sys.exit(2)
        elif code == "AUTH_REQUIRED":
            sys.exit(4)
        else:
            sys.exit(3)


if __name__ == "__main__":
    main()
