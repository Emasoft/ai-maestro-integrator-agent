#!/usr/bin/env python3
"""
amia_ensure_label.py - Ensure a GitHub label exists, creating it if needed.

Checks whether a label is present in a repository and, when it is absent and
auto-creation is enabled, creates it with a sensible default color and
description chosen by matching the label name against a built-in config table.

All GitHub access goes through the `gh` CLI with a fixed argument vector
(never a shell string), so no untrusted value is ever interpolated into a
shell command.

Usage:
    amia_ensure_label.py --repo owner/repo --label "priority:high"
    amia_ensure_label.py --repo owner/repo --label "needs-triage" --no-create

Output:
    JSON to stdout: {"label": ..., "existed": bool, "created": bool}

Exit codes (standardized):
    0 - Success (label exists or was created)
    1 - Invalid parameters
    2 - Label absent and creation disabled / creation failed
    3 - API error (network, rate limit, timeout)
    4 - Not authenticated (gh CLI not logged in)
"""

import argparse
import json
import subprocess
import sys

# Default color + description for labels, keyed by exact name.
DEFAULT_LABEL_CONFIGS: dict[str, dict[str, str]] = {
    "priority:critical": {"color": "b60205", "description": "Critical priority"},
    "priority:high": {"color": "d93f0b", "description": "High priority"},
    "priority:normal": {"color": "fbca04", "description": "Normal priority"},
    "priority:low": {"color": "0e8a16", "description": "Low priority"},
    "bug": {"color": "d73a4a", "description": "Something isn't working"},
    "feature": {"color": "5319e7", "description": "New functionality"},
    "task": {"color": "0075ca", "description": "General task"},
    "docs": {"color": "0075ca", "description": "Documentation"},
    "status:backlog": {"color": "d4c5f9", "description": "In backlog, needs assessment"},
    "status:todo": {"color": "c2e0c6", "description": "Ready to be worked on"},
    "status:in-progress": {"color": "fbca04", "description": "Work in progress"},
    "status:ai-review": {"color": "1d76db", "description": "Ready for AI agent review"},
    "status:human-review": {"color": "0e8a16", "description": "Awaiting human review"},
    "status:merge-release": {"color": "0e8a16", "description": "Approved, ready to merge"},
    "status:blocked": {"color": "d73a4a", "description": "Blocked by dependency"},
    "status:done": {"color": "006b75", "description": "Completed"},
}


def run_gh(args: list[str]) -> tuple[bool, str]:
    """Execute a gh CLI command with a fixed argv and return (ok, output)."""
    result = subprocess.run(["gh"] + args, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout.strip()
    return False, result.stderr.strip()


def get_label_config(label_name: str) -> dict[str, str]:
    """Return color/description for a label, falling back to a gray default."""
    if label_name in DEFAULT_LABEL_CONFIGS:
        return DEFAULT_LABEL_CONFIGS[label_name]
    return {"color": "cfd3d7", "description": f"Label: {label_name}"}


def label_exists(repo: str, label: str) -> bool:
    """Return True if `label` is present in the repository."""
    ok, out = run_gh(["label", "list", "--repo", repo, "--json", "name"])
    if not ok or not out:
        return False
    return any(entry["name"] == label for entry in json.loads(out))


def ensure_label(repo: str, label: str, auto_create: bool = True) -> dict:
    """Ensure a label exists; create it with defaults when missing."""
    if label_exists(repo, label):
        return {"label": label, "existed": True, "created": False}
    if not auto_create:
        return {"label": label, "existed": False, "created": False}

    config = get_label_config(label)
    ok, _ = run_gh(
        [
            "label", "create", label,
            "--repo", repo,
            "--color", config["color"],
            "--description", config["description"],
        ]
    )
    return {"label": label, "existed": False, "created": ok}


def main() -> int:
    parser = argparse.ArgumentParser(description="Ensure a GitHub label exists.")
    parser.add_argument("--repo", required=True, help="Repository in owner/repo format")
    parser.add_argument("--label", required=True, help="Label name to ensure")
    parser.add_argument(
        "--no-create",
        dest="auto_create",
        action="store_false",
        help="Do not create the label if it is missing",
    )
    args = parser.parse_args()

    result = ensure_label(args.repo, args.label, args.auto_create)
    print(json.dumps(result, indent=2))
    if result["existed"] or result["created"]:
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
