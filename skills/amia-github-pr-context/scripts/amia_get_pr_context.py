#!/usr/bin/env python3
"""
amia_get_pr_context.py - Get full PR context including metadata, files, and status.

Usage:
    python3 amia_get_pr_context.py --pr NUMBER [--repo OWNER/REPO] [--verbose] [--max-files N]

Exit codes (standardized):
    0 - Success, JSON output to stdout
    1 - Invalid parameters (bad PR number, missing required args)
    2 - Resource not found (PR does not exist)
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
    5 - Idempotency skip (N/A for this script)
    6 - Not mergeable (N/A for this script)
"""

import argparse
import json
import os
import subprocess
import sys
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
from shared.thresholds import write_output


def run_gh_command(args: list[str], retry: int = 2) -> tuple[int, str, str]:
    """Run a gh CLI command with retry logic."""
    for attempt in range(retry + 1):
        try:
            result = subprocess.run(
                ["gh"] + args,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if attempt == retry:
                return 2, "", "Command timed out"
        except FileNotFoundError:
            return 2, "", "gh CLI not found. Install with: brew install gh"
    return 2, "", "Max retries exceeded"


def get_pr_context(pr_number: int, repo: Optional[str], verbose: bool) -> dict:
    """Fetch comprehensive PR context from GitHub."""
    fields = [
        "number", "title", "body", "state", "url", "isDraft",
        "createdAt", "updatedAt", "closedAt", "mergedAt",
        "author", "assignees", "labels", "milestone",
        "headRefName", "baseRefName", "headRepository", "baseRepository",
        "mergeable", "mergeStateStatus",
        "reviewDecision", "reviews", "reviewRequests",
        "commits", "changedFiles", "additions", "deletions",
        "statusCheckRollup"
    ]

    cmd = ["pr", "view", str(pr_number), "--json", ",".join(fields)]
    if repo:
        cmd.extend(["--repo", repo])

    if verbose:
        print(f"Running: gh {' '.join(cmd)}", file=sys.stderr)

    returncode, stdout, stderr = run_gh_command(cmd)

    if returncode != 0:
        if "Could not resolve to a PullRequest" in stderr:
            raise ValueError(f"PR #{pr_number} not found")
        if "authentication" in stderr.lower() or "login" in stderr.lower():
            raise ConnectionError(f"Authentication error: {stderr}")
        raise RuntimeError(f"API error: {stderr}")

    return json.loads(stdout)


def get_pr_files(pr_number: int, repo: Optional[str]) -> list[dict]:
    """Fetch list of changed files in the PR."""
    cmd = ["pr", "view", str(pr_number), "--json", "files"]
    if repo:
        cmd.extend(["--repo", repo])

    returncode, stdout, _stderr = run_gh_command(cmd)

    if returncode != 0:
        return []

    data = json.loads(stdout)
    return data.get("files", [])


def format_context(pr_data: dict, files: list[dict]) -> dict:
    """Format PR context into a clean output structure."""
    return {
        "number": pr_data.get("number"),
        "title": pr_data.get("title"),
        "body": pr_data.get("body"),
        "state": pr_data.get("state"),
        "url": pr_data.get("url"),
        "isDraft": pr_data.get("isDraft"),
        "createdAt": pr_data.get("createdAt"),
        "updatedAt": pr_data.get("updatedAt"),
        "author": pr_data.get("author"),
        "assignees": pr_data.get("assignees", []),
        "headRefName": pr_data.get("headRefName"),
        "baseRefName": pr_data.get("baseRefName"),
        "headRepository": pr_data.get("headRepository"),
        "baseRepository": pr_data.get("baseRepository"),
        "mergeable": pr_data.get("mergeable"),
        "mergeStateStatus": pr_data.get("mergeStateStatus"),
        "reviewDecision": pr_data.get("reviewDecision"),
        "reviews": pr_data.get("reviews", []),
        "reviewRequests": pr_data.get("reviewRequests", []),
        "labels": pr_data.get("labels", []),
        "milestone": pr_data.get("milestone"),
        "commits": pr_data.get("commits"),
        "changedFiles": pr_data.get("changedFiles"),
        "additions": pr_data.get("additions"),
        "deletions": pr_data.get("deletions"),
        "statusCheckRollup": pr_data.get("statusCheckRollup"),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get full PR context including metadata and files"
    )
    parser.add_argument(
        "--pr", type=int, required=True, help="PR number"
    )
    parser.add_argument(
        "--repo", type=str, help="Repository in OWNER/REPO format"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Enable verbose output"
    )
    parser.add_argument("--output-file", help="Write full JSON output to this file instead of stdout")
    parser.add_argument(
        "--max-files", type=int, default=30,
        help="Maximum number of changed files to include (default: 30)"
    )

    args = parser.parse_args()

    if args.pr <= 0:
        write_output({"error": "PR number must be positive", "code": "INVALID_PARAMS"}, "amia_get_pr_context", args.output_file)
        return 1  # Invalid parameters

    try:
        pr_data = get_pr_context(args.pr, args.repo, args.verbose)
        files = get_pr_files(args.pr, args.repo)

        # Truncate file list if it exceeds --max-files to prevent oversized output
        total_file_count = len(files)
        if total_file_count > args.max_files:
            files = files[: args.max_files]

        output = format_context(pr_data, files)

        if total_file_count > args.max_files:
            output["truncated"] = True
            output["total_files"] = total_file_count
            output["shown_files"] = args.max_files

        write_output(output, "amia_get_pr_context", args.output_file)
        return 0  # Success
    except ValueError as e:
        # PR not found
        write_output({"error": str(e), "code": "RESOURCE_NOT_FOUND"}, "amia_get_pr_context", args.output_file)
        return 2  # Resource not found
    except ConnectionError as e:
        # Authentication error
        write_output({"error": str(e), "code": "NOT_AUTHENTICATED"}, "amia_get_pr_context", args.output_file)
        return 4  # Not authenticated
    except RuntimeError as e:
        # API error
        write_output({"error": str(e), "code": "API_ERROR"}, "amia_get_pr_context", args.output_file)
        return 3  # API error


if __name__ == "__main__":
    sys.exit(main())
