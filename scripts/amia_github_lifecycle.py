#!/usr/bin/env python3
"""
amia_github_lifecycle.py - GitHub Issue Lifecycle Automation for Integrator.

Automates the full issue lifecycle: create -> link PR -> move cards -> close.
Designed to save orchestrator tokens by handling GitHub operations via CLI.

Features:
1. Create issues from design specs (with frontmatter extraction)
2. Attach design documents as issue comments (sanitized)
3. Link PRs to issues automatically
4. Move GitHub Projects V2 cards between columns
5. Verify closure requirements (IRON RULE compliance)
6. Bulk operations for multiple issues

Uses gh CLI for authentication (must be logged in via `gh auth login`).

Usage:
    # Create issue from spec
    python amia_github_lifecycle.py create --spec docs/design/specs/auth.md --project 1

    # Attach design document to existing issue
    python amia_github_lifecycle.py attach --issue 234 --document docs/design/specs/auth.md

    # Bulk attach documents to issue
    python amia_github_lifecycle.py attach --issue 234 --documents docs/design/specs/*.md

    # Link PR to issue
    python amia_github_lifecycle.py link-pr --issue 234 --pr 456

    # Move project card
    python amia_github_lifecycle.py move --issue 234 --status "In Progress"

    # Verify closure requirements
    python amia_github_lifecycle.py verify-close --issue 234

    # Validate frontmatter (single file)
    python amia_github_lifecycle.py validate --file docs/design/specs/auth.md

    # Validate frontmatter (directory)
    python amia_github_lifecycle.py validate --dir docs/design/specs --strict

    # Validate with JSON output
    python amia_github_lifecycle.py validate --dir docs/design --json

Dependencies: Python 3.8+, gh CLI (authenticated)

Module Structure:
- amia_github_lifecycle.py (this file): CLI entry point
- amia_github_lifecycle_core.py: Data classes, utilities, constants
- amia_github_lifecycle_issues.py: Issue operations and validation
- amia_github_lifecycle_projects.py: Project and PR operations
"""

import argparse
import json
import sys
from pathlib import Path

# Import core utilities
from amia_github_lifecycle_core import check_gh_auth, validate_frontmatter

# Import issue operations
from amia_github_lifecycle_issues import (
    attach_document_to_issue,
    attach_multiple_documents,
    create_issue_from_spec,
    get_issue_info,
    search_issues,
    verify_closure_requirements,
)

# Import project operations
from amia_github_lifecycle_projects import (
    link_pr_to_issue,
    list_project_statuses,
    move_issue_in_project,
)

