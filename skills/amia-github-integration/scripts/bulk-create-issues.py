#!/usr/bin/env python3
"""Bulk create GitHub issues from a CSV or JSON file.

Usage:
    python scripts/bulk-create-issues.py --repo owner/repo --input issues.csv
    python scripts/bulk-create-issues.py --repo owner/repo --input issues.json --dry-run

CSV format:
    title,body,labels
    "Fix auth bug","Auth fails on login","bug,auth"
    "Add dark mode","Support dark theme","enhancement,ui"

JSON format:
    [
        {"title": "Fix auth bug", "body": "Auth fails on login", "labels": ["bug", "auth"]},
        {"title": "Add dark mode", "body": "Support dark theme", "labels": ["enhancement", "ui"]}
    ]

Exit codes:
    0 - Success (all issues created)
    1 - Invalid parameters (bad arguments or unsupported file format)
    2 - Not found (input file does not exist)
    3 - API error (gh command failed during issue creation)
    4 - Not authenticated (gh auth status fails)
    5 - Partial success (some issues created, some failed)
    6 - Parse error (input file could not be parsed)
"""

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path


def run_gh_command(args: list[str]) -> subprocess.CompletedProcess:
    """Run a gh CLI command and return the completed process."""
    return subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        timeout=30,
    )


def check_auth() -> bool:
    """Check if gh CLI is authenticated. Returns True if authenticated."""
    result = run_gh_command(["auth", "status"])
    return result.returncode == 0


def parse_csv_file(filepath: Path) -> list[dict]:
    """Parse a CSV file into a list of issue dicts."""
    issues = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            issue = {}
            # Normalize keys to lowercase and strip whitespace
            for key, value in row.items():
                issue[key.strip().lower()] = value.strip() if value else ""
            # Convert comma-separated labels string to list
            if "labels" in issue and issue["labels"]:
                issue["labels"] = [l.strip() for l in issue["labels"].split(",") if l.strip()]
            else:
                issue["labels"] = []
            issues.append(issue)
    return issues


def parse_json_file(filepath: Path) -> list[dict]:
    """Parse a JSON file into a list of issue dicts."""
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON file must contain an array of issue objects")
    issues = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("Each element in the JSON array must be an object")
        issue = {}
        for key, value in item.items():
            issue[key.strip().lower()] = value
        # Ensure labels is a list
        if "labels" in issue:
            if isinstance(issue["labels"], str):
                issue["labels"] = [l.strip() for l in issue["labels"].split(",") if l.strip()]
            elif not isinstance(issue["labels"], list):
                issue["labels"] = []
        else:
            issue["labels"] = []
        issues.append(issue)
    return issues


def validate_issue(issue: dict) -> str | None:
    """Validate an issue dict. Returns error string or None if valid."""
    title = issue.get("title", "").strip() if isinstance(issue.get("title"), str) else ""
    if not title:
        return "Missing title"
    return None


def create_issue(repo: str, issue: dict) -> dict:
    """Create a single GitHub issue. Returns result dict."""
    title = issue["title"].strip()
    cmd_args = ["issue", "create", "--repo", repo, "--title", title]

    body = issue.get("body", "").strip() if isinstance(issue.get("body"), str) else ""
    if body:
        cmd_args.extend(["--body", body])

    labels = issue.get("labels", [])
    if labels:
        label_str = ",".join(labels) if isinstance(labels, list) else str(labels)
        if label_str:
            cmd_args.extend(["--label", label_str])

    result = run_gh_command(cmd_args)

    if result.returncode != 0:
        return {
            "title": title,
            "status": "failed",
            "error": result.stderr.strip() or "gh issue create failed",
        }

    # Parse the URL from stdout to extract issue number
    url = result.stdout.strip()
    number = None
    if url:
        # URL format: https://github.com/owner/repo/issues/123
        parts = url.rstrip("/").split("/")
        if parts:
            try:
                number = int(parts[-1])
            except ValueError:
                pass

    entry = {"title": title, "status": "created", "url": url}
    if number is not None:
        entry["number"] = number
    return entry


def main() -> None:
    """Main entry point with argparse CLI."""
    parser = argparse.ArgumentParser(
        description="Bulk create GitHub issues from a CSV or JSON file.",
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Target repository in owner/repo format",
    )
    parser.add_argument(
        "--input",
        required=True,
        dest="input_file",
        help="Path to CSV or JSON file containing issues",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Preview issues without creating them",
    )

    args = parser.parse_args()

    # Validate repo format
    if "/" not in args.repo or len(args.repo.split("/")) != 2:
        print(
            json.dumps({"error": "Invalid repo format. Expected owner/repo"}, indent=2),
            file=sys.stdout,
        )
        sys.exit(1)

    # Check input file exists
    input_path = Path(args.input_file)
    if not input_path.is_file():
        print(
            json.dumps({"error": f"Input file not found: {args.input_file}"}, indent=2),
            file=sys.stdout,
        )
        sys.exit(2)

    # Detect format from extension
    ext = input_path.suffix.lower()
    if ext not in (".csv", ".json"):
        print(
            json.dumps({"error": f"Unsupported file format: {ext}. Use .csv or .json"}, indent=2),
            file=sys.stdout,
        )
        sys.exit(1)

    # Parse input file
    try:
        if ext == ".csv":
            issues = parse_csv_file(input_path)
        else:
            issues = parse_json_file(input_path)
    except (ValueError, json.JSONDecodeError, csv.Error) as e:
        print(
            json.dumps({"error": f"Failed to parse input file: {e}"}, indent=2),
            file=sys.stdout,
        )
        sys.exit(6)

    # Check authentication (skip for dry-run)
    if not args.dry_run:
        if not check_auth():
            print(
                json.dumps({"error": "Not authenticated. Run 'gh auth login' first."}, indent=2),
                file=sys.stdout,
            )
            sys.exit(4)

    # Process issues
    results = []
    created_count = 0
    failed_count = 0

    for issue in issues:
        validation_error = validate_issue(issue)
        if validation_error:
            results.append({
                "title": issue.get("title", ""),
                "status": "failed",
                "error": validation_error,
            })
            failed_count += 1
            continue

        if args.dry_run:
            entry = {
                "title": issue["title"].strip(),
                "status": "dry_run",
                "body_preview": (issue.get("body", "") or "")[:80],
                "labels": issue.get("labels", []),
            }
            results.append(entry)
            created_count += 1
        else:
            entry = create_issue(args.repo, issue)
            results.append(entry)
            if entry["status"] == "created":
                created_count += 1
            else:
                failed_count += 1

    # Build output
    output = {
        "repo": args.repo,
        "input_file": str(args.input_file),
        "dry_run": args.dry_run,
        "total_rows": len(issues),
        "created": created_count,
        "failed": failed_count,
        "results": results,
    }

    print(json.dumps(output, indent=2))

    # Determine exit code
    if failed_count == 0:
        sys.exit(0)
    elif created_count > 0:
        sys.exit(5)  # Partial success
    else:
        sys.exit(3)  # All failed (API errors)


if __name__ == "__main__":
    main()
