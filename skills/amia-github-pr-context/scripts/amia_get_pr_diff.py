#!/usr/bin/env python3
"""
amia_get_pr_diff.py - Get PR diff with optional filtering.

Usage:
    python3 amia_get_pr_diff.py --pr NUMBER [--repo OWNER/REPO] [--stat] [--files FILE...]

Exit codes (standardized):
    0 - Success, diff text or JSON stats to stdout
    1 - Invalid parameters (bad PR number, missing required args)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import subprocess
import sys
from typing import Optional


def run_gh_command(args: list[str], retry: int = 2) -> tuple[int, str, str]:
    """Run a gh CLI command with retry logic."""
    for attempt in range(retry + 1):
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=60,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if attempt == retry:
                return 2, "", "Command timed out"
        except FileNotFoundError:
            return 2, "", "gh CLI not found. Install with: brew install gh"
    return 2, "", "Max retries exceeded"


def get_pr_diff(pr_number: int, repo: Optional[str]) -> str:
    """Fetch full PR diff."""
    cmd = ["pr", "diff", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])

    returncode, stdout, stderr = run_gh_command(cmd)

    if returncode != 0:
        if "Could not resolve to a PullRequest" in stderr:
            raise ValueError(f"PR #{pr_number} not found")
        if "authentication" in stderr.lower() or "login" in stderr.lower():
            raise ConnectionError(f"Authentication error: {stderr}")
        raise RuntimeError(f"API error: {stderr}")

    return stdout


def filter_diff_by_files(diff_text: str, files: list[str]) -> str:
    """Extract only diffs for specified files."""
    result_lines: list[str] = []
    include_current = False

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            include_current = False
            for f in files:
                if f in line:
                    include_current = True
                    break

        if include_current:
            result_lines.append(line)

    return "\n".join(result_lines)


def calculate_stats(diff_text: str) -> dict:
    """Calculate diff statistics from diff text."""
    files: dict[str, dict] = {}
    current_file: Optional[str] = None
    total_additions = 0
    total_deletions = 0

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1]
                files[current_file] = {"additions": 0, "deletions": 0}
        elif current_file:
            if line.startswith("+") and not line.startswith("+++"):
                files[current_file]["additions"] += 1
                total_additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                files[current_file]["deletions"] += 1
                total_deletions += 1

    file_stats = [
        {
            "filename": filename,
            "additions": stats["additions"],
            "deletions": stats["deletions"],
        }
        for filename, stats in files.items()
    ]

    file_stats.sort(key=lambda x: x["additions"] + x["deletions"], reverse=True)

    return {
        "total_additions": total_additions,
        "total_deletions": total_deletions,
        "files_changed": len(files),
        "files": file_stats,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get PR diff with optional filtering"
    )
    parser.add_argument(
        "--pr", type=int, required=True, help="PR number"
    )
    parser.add_argument(
        "--repo", type=str, help="Repository in OWNER/REPO format"
    )
    parser.add_argument(
        "--stat", action="store_true", help="Show statistics only (JSON)"
    )
    parser.add_argument(
        "--files", nargs="+", help="Filter to specific files"
    )

    args = parser.parse_args()

    if args.pr <= 0:
        print(json.dumps({"error": "PR number must be positive", "code": "INVALID_PARAMS"}))
        return 1  # Invalid parameters

    try:
        diff_text = get_pr_diff(args.pr, args.repo)

        if args.files:
            diff_text = filter_diff_by_files(diff_text, args.files)

        if args.stat:
            stats = calculate_stats(diff_text)
            print(json.dumps(stats, indent=2))
        else:
            print(diff_text)

        return 0  # Success

    except ValueError as e:
        # PR not found
        print(json.dumps({"error": str(e), "code": "RESOURCE_NOT_FOUND"}))
        return 2  # Resource not found
    except ConnectionError as e:
        # Authentication error
        print(json.dumps({"error": str(e), "code": "NOT_AUTHENTICATED"}))
        return 4  # Not authenticated
    except RuntimeError as e:
        # API error
        print(json.dumps({"error": str(e), "code": "API_ERROR"}))
        return 3  # API error


if __name__ == "__main__":
    sys.exit(main())