__all__ = [
    "main",
]


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GitHub Issue Lifecycle Automation for Integrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create issue from spec
  python amia_github_lifecycle.py create --spec docs/design/specs/auth.md

  # Attach document to issue
  python amia_github_lifecycle.py attach --issue 234 --document docs/design/specs/auth.md

  # Attach multiple documents
  python amia_github_lifecycle.py attach --issue 234 --documents docs/design/specs/auth.md docs/design/plans/impl.md

  # Link PR to issue
  python amia_github_lifecycle.py link-pr --issue 234 --pr 456

  # Move issue in project
  python amia_github_lifecycle.py move --issue 234 --project 1 --status "In Progress"

  # Verify closure requirements
  python amia_github_lifecycle.py verify-close --issue 234

  # Search issues by UUID
  python amia_github_lifecycle.py search --query "PROJ-SPEC-20250108"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Create command
    create_parser = subparsers.add_parser("create", help="Create issue from spec")
    create_parser.add_argument(
        "--spec", "-s", type=Path, required=True, help="Path to spec file"
    )
    create_parser.add_argument(
        "--project", "-p", type=int, help="Project number to add issue to"
    )
    create_parser.add_argument("--labels", "-l", nargs="+", help="Additional labels")
    create_parser.add_argument("--assignees", "-a", nargs="+", help="Assignees")
    create_parser.add_argument(
        "--no-sanitize", action="store_true", help="Don't sanitize INTERNAL content"
    )

    # Attach command
    attach_parser = subparsers.add_parser("attach", help="Attach document(s) to issue")
    attach_parser.add_argument(
        "--issue", "-i", type=int, required=True, help="Issue number"
    )
    attach_parser.add_argument(
        "--document", "-d", type=Path, help="Single document to attach"
    )
    attach_parser.add_argument(
        "--documents", "-D", type=Path, nargs="+", help="Multiple documents to attach"
    )
    attach_parser.add_argument(
        "--no-sanitize", action="store_true", help="Don't sanitize INTERNAL content"
    )
    attach_parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip frontmatter validation (not recommended)",
    )
    attach_parser.add_argument(
        "--strict", action="store_true", help="Treat validation warnings as errors"
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate document frontmatter"
    )
    validate_parser.add_argument(
        "--file", "-f", type=Path, help="Single file to validate"
    )
    validate_parser.add_argument(
        "--files", "-F", type=Path, nargs="+", help="Multiple files to validate"
    )
    validate_parser.add_argument(
        "--dir", "-d", type=Path, help="Directory to validate (all .md files)"
    )
    validate_parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    validate_parser.add_argument(
        "--quiet", "-q", action="store_true", help="Only output errors, not warnings"
    )
    validate_parser.add_argument(
        "--json", action="store_true", help="Output results as JSON"
    )

    # Link PR command
    link_parser = subparsers.add_parser("link-pr", help="Link PR to issue")
    link_parser.add_argument(
        "--issue", "-i", type=int, required=True, help="Issue number"
    )
    link_parser.add_argument("--pr", "-p", type=int, required=True, help="PR number")

    # Move command
    move_parser = subparsers.add_parser("move", help="Move issue in project")
    move_parser.add_argument(
        "--issue", "-i", type=int, required=True, help="Issue number"
    )
    move_parser.add_argument(
        "--project", "-p", type=int, required=True, help="Project number"
    )
    move_parser.add_argument("--status", "-s", required=True, help="Target status")

    # Verify close command
    verify_parser = subparsers.add_parser(
        "verify-close", help="Verify closure requirements"
    )
    verify_parser.add_argument(
        "--issue", "-i", type=int, required=True, help="Issue number"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search issues")
    search_parser.add_argument("--query", "-q", required=True, help="Search query")
    search_parser.add_argument(
        "--limit", "-l", type=int, default=20, help="Max results"
    )

    # List statuses command
    status_parser = subparsers.add_parser(
        "list-statuses", help="List project status options"
    )
    status_parser.add_argument(
        "--project", "-p", type=int, required=True, help="Project number"
    )

    # Info command
    info_parser = subparsers.add_parser("info", help="Get issue info")
    info_parser.add_argument(
        "--issue", "-i", type=int, required=True, help="Issue number"
    )

    args = parser.parse_args()

    # Check authentication
    if not check_gh_auth():
        print("ERROR: gh CLI not authenticated. Run: gh auth login", file=sys.stderr)
        return 1

    # Execute command
    if args.command == "create":
        issue_num = create_issue_from_spec(
            spec_path=args.spec,
            project_number=args.project,
            labels=args.labels,
            assignees=args.assignees,
            sanitize=not args.no_sanitize,
        )
        return 0 if issue_num else 1

    elif args.command == "attach":
        sanitize = not args.no_sanitize
        do_validate = not args.no_validate
        if args.documents:
            count = attach_multiple_documents(
                args.issue,
                args.documents,
                sanitize,
                validate=do_validate,
                strict=args.strict,
            )
            return 0 if count > 0 else 1
        elif args.document:
            success = attach_document_to_issue(
                args.issue,
                args.document,
                sanitize,
                validate=do_validate,
                strict=args.strict,
            )
            return 0 if success else 1
        else:
            print("ERROR: Specify --document or --documents", file=sys.stderr)
            return 1

    elif args.command == "validate":
        # Collect files to validate
        files_to_validate: list[Path] = []
        if args.file:
            files_to_validate.append(args.file)
        if args.files:
            files_to_validate.extend(args.files)
        if args.dir:
            if not args.dir.exists():
                print(f"ERROR: Directory not found: {args.dir}", file=sys.stderr)
                return 1
            files_to_validate.extend(sorted(args.dir.rglob("*.md")))

        if not files_to_validate:
            print("ERROR: Specify --file, --files, or --dir", file=sys.stderr)
            return 1

        # Validate all files
        results: list[dict[str, object]] = []
        total_errors = 0
        total_warnings = 0

        for path in files_to_validate:
            result = validate_frontmatter(path, strict=args.strict)
            results.append(
                {
                    "path": str(path),
                    "valid": result.valid,
                    "errors": result.errors,
                    "warnings": result.warnings,
                }
            )
            total_errors += len(result.errors)
            total_warnings += len(result.warnings)

        # Output results
        if args.json:
            print(
                json.dumps(
                    {
                        "files_checked": len(files_to_validate),
                        "valid_files": sum(1 for r in results if r["valid"]),
                        "invalid_files": sum(1 for r in results if not r["valid"]),
                        "total_errors": total_errors,
                        "total_warnings": total_warnings,
                        "results": results,
                    },
                    indent=2,
                )
            )
        else:
            valid_count = 0
            invalid_count = 0
            for r in results:
                if r["valid"]:
                    valid_count += 1
                    warnings_list = r["warnings"]
                    if (
                        isinstance(warnings_list, list)
                        and warnings_list
                        and not args.quiet
                    ):
                        print(f"⚠ {r['path']}: {len(warnings_list)} warnings")
                        for w in warnings_list:
                            print(f"    - {w}")
                else:
                    invalid_count += 1
                    errors_list = r["errors"]
                    if isinstance(errors_list, list):
                        print(f"✗ {r['path']}: {len(errors_list)} errors")
                        for e in errors_list:
                            print(f"    - {e}")

            print(f"\n{'─' * 50}")
            print(f"Files checked: {len(files_to_validate)}")
            print(f"✓ Valid: {valid_count}")
            print(f"✗ Invalid: {invalid_count}")
            if total_warnings > 0 and not args.quiet:
                print(f"⚠ Warnings: {total_warnings}")

        return 0 if total_errors == 0 else 1

    elif args.command == "link-pr":
        success = link_pr_to_issue(args.issue, args.pr)
        return 0 if success else 1

    elif args.command == "move":
        success = move_issue_in_project(args.issue, args.project, args.status)
        return 0 if success else 1

    elif args.command == "verify-close":
        can_close, _ = verify_closure_requirements(args.issue)
        return 0 if can_close else 1

    elif args.command == "search":
        issues = search_issues(args.query, args.limit)
        if not issues:
            print("No issues found")
            return 0

        print(f"\n{'#':<6} {'State':<8} {'Title':<60}")
        print("-" * 80)
        for issue in issues:
            title = issue.title[:57] + "..." if len(issue.title) > 60 else issue.title
            print(f"#{issue.number:<5} {issue.state:<8} {title}")
        print(f"\nTotal: {len(issues)} issues")
        return 0

    elif args.command == "list-statuses":
        statuses = list_project_statuses(args.project)
        if not statuses:
            print(f"No statuses found for project #{args.project}")
            return 1
        print(f"Available statuses for project #{args.project}:")
        for status in statuses:
            print(f"  - {status}")
        return 0

    elif args.command == "info":
        info = get_issue_info(args.issue)
        if not info:
            print(f"Issue #{args.issue} not found")
            return 1
        print(f"Issue #{info.number}: {info.title}")
        print(f"State: {info.state}")
        print(f"Labels: {', '.join(info.labels) or 'none'}")
        print(f"URL: {info.url}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
