#!/usr/bin/env python3
"""
amia_github_pr_gate.py - PR approval gates enforcement.

Verifies PRs meet Integrator requirements before merge:
- Linked to approved spec (for feature PRs)
- All tests passing
- Required reviews present
- No blocking comments
- Documentation updated (if applicable)

Uses gh CLI for GitHub operations.

Usage:
    # Check if PR is ready to merge
    python amia_github_pr_gate.py check --pr 123

    # Check specific gates only
    python amia_github_pr_gate.py check --pr 123 --gates spec,tests,reviews

    # Get detailed report
    python amia_github_pr_gate.py report --pr 123

    # Block PR with reason
    python amia_github_pr_gate.py block --pr 123 --reason "Needs approved spec"

    # Approve PR (add approval label)
    python amia_github_pr_gate.py approve --pr 123

Dependencies: Python 3.8+, gh CLI
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

from amia_github_pr_gate_checks import (
    GateResult,
    PRInfo,
    check_draft_gate,
    check_linked_issues_gate,
    check_mergeable_gate,
    check_reviews_gate,
    check_spec_gate,
    check_tests_gate,
)


def run_gh_command(args: list[str]) -> tuple[bool, str]:
    """Run gh CLI command and return (success, output)."""
    try:
        result = subprocess.run(["gh"] + args, capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip()
    except FileNotFoundError:
        return False, "gh CLI not found"


def get_pr_info(pr_number: int, repo: Optional[str] = None) -> Optional[PRInfo]:
    """Get detailed PR information using gh CLI."""
    cmd = [
        "pr",
        "view",
        str(pr_number),
        "--json",
        "number,title,body,state,isDraft,labels,author,reviewRequests,"
        "reviews,statusCheckRollup,mergeable,headRefName,baseRefName",
    ]
    if repo:
        cmd.extend(["--repo", repo])

    success, output = run_gh_command(cmd)
    if not success:
        print(f"ERROR: Failed to get PR info: {output}", file=sys.stderr)
        return None

    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON from gh: {output}", file=sys.stderr)
        return None

    # Parse reviews
    reviews = data.get("reviews", [])
    approvals = sum(1 for r in reviews if r.get("state") == "APPROVED")
    changes_requested = sum(1 for r in reviews if r.get("state") == "CHANGES_REQUESTED")
    reviewers = [
        r.get("author", {}).get("login", "") for r in reviews if r.get("author")
    ]

    # Parse labels
    labels = [label.get("name", "") for label in data.get("labels", [])]

    # Parse status checks
    checks = data.get("statusCheckRollup", [])
    checks_passing = all(
        c.get("conclusion") == "SUCCESS" for c in checks if c.get("conclusion")
    )
    checks_pending = any(
        c.get("status") == "PENDING" or c.get("status") == "IN_PROGRESS" for c in checks
    )

    # Extract linked issues from body
    body = data.get("body", "") or ""
    linked_issues: list[int] = []
    for match in re.finditer(
        r"(?:closes?|fixes?|resolves?)\s+#(\d+)", body, re.IGNORECASE
    ):
        linked_issues.append(int(match.group(1)))

    return PRInfo(
        number=data.get("number", pr_number),
        title=data.get("title", ""),
        body=body,
        state=data.get("state", ""),
        draft=data.get("isDraft", False),
        labels=labels,
        author=data.get("author", {}).get("login", ""),
        reviewers=reviewers,
        approvals=approvals,
        changes_requested=changes_requested,
        linked_issues=linked_issues,
        checks_passing=checks_passing,
        checks_pending=checks_pending,
        mergeable=data.get("mergeable") == "MERGEABLE",
        head_ref=data.get("headRefName", ""),
        base_ref=data.get("baseRefName", ""),
    )


def run_all_gates(
    pr: PRInfo,
    project_root: Path,
    gates: Optional[list[str]] = None,
    min_approvals: int = 1,
) -> list[GateResult]:
    """Run all gate checks."""
    all_gates = {
        "draft": lambda: check_draft_gate(pr),
        "mergeable": lambda: check_mergeable_gate(pr),
        "tests": lambda: check_tests_gate(pr),
        "reviews": lambda: check_reviews_gate(pr, min_approvals),
        "spec": lambda: check_spec_gate(pr, project_root),
        "issues": lambda: check_linked_issues_gate(pr),
    }

    if gates:
        selected = [g.lower() for g in gates]
    else:
        selected = list(all_gates.keys())

    results = []
    for gate_name in selected:
        if gate_name in all_gates:
            results.append(all_gates[gate_name]())

    return results


def add_pr_label(pr_number: int, label: str, repo: Optional[str] = None) -> bool:
    """Add label to PR."""
    cmd = ["pr", "edit", str(pr_number), "--add-label", label]
    if repo:
        cmd.extend(["--repo", repo])
    success, _ = run_gh_command(cmd)
    return success


def add_pr_comment(pr_number: int, body: str, repo: Optional[str] = None) -> bool:
    """Add comment to PR."""
    cmd = ["pr", "comment", str(pr_number), "--body", body]
    if repo:
        cmd.extend(["--repo", repo])
    success, _ = run_gh_command(cmd)
    return success


def generate_report(pr: PRInfo, results: list[GateResult]) -> str:
    """Generate markdown report of gate checks."""
    lines = [
        f"## PR Gate Check: #{pr.number}",
        "",
        f"**Title**: {pr.title}",
        f"**Author**: @{pr.author}",
        f"**Branch**: `{pr.head_ref}` -> `{pr.base_ref}`",
        "",
        "### Gate Results",
        "",
        "| Gate | Status | Message |",
        "|------|--------|---------|",
    ]

    all_required_passed = True
    for result in results:
        status = (
            "PASS" if result.passed else ("WARN" if not result.required else "FAIL")
        )
        req = " (required)" if result.required else ""
        lines.append(f"| {result.name}{req} | {status} | {result.message} |")

        if result.required and not result.passed:
            all_required_passed = False

    lines.append("")

    # Add details for failed gates
    failed_gates = [r for r in results if not r.passed]
    if failed_gates:
        lines.append("### Issues to Address")
        lines.append("")
        for result in failed_gates:
            lines.append(f"**{result.name}**: {result.message}")
            for detail in result.details:
                lines.append(f"  - {detail}")
            lines.append("")

    # Summary
    lines.append("### Summary")
    lines.append("")
    if all_required_passed:
        lines.append("**All required gates passed** - PR is ready to merge")
    else:
        lines.append("**Required gates failed** - Address issues before merge")

    return "\n".join(lines)


# =============================================================================
# CLI Commands
# =============================================================================


def cmd_check(args: argparse.Namespace) -> int:
    """Handle check command."""
    pr = get_pr_info(args.pr, args.repo)
    if not pr:
        return 1

    gates = args.gates.split(",") if args.gates else None
    results = run_all_gates(pr, args.project_root, gates, args.min_approvals)

    # Print results
    all_required_passed = True
    print(f"\nPR #{pr.number}: {pr.title}\n")

    for result in results:
        status = (
            "PASS" if result.passed else ("WARN" if not result.required else "FAIL")
        )
        req = " [required]" if result.required else ""
        print(f"  [{status}] {result.name}{req}: {result.message}")

        if result.required and not result.passed:
            all_required_passed = False

    print()
    if all_required_passed:
        print("All required gates passed")
        return 0
    else:
        print("Some required gates failed")
        return 1


def cmd_report(args: argparse.Namespace) -> int:
    """Handle report command."""
    pr = get_pr_info(args.pr, args.repo)
    if not pr:
        return 1

    gates = args.gates.split(",") if args.gates else None
    results = run_all_gates(pr, args.project_root, gates, args.min_approvals)

    report = generate_report(pr, results)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report saved: {args.output}")
    elif args.comment:
        if add_pr_comment(args.pr, report, args.repo):
            print(f"Report posted as comment on PR #{args.pr}")
        else:
            print("Failed to post comment", file=sys.stderr)
            return 1
    else:
        print(report)

    return 0


def cmd_block(args: argparse.Namespace) -> int:
    """Handle block command - add blocking label and comment."""
    comment = (
        f"**PR Blocked**\n\nReason: {args.reason}\n\n*Added by Integrator gate checker*"
    )

    success = True
    if add_pr_label(args.pr, "blocked", args.repo):
        print(f"Added 'blocked' label to PR #{args.pr}")
    else:
        print("Failed to add label", file=sys.stderr)
        success = False

    if add_pr_comment(args.pr, comment, args.repo):
        print(f"Added blocking comment to PR #{args.pr}")
    else:
        print("Failed to add comment", file=sys.stderr)
        success = False

    return 0 if success else 1


def cmd_approve(args: argparse.Namespace) -> int:
    """Handle approve command - add approval label."""
    if add_pr_label(args.pr, "gates-passed", args.repo):
        print(f"Added 'gates-passed' label to PR #{args.pr}")
        return 0
    else:
        print("Failed to add label", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PR approval gates enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Gates:
  draft      - PR is not a draft
  mergeable  - No merge conflicts
  tests      - All CI checks passing
  reviews    - Required approvals present
  spec       - Feature PRs linked to approved spec
  issues     - Linked to issues (recommended)

Examples:
  python amia_github_pr_gate.py check --pr 123
  python amia_github_pr_gate.py check --pr 123 --gates tests,reviews
  python amia_github_pr_gate.py report --pr 123
  python amia_github_pr_gate.py report --pr 123 --comment
  python amia_github_pr_gate.py block --pr 123 --reason "Needs spec"
        """,
    )

    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--repo", "-r", help="GitHub repo (owner/repo)")

    subparsers = parser.add_subparsers(dest="command")

    # check command
    check_parser = subparsers.add_parser("check", help="Check PR gates")
    check_parser.add_argument("--pr", "-p", type=int, required=True, help="PR number")
    check_parser.add_argument("--gates", "-g", help="Comma-separated gates to check")
    check_parser.add_argument("--min-approvals", type=int, default=1)

    # report command
    report_parser = subparsers.add_parser("report", help="Generate gate report")
    report_parser.add_argument("--pr", "-p", type=int, required=True)
    report_parser.add_argument("--gates", "-g", help="Comma-separated gates")
    report_parser.add_argument("--min-approvals", type=int, default=1)
    report_parser.add_argument("--output", "-o", help="Save to file")
    report_parser.add_argument(
        "--comment", "-c", action="store_true", help="Post as PR comment"
    )

    # block command
    block_parser = subparsers.add_parser("block", help="Block PR")
    block_parser.add_argument("--pr", "-p", type=int, required=True)
    block_parser.add_argument("--reason", "-R", required=True, help="Blocking reason")

    # approve command
    approve_parser = subparsers.add_parser("approve", help="Mark PR as gates-passed")
    approve_parser.add_argument("--pr", "-p", type=int, required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    commands = {
        "check": cmd_check,
        "report": cmd_report,
        "block": cmd_block,
        "approve": cmd_approve,
    }

    return commands[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
