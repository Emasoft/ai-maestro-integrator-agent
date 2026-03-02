#!/usr/bin/env python3
"""
amia_get_pr_files.py - Get list of changed files in a PR.

Usage:
    python3 amia_get_pr_files.py --pr NUMBER [--repo OWNER/REPO] [--include-patch]

Exit codes (standardized):
    0 - Success, JSON array output to stdout
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
                timeout=30,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            if attempt == retry:
                return 2, "", "Command timed out"
        except FileNotFoundError:
            return 2, "", "gh CLI not found. Install with: brew install gh"
    return 2, "", "Max retries exceeded"


def get_pr_files_basic(pr_number: int, repo: Optional[str]) -> list[dict]:
    """Fetch basic file list from PR."""
    cmd = ["pr", "view", str(pr_number), "--json", "files"]
    if repo:
        cmd.extend(["--repo", repo])

    returncode, stdout, stderr = run_gh_command(cmd)

    if returncode != 0:
        if "Could not resolve to a PullRequest" in stderr:
            raise ValueError(f"PR #{pr_number} not found")
        if "authentication" in stderr.lower() or "login" in stderr.lower():
            raise ConnectionError(f"Authentication error: {stderr}")
        raise RuntimeError(f"API error: {stderr}")

    data = json.loads(stdout)
    return data.get("files", [])


def get_pr_diff(pr_number: int, repo: Optional[str]) -> str:
    """Fetch PR diff for patch extraction."""
    cmd = ["pr", "diff", str(pr_number)]
    if repo:
        cmd.extend(["--repo", repo])

    returncode, stdout, _stderr = run_gh_command(cmd)

    if returncode != 0:
        return ""

    return stdout


def extract_file_patches(diff_text: str) -> dict[str, str]:
    """Extract per-file patches from full diff."""
    patches: dict[str, str] = {}
    current_file: Optional[str] = None
    current_patch: list[str] = []

    for line in diff_text.split("\n"):
        if line.startswith("diff --git"):
            if current_file and current_patch:
                patches[current_file] = "\n".join(current_patch)
            parts = line.split(" b/")
            if len(parts) > 1:
                current_file = parts[1]
            current_patch = [line]
        elif current_file:
            current_patch.append(line)

    if current_file and current_patch:
        patches[current_file] = "\n".join(current_patch)

    return patches


def format_files(files: list[dict], patches: Optional[dict[str, str]]) -> list[dict]:
    """Format file list with optional patches."""
    result = []

    for f in files:
        entry = {
            "filename": f.get("path", f.get("filename", "")),
            "status": f.get("status", "modified"),
            "additions": f.get("additions", 0),
            "deletions": f.get("deletions", 0),
        }

        if f.get("previous_filename"):
            entry["previous_filename"] = f["previous_filename"]

        if patches and entry["filename"] in patches:
            entry["patch"] = patches[entry["filename"]]

        result.append(entry)

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Get list of changed files in a PR"
    )
    parser.add_argument(
        "--pr", type=int, required=True, help="PR number"
    )
    parser.add_argument(
        "--repo", type=str, help="Repository in OWNER/REPO format"
    )
    parser.add_argument(
        "--include-patch", action="store_true", help="Include patch for each file"
    )

    args = parser.parse_args()

    if args.pr <= 0:
        print(json.dumps({"error": "PR number must be positive", "code": "INVALID_PARAMS"}))
        return 1  # Invalid parameters

    try:
        files = get_pr_files_basic(args.pr, args.repo)

        patches = None
        if args.include_patch:
            diff_text = get_pr_diff(args.pr, args.repo)
            if diff_text:
                patches = extract_file_patches(diff_text)

        output = format_files(files, patches)
        print(json.dumps(output, indent=2))
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
